# intercept.py — Pydantic schemas for tool call interception requests and responses
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class InterceptDecision(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


class InterceptRequest(BaseModel):
    agent: str
    tool: str
    arguments: dict
    metadata: Optional[dict] = None


class InterceptResponse(BaseModel):
    decision: InterceptDecision
    reason: Optional[str]
    log_id: str
    agent: str
    tool: str
    timestamp: datetime
