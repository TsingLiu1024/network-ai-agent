import json
import platform
import subprocess
from datetime import datetime, timezone

from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult
from config.settings import settings
from llm.optimizer import redact_data

# One complete pipeline, JSON rather than a truncated Format-Table.
LOG_COMMAND = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Get-WinEvent -FilterHashtable @{LogName='System'; Level=2,3} -MaxEvents 20 -ErrorAction Stop | Select-Object TimeCreated,LevelDisplayName,ProviderName,Id,Message | ConvertTo-Json -Depth 3 -Compress"


class LogAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("log_agent", "API server Windows event evidence")
        self.config = config or settings

    def run(self, query):
        cloud = self.config.MODEL_PROVIDER in {"openai", "deepseek"}
        if not self.config.COLLECT_LOCAL_EVIDENCE or (
            cloud and not self.config.ALLOW_CLOUD_LOG_UPLOAD
        ):
            return AgentResult(
                self.name,
                False,
                message="Local evidence disabled or cloud upload not permitted",
                metadata={"status": "skipped"},
            )
        if platform.system() != "Windows":
            return AgentResult(
                self.name,
                False,
                message="Windows event logs unavailable on this platform",
                metadata={"status": "skipped"},
            )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", LOG_COMMAND],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.config.TOOL_TIMEOUT,
                shell=False,
            )
            if result.returncode != 0:
                return AgentResult(
                    self.name,
                    False,
                    message="Log collection failed",
                    metadata={"error_code": "log_collection_failed"},
                )
            if len(result.stdout) > 32000:
                raise ValueError("Too much output")
            events = json.loads(result.stdout)
            if isinstance(events, dict):
                events = [events]
            if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
                raise ValueError("Invalid event data")
            return AgentResult(
                self.name,
                True,
                data={
                    "scope": "api_server",
                    "events": redact_data(events),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
                message="Windows events collected",
            )
        except (OSError, subprocess.TimeoutExpired, ValueError):
            return AgentResult(
                self.name,
                False,
                message="Log collection unavailable",
                metadata={"error_code": "log_collection_failed"},
            )
