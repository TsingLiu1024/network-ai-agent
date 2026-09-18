from dataclasses import dataclass, field
from typing import Any, Dict



@dataclass
class AgentResult:
    """
    Agent统一返回结果
    """


    agent: str


    success: bool


    data: Any = None


    message: str = ""


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    def to_dict(self):

        return {

            "agent": self.agent,

            "success": self.success,

            "data": self.data,

            "message": self.message,

            "metadata": self.metadata

        }