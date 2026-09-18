from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """
    Tool统一返回结果
    """

    tool: str

    success: bool

    data: Any = None

    message: str = ""

    error: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    def to_dict(self):

        return {

            "tool": self.tool,

            "success": self.success,

            "data": self.data,

            "message": self.message,

            "error": self.error,

            "metadata": self.metadata

        }