from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult
from tools.network import NetworkTool


class NetworkAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("network_agent", "Read-only measurements on API server")
        self.tool = NetworkTool(config)

    def run(self, query):
        result = self.tool.run()
        return AgentResult(
            self.name,
            result.success,
            data=result.data,
            message=result.message,
            metadata={"error_code": result.error},
        )
