"""Fixed read-only probes; measurements always describe the API server."""

import ipaddress
import platform
import subprocess
import time
from datetime import datetime, timezone

from config.settings import settings

from .base_tool import BaseTool
from .result import ToolResult


def run_probe(argv, timeout):
    started = time.monotonic()
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, errors="replace", timeout=timeout, shell=False
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout[:12000],
            "error": None if result.returncode == 0 else "probe_failed",
            "duration_ms": round((time.monotonic() - started) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "timeout"}
    except OSError:
        return {"success": False, "output": "", "error": "tool_unavailable"}


class NetworkTool(BaseTool):
    def __init__(self, config=None):
        super().__init__("network")
        self.config = config or settings

    def run(self, target="1.1.1.1"):
        # Only literal addresses: no flags, shell syntax or unbounded DNS resolution.
        ipaddress.ip_address(target)
        windows = platform.system() == "Windows"
        ping = (
            ["ping", "-n", "1", "-w", str(int(self.config.TOOL_TIMEOUT * 1000)), target]
            if windows
            else ["ping", "-c", "1", "-W", str(max(1, int(self.config.TOOL_TIMEOUT))), target]
        )
        data = {
            "scope": "api_server",
            "platform": platform.system(),
            "target": target,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "ping": run_probe(ping, self.config.TOOL_TIMEOUT),
            "dns": run_probe(["nslookup", "github.com"], self.config.TOOL_TIMEOUT),
        }
        ok = data["ping"]["success"] and data["dns"]["success"]
        return ToolResult(
            self.name,
            ok,
            data=data,
            message="Read-only server probes completed",
            error=None if ok else "One or more probes failed",
        )
