from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
import app.models.audit_log  # noqa: F401 — registers AuditLog with Base.metadata
from app.api.audit_logs import router as audit_logs_router

# FastAPI application entry point, registers lifespan events and base routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected")
    yield


app = FastAPI(
    title="Interceptr",
    description="AI Agent Security Middleware",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(audit_logs_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
