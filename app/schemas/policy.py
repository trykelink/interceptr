# policy.py — Pydantic schemas for policy information responses
from typing import Optional
from pydantic import BaseModel


class PolicyInfo(BaseModel):
    agent: str
    allow_count: int
    deny_count: int
    default: str
    policy_path: str


class PolicyReloadResponse(BaseModel):
    status: str
    policy: Optional[PolicyInfo] = None
