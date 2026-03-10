# conftest.py — pytest fixtures and database setup for testing
import itertools
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
import app.models.audit_log  # noqa: F401 — ensures AuditLog is registered with Base
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_CLIENT_COUNTER = itertools.count(start=1)


def _next_test_client_ip() -> str:
    octet = (next(_CLIENT_COUNTER) % 253) + 1
    return f"10.10.0.{octet}"


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def client(setup_db):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app, client=(_next_test_client_ip(), 50_000))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
