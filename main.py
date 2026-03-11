# main.py — FastAPI application entry point with security middleware and API router registration.
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.database import engine, Base
import app.models.audit_log  # noqa: F401 — registers AuditLog with Base.metadata
from app.api.audit_logs import router as audit_logs_router
from app.api.intercept import router as intercept_router
from app.api.policy import router as policy_router
from app.api.analyze import router as analyze_router
from app.core.policy_engine import PolicyEngine
from app.core.rate_limiter import limiter
from app.services.interceptor_service import interceptor_service

logger = logging.getLogger(__name__)


def _is_truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
ENABLE_DOCS = _is_truthy(
    os.getenv("INTERCEPTR_ENABLE_DOCS"),
    default=APP_ENV != "production",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database connected")
    if os.path.isfile("policy.yaml"):
        try:
            interceptor_service.policy_engine = PolicyEngine("policy.yaml")
            logger.info("Policy loaded for agent=%s", interceptor_service.policy_engine.agent)
        except (ValueError, FileNotFoundError) as exc:
            interceptor_service.policy_engine = None
            logger.warning("policy.yaml present but could not be loaded (%s). All tool calls will be ALLOWED.", exc)
    else:
        logger.warning("No policy.yaml found. All tool calls will be ALLOWED by default.")
    yield


app = FastAPI(
    title="Interceptr",
    description="AI Agent Security Middleware",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    base_response = _rate_limit_exceeded_handler(request, exc)
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
        headers=dict(base_response.headers),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Request validation failed on path=%s", request.url.path)
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request payload"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on path=%s", request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


app.include_router(audit_logs_router)
app.include_router(intercept_router)
app.include_router(policy_router)
app.include_router(analyze_router)


@app.get("/health")
def health():
    return {"status": "ok"}
