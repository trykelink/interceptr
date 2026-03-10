# analyze.py - API route for prompt injection analysis endpoint
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.injection_detector import injection_detector
from app.core.rate_limiter import limiter
from app.models.audit_log import LogStatus
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.schemas.audit_log import AuditLogCreate
from app.services.audit_log_service import create_log

router = APIRouter(prefix="/api/v1/analyze", tags=["analyze"])


@router.post("/", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
def analyze_input(
    request: Request,
    payload: AnalyzeRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    analysis_result = injection_detector.analyze(payload.input_text)
    input_preview = payload.input_text[:100]
    log_id: str | None = None

    if analysis_result.is_injection and analysis_result.severity in {"high", "medium"}:
        log_data = AuditLogCreate(
            agent=payload.agent or "unknown",
            tool="prompt_injection_detected",
            arguments={
                "input_preview": input_preview,
                "severity": analysis_result.severity,
                "patterns": analysis_result.patterns_matched,
            },
            status=LogStatus.BLOCKED,
            reason=f"prompt_injection_{analysis_result.severity}",
        )
        log = create_log(db, log_data)
        log_id = log.id

    return AnalyzeResponse(
        is_injection=analysis_result.is_injection,
        severity=analysis_result.severity,
        patterns_matched=analysis_result.patterns_matched,
        categories=analysis_result.categories,
        recommendation=analysis_result.recommendation,
        input_preview=input_preview,
        log_id=log_id,
    )
