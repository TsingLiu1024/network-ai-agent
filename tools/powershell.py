"""Compatibility class name; executes fixed argv only, never PowerShell text."""

import platform

from .base_tool import BaseTool
from .network import run_probe
from .policy import ToolPolicy
from .result import ToolResult


class PowerShellTool(BaseTool):
    def __init__(self):
        super().__init__("powershell")

    def run(self, action, *, confirmed=False):
        if not ToolPolicy.check(action) or confirmed is not True:
            return self.failure("blocked", "Named action and explicit confirmation required")
        if platform.system() != "Windows":
            return self.failure("unsupported_platform")
        data = run_probe(list(ToolPolicy.ACTIONS[action]), 10)
        return ToolResult(
            self.name,
            data["success"],
            data=data,
            error=data["error"],
            message="Repair action finished",
        )
