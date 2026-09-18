from pydantic import BaseModel, Field
from typing import Optional, Dict, Any



class DiagnoseRequest(BaseModel):
    """
    用户诊断请求
    """

    question: str = Field(
        ...,
        description="用户描述的网络问题"
    )


    user_id: Optional[str] = Field(
        default=None,
        description="用户ID"
    )



class DiagnoseResponse(BaseModel):
    """
    诊断响应
    """


    success: bool


    question: str


    result: Dict[str, Any]