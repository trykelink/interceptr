# test_intercept_with_policy.py — Integration tests for interception with policy engine active
import pytest
import yaml
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.policy_engine import PolicyEngine
from app.services.interceptor_service import interceptor_service
import app.models.audit_log  # noqa: F401
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

POLICY_DATA = {
    "version": "1.0",
    "agent": "customer-support-agent",
    "rules": {
        "allow": ["read_customer", "list_orders"],
        "deny": ["delete_customer", "drop_table"],
    },
    "default": "deny",
}


@pytest.fixture
async def client_with_policy(tmp_path):
    Base.metadata.create_all(bind=engine)

    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(yaml.dump(POLICY_DATA))
    interceptor_service.policy_engine = PolicyEngine(str(policy_path))

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    interceptor_service.policy_engine = None
    Base.metadata.drop_all(bind=engine)


@pytest.mark.anyio
async def test_intercept_blocked_by_policy(client_with_policy: AsyncClient):
    response = await client_with_policy.post(
        "/api/v1/intercept/",
        json={"agent": "customer-support-agent", "tool": "delete_customer", "arguments": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "BLOCKED"
    assert data["reason"] == "policy_violation"


@pytest.mark.anyio
async def test_intercept_allowed_by_policy(client_with_policy: AsyncClient):
    response = await client_with_policy.post(
        "/api/v1/intercept/",
        json={"agent": "customer-support-agent", "tool": "read_customer", "arguments": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOWED"
    assert data["reason"] is None


@pytest.mark.anyio
async def test_intercept_blocked_by_default_deny(client_with_policy: AsyncClient):
    response = await client_with_policy.post(
        "/api/v1/intercept/",
        json={"agent": "customer-support-agent", "tool": "send_email", "arguments": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "BLOCKED"
    assert data["reason"] == "not_in_allowlist"


@pytest.mark.anyio
async def test_intercept_audit_log_records_blocked_status(client_with_policy: AsyncClient):
    await client_with_policy.post(
        "/api/v1/intercept/",
        json={"agent": "customer-support-agent", "tool": "delete_customer", "arguments": {}},
    )
    response = await client_with_policy.get("/api/v1/audit-logs/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    log = data["logs"][0]
    assert log["status"] == "BLOCKED"
    assert log["tool"] == "delete_customer"


@pytest.mark.anyio
async def test_get_policy_info(client_with_policy: AsyncClient):
    response = await client_with_policy.get("/api/v1/policy/")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "customer-support-agent"
    assert data["allow_count"] == 2
    assert data["deny_count"] == 2
    assert data["default"] == "deny"


@pytest.mark.anyio
async def test_policy_reload_endpoint(client_with_policy: AsyncClient):
    response = await client_with_policy.post("/api/v1/policy/reload")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reloaded"
    assert data["policy"]["agent"] == "customer-support-agent"
