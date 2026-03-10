# audit_log_service.py — Business logic for creating and querying audit logs
import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate

_MAX_STRING_LENGTH = 1_000
_MAX_ITEMS_PER_COLLECTION = 100
_MAX_NESTING_DEPTH = 5
_SENSITIVE_KEYS = {
    "password",
    "passphrase",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "credential",
    "private_key",
    "ssn",
}


def _sanitize_for_audit(value, depth: int = 0):
    if depth >= _MAX_NESTING_DEPTH:
        return "[truncated_depth]"

    if isinstance(value, dict):
        sanitized: dict = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= _MAX_ITEMS_PER_COLLECTION:
                sanitized["truncated"] = True
                break
            normalized_key = str(key)
            if normalized_key.lower() in _SENSITIVE_KEYS:
                sanitized[normalized_key] = "[redacted]"
            else:
                sanitized[normalized_key] = _sanitize_for_audit(item, depth + 1)
        return sanitized

    if isinstance(value, list):
        return [
            _sanitize_for_audit(item, depth + 1)
            for item in value[:_MAX_ITEMS_PER_COLLECTION]
        ]

    if isinstance(value, str):
        if len(value) > _MAX_STRING_LENGTH:
            return value[:_MAX_STRING_LENGTH]
        return value

    return value


def create_log(db: Session, log_data: AuditLogCreate) -> AuditLog:
    payload = log_data.model_dump()
    payload["arguments"] = _sanitize_for_audit(payload.get("arguments", {}))
    log = AuditLog(id=str(uuid.uuid4()), **payload)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[AuditLog], int]:
    total = db.query(AuditLog).count()
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs, total
