# audit_log.py — Pydantic schemas for validating and serializing audit log data
import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.audit_log import LogStatus

_MAX_ARGUMENTS_SIZE = 20_000


class AuditLogCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: str = Field(..., max_length=100)
    tool: str = Field(..., max_length=200)
    arguments: dict = Field(...)
    status: LogStatus
    reason: str | None = Field(default=None, max_length=1_000)

    @field_validator("arguments")
    @classmethod
    def validate_arguments_size(cls, value: dict) -> dict:
        if len(json.dumps(value, ensure_ascii=False)) > _MAX_ARGUMENTS_SIZE:
            raise ValueError(f"arguments payload must be <= {_MAX_ARGUMENTS_SIZE} characters")
        return value


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    agent: str
    tool: str
    arguments: dict
    status: LogStatus
    reason: str | None = None


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
