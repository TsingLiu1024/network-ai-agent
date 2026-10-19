"""Bounded two-inference pipeline; no command execution in diagnosis."""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from agents.core.result import AgentResult
from agents.core.supervisor_agent import SupervisorAgent
from agents.log_agent import LogAgent
from agents.network_agent import NetworkAgent
from agents.rag_agent import RAGAgent
from agents.repair_agent import RepairAgent
from config.settings import settings
from llm import get_llm

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(self, config=None, llm=None, retriever=None):
        self.config = config or settings
        llm = llm or get_llm(self.config)
        self.agents = {
            "network": NetworkAgent(self.config),
            "log": LogAgent(self.config),
            "rag": RAGAgent(self.config, retriever),
            "repair": RepairAgent(self.config, llm),
        }
        self.supervisor = SupervisorAgent(self.config, llm)

    def prepare(self):
        self.agents["rag"].prepare()

    def get_agent(self, name):
        return self.agents.get(name)

    @staticmethod
    def _failed(name, code="stage_failed"):
        return AgentResult(
            name, False, message="Stage unavailable", metadata={"error_code": code}
        ).to_dict()

    @staticmethod
    def _safe(name, function, *args, **kwargs):
        try:
            return function(*args, **kwargs).to_dict()
        except Exception:
            # No exception strings or traceback: upstream libraries can include credentials.
            logger.warning("Diagnostic stage failed: %s", name)
            return AgentManager._failed(name)

    def run(self, query):
        started = time.monotonic()
        deadline = started + self.config.DIAGNOSIS_TIMEOUT

        def remaining():
            return max(0, deadline - time.monotonic())

        results = {}
        collect = self.config.COLLECT_LOCAL_EVIDENCE and (
            self.config.MODEL_PROVIDER not in {"deepseek", "openai"}
            or self.config.ALLOW_CLOUD_LOG_UPLOAD
        )
        if collect:
            pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="evidence")
            jobs = {
                name: pool.submit(self._safe, name, self.agents[name].run, query)
                for name in ("network", "log")
            }
            try:
                for name, job in jobs.items():
                    try:
                        results[name] = job.result(timeout=remaining())
                    except TimeoutError:
                        results[name] = self._failed(name, "deadline")
            finally:
                # Keep the parent API capacity occupied until bounded collectors exit.
                pool.shutdown(wait=True, cancel_futures=True)
        else:
            for name in ("network", "log"):
                results[name] = AgentResult(
                    name,
                    False,
                    message="Local server evidence disabled",
                    metadata={"status": "skipped"},
                ).to_dict()
        results["rag"] = (
            self._safe("rag", self.agents["rag"].run, query)
            if remaining()
            else self._failed("rag", "deadline")
        )
        context = json.dumps(
            {"question": query, "evidence": results}, ensure_ascii=False, default=str
        )
        results["repair"] = (
            self._safe("repair", self.agents["repair"].run, context, timeout=remaining())
            if remaining()
            else self._failed("repair", "deadline")
        )
        results["supervisor"] = (
            self._safe(
                "supervisor", self.supervisor.run, query, results.copy(), timeout=remaining()
            )
            if remaining()
            else self._failed("supervisor", "deadline")
        )
        if not remaining():
            results["supervisor"] = self._failed("supervisor", "deadline")
        required_ok = all(results[n]["success"] for n in ("repair", "supervisor"))
        observed = results["network"]["success"]
        optional_failed = any(
            not r["success"] and r.get("metadata", {}).get("status") != "skipped"
            for r in results.values()
        )
        status = (
            "failed"
            if not results["supervisor"]["success"]
            else "success"
            if required_ok and observed and not optional_failed
            else "partial"
        )
        if self.config.MODEL_PROVIDER == "demo" and required_ok:
            status = "demo"
        return {
            "status": status,
            "evidence_scope": "api_server",
            "mode": self.config.MODEL_PROVIDER,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "execution_enabled": False,
            "stages": results,
        }
