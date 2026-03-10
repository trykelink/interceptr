# audit_logs.py — API routes for creating and retrieving audit logs
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse, AuditLogListResponse
from app.services.audit_log_service import create_log, get_logs

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit-logs"])


@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(log_data: AuditLogCreate, db: Session = Depends(get_db)):
    return create_log(db, log_data)


@router.get("/", response_model=AuditLogListResponse)
@limiter.limit("30/minute")
def list_audit_logs(
    request: Request,
    response: Response,
    skip: int = Query(default=0, ge=0, le=10_000),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    logs, total = get_logs(db, skip=skip, limit=limit)
    return AuditLogListResponse(logs=logs, total=total)
