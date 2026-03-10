# analysis.py - Pydantic schemas for prompt injection analysis requests and responses
from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    input_text: str = Field(..., alias="input", max_length=10_000)
    agent: str | None = Field(default=None, max_length=100)


class AnalyzeResponse(BaseModel):
    is_injection: bool
    severity: str | None
    patterns_matched: list[str]
    categories: list[str]
    recommendation: str
    input_preview: str
    log_id: str | None = None
