# audit_log.py — Pydantic schemas for validating and serializing audit log data
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.audit_log import LogStatus


class AuditLogCreate(BaseModel):
    agent: str
    tool: str
    arguments: dict
    status: LogStatus
    reason: Optional[str] = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    agent: str
    tool: str
    arguments: dict
    status: LogStatus
    reason: Optional[str] = None


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
