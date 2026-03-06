# audit_log.py — SQLAlchemy model representing the audit_logs table in PostgreSQL
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class LogStatus(str, enum.Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    agent: Mapped[str] = mapped_column(String, nullable=False)
    tool: Mapped[str] = mapped_column(String, nullable=False)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[LogStatus] = mapped_column(SAEnum(LogStatus, native_enum=False), nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
