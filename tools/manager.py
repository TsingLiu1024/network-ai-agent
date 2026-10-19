"""
Tool Manager

负责管理所有自动修复工具
"""

from tools.base_tool import BaseTool


class ToolManager:
    def __init__(self):

        self.tools = {}

    def register(self, tool: BaseTool):

        self.tools[tool.name] = tool

    def get(self, name: str):

        return self.tools.get(name)

    def list_tools(self):

        return list(self.tools.keys())
