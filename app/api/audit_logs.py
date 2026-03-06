# audit_logs.py — API routes for creating and retrieving audit logs
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse, AuditLogListResponse
from app.services.audit_log_service import create_log, get_logs

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit-logs"])


@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(log_data: AuditLogCreate, db: Session = Depends(get_db)):
    return create_log(db, log_data)


@router.get("/", response_model=AuditLogListResponse)
def list_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs, total = get_logs(db, skip=skip, limit=limit)
    return AuditLogListResponse(logs=logs, total=total)
