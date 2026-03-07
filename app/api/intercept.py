# intercept.py — API route for the tool call interception endpoint
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.intercept import InterceptRequest, InterceptResponse
from app.services.interceptor_service import interceptor_service

router = APIRouter(prefix="/api/v1/intercept", tags=["intercept"])


@router.post("/", response_model=InterceptResponse)
def intercept_tool_call(request: InterceptRequest, db: Session = Depends(get_db)):
    return interceptor_service.intercept(request, db)
