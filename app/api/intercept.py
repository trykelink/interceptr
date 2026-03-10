# intercept.py — API route for the tool call interception endpoint
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.schemas.intercept import InterceptRequest, InterceptResponse
from app.services.interceptor_service import interceptor_service

router = APIRouter(prefix="/api/v1/intercept", tags=["intercept"])


@router.post("/", response_model=InterceptResponse)
@limiter.limit("60/minute")
def intercept_tool_call(
    request: Request,
    payload: InterceptRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    return interceptor_service.intercept(payload, db)
