import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
import app.models.audit_log  # noqa: F401 — registers AuditLog with Base.metadata
from app.api.audit_logs import router as audit_logs_router
from app.api.intercept import router as intercept_router
from app.api.policy import router as policy_router
from app.api.analyze import router as analyze_router
from app.core.policy_engine import PolicyEngine
from app.services.interceptor_service import interceptor_service

# FastAPI application entry point, registers lifespan events and base routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected")
    if os.path.isfile("policy.yaml"):
        interceptor_service.policy_engine = PolicyEngine("policy.yaml")
        print(f"✅ Policy loaded: {interceptor_service.policy_engine.agent}")
    else:
        print("⚠️  No policy.yaml found. All tool calls will be ALLOWED by default.")
    yield


app = FastAPI(
    title="Interceptr",
    description="AI Agent Security Middleware",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(audit_logs_router)
app.include_router(intercept_router)
app.include_router(policy_router)
app.include_router(analyze_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
