import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from agents.core.manager import AgentManager
from config.settings import Settings
from llm.base import LLMError


class Model:
    def __init__(self):
        self.prompts = []

    def chat(self, prompt, timeout=None):
        self.prompts.append(prompt)
        if "REPAIR_PLAN" in prompt:
            return json.dumps({"reason": "需要更多证据", "steps": ["检查DNS"], "commands": []})
        return "证据不足：请先验证 DNS。"


def config(**kwargs):
    return Settings(_env_file=None, ENABLE_RAG=False, **kwargs)


def test_pipeline_uses_at_most_two_calls_and_marks_missing_evidence():
    model = Model()
    manager = AgentManager(config=config(), llm=model)
    result = manager.run("DNS failure")
    assert len(model.prompts) == 2
    assert result["status"] == "partial"
    assert result["evidence_scope"] == "api_server"
    assert result["stages"]["network"]["metadata"]["status"] == "skipped"


def test_model_outage_marks_whole_pipeline_failed():
    class Offline:
        def chat(self, prompt, timeout=None):
            raise LLMError("provider_unavailable", "Model unavailable")

    result = AgentManager(config=config(), llm=Offline()).run("DNS failure")
    assert result["status"] == "failed"
    assert result["stages"]["repair"]["success"] is False


def test_deadline_prevents_starting_second_model_call():
    class Slow(Model):
        def chat(self, prompt, timeout=None):
            time.sleep(0.02)
            return super().chat(prompt, timeout)

    model = Slow()
    result = AgentManager(config=config(DIAGNOSIS_TIMEOUT=0.01), llm=model).run("DNS failure")
    assert len(model.prompts) == 1
    assert not result["stages"]["supervisor"]["success"]
    assert result["stages"]["supervisor"]["metadata"]["error_code"] == "deadline"


def test_prompt_budget_bounds_whole_serialized_evidence():
    model = Model()
    manager = AgentManager(config=config(MAX_CONTEXT_LENGTH=1000), llm=model)
    manager.run("DNS " * 500)
    assert len(model.prompts) == 2
    assert all(len(prompt) <= 1000 for prompt in model.prompts)


def test_cloud_evidence_requires_explicit_upload_permission(monkeypatch):
    def forbidden(*a, **k):
        raise AssertionError("Local evidence collected without permission")

    monkeypatch.setattr("subprocess.run", forbidden)
    result = AgentManager(
        config=config(MODEL_PROVIDER="deepseek", COLLECT_LOCAL_EVIDENCE=True), llm=Model()
    ).run("failure")
    assert result["stages"]["network"]["metadata"]["status"] == "skipped"


def test_unexpected_stage_error_is_sanitized(monkeypatch):
    manager = AgentManager(config=config(COLLECT_LOCAL_EVIDENCE=True), llm=Model())

    def broken(query):
        raise RuntimeError("secret-token private-host")

    monkeypatch.setattr(manager.agents["network"], "run", broken)
    result = manager.run("failure")
    assert result["status"] == "partial"
    assert "secret-token" not in json.dumps(result)


def test_summary_returning_after_deadline_is_not_accepted():
    class SlowSummary(Model):
        def chat(self, prompt, timeout=None):
            if "REPAIR_PLAN" not in prompt:
                time.sleep(0.02)
            return super().chat(prompt, timeout)

    result = AgentManager(config=config(DIAGNOSIS_TIMEOUT=0.01), llm=SlowSummary()).run("failure")
    assert result["status"] == "failed"
    assert result["stages"]["supervisor"]["metadata"]["error_code"] == "deadline"


def test_manager_does_not_finish_while_evidence_workers_still_run(monkeypatch):
    from agents.core.result import AgentResult

    started, release = threading.Event(), threading.Event()
    manager = AgentManager(
        config=config(COLLECT_LOCAL_EVIDENCE=True, DIAGNOSIS_TIMEOUT=0.01), llm=Model()
    )

    def slow(query):
        started.set()
        release.wait(3)
        return AgentResult("network", True, data={})

    monkeypatch.setattr(manager.agents["network"], "run", slow)
    monkeypatch.setattr(manager.agents["log"], "run", lambda q: AgentResult("log", True, data={}))
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(manager.run, "failure")
        assert started.wait(1)
        try:
            time.sleep(0.05)
            assert not pending.done()
        finally:
            release.set()
        assert pending.result()["status"] == "failed"
