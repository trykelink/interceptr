# analysis.py - Pydantic schemas for prompt injection analysis requests and responses
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    input: str
    agent: str | None = None


class AnalyzeResponse(BaseModel):
    is_injection: bool
    severity: str | None
    patterns_matched: list[str]
    categories: list[str]
    recommendation: str
    input_preview: str
    log_id: str | None = None
