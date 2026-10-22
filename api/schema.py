from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DiagnoseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)
    question: str = Field(
        min_length=1, max_length=2000, validation_alias=AliasChoices("question", "problem")
    )
    user_id: str | None = Field(default=None, max_length=100)


class DiagnoseResponse(BaseModel):
    success: bool
    status: Literal["success", "partial", "failed", "demo"]
    question: str
    request_id: str
    result: dict[str, Any]
