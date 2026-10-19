import platform

from .base_tool import BaseTool
from .network import run_probe
from .result import ToolResult


class WSLTool(BaseTool):
    def __init__(self):
        super().__init__("wsl")

    def run(self, action, *, confirmed=False):
        if action != "restart" or confirmed is not True:
            return self.failure(
                "blocked", "Explicit confirmation required; stops all WSL distributions"
            )
        if platform.system() != "Windows":
            return self.failure("unsupported_platform")
        data = run_probe(["wsl", "--shutdown"], 15)
        return ToolResult(self.name, data["success"], data=data, error=data["error"])
