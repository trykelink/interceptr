# audit_log_service.py — Business logic for creating and querying audit logs
import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate


def create_log(db: Session, log_data: AuditLogCreate) -> AuditLog:
    log = AuditLog(id=str(uuid.uuid4()), **log_data.model_dump())
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
