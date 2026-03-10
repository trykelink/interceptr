# intercept.py — Pydantic schemas for tool call interception requests and responses
import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator

_MAX_ARGUMENTS_SIZE = 20_000
_MAX_METADATA_SIZE = 4_096


class InterceptDecision(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


class InterceptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: str = Field(..., max_length=100)
    tool: str = Field(..., max_length=200)
    arguments: dict = Field(...)
    metadata: dict | None = Field(default=None)

    @field_validator("arguments")
    @classmethod
    def validate_arguments_size(cls, value: dict) -> dict:
        if len(json.dumps(value, ensure_ascii=False)) > _MAX_ARGUMENTS_SIZE:
            raise ValueError(f"arguments payload must be <= {_MAX_ARGUMENTS_SIZE} characters")
        return value

    @field_validator("metadata")
    @classmethod
    def validate_metadata_size(cls, value: dict | None) -> dict | None:
        if value is None:
            return value
        if len(json.dumps(value, ensure_ascii=False)) > _MAX_METADATA_SIZE:
            raise ValueError(f"metadata payload must be <= {_MAX_METADATA_SIZE} characters")
        return value


class InterceptResponse(BaseModel):
    decision: InterceptDecision
    reason: str | None
    log_id: str
    agent: str
    tool: str
    timestamp: datetime
