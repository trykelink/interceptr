# test_policy_reload_api.py — Tests for POST /api/v1/policy/reload 422 behavior
import itertools
import os
import pytest
import yaml
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

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
_CLIENT_COUNTER = itertools.count(start=1)

POLICY_DATA = {
    "version": "1.0",
    "agent": "*",
    "rules": {"allow": ["read_customer"], "deny": ["drop_table"]},
    "default": "allow",
}


@pytest.fixture
async def plain_client():
    """Client with no policy loaded and a fresh in-memory DB."""
    Base.metadata.create_all(bind=engine)
    interceptor_service.policy_engine = None

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    octet = (next(_CLIENT_COUNTER) % 253) + 1
    transport = ASGITransport(app=app, client=(f"10.30.0.{octet}", 50_002))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    interceptor_service.policy_engine = None
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def client_with_policy(tmp_path):
    """Client with a policy already loaded."""
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
    octet = (next(_CLIENT_COUNTER) % 253) + 1
    transport = ASGITransport(app=app, client=(f"10.30.0.{octet}", 50_003))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    interceptor_service.policy_engine = None
    Base.metadata.drop_all(bind=engine)


@pytest.mark.anyio
async def test_reload_returns_422_when_no_policy_file(plain_client):
    """POST /reload with no policy loaded and no file on disk → 422."""
    with patch("os.path.isfile", return_value=False):
        response = await plain_client.post("/api/v1/policy/reload")
    assert response.status_code == 422
    body = response.json()
    assert "policy.yaml" in body["detail"].lower() or "no policy" in body["detail"].lower()


@pytest.mark.anyio
async def test_reload_422_detail_mentions_policy_edit(plain_client):
    """422 error detail references 'interceptr policy edit' to help the user."""
    with patch("os.path.isfile", return_value=False):
        response = await plain_client.post("/api/v1/policy/reload")
    assert response.status_code == 422
    assert "interceptr policy edit" in response.json()["detail"]


@pytest.mark.anyio
async def test_reload_does_not_return_404(plain_client):
    """Ensures the old 404 behavior is gone."""
    with patch("os.path.isfile", return_value=False):
        response = await plain_client.post("/api/v1/policy/reload")
    assert response.status_code != 404


@pytest.mark.anyio
async def test_reload_succeeds_when_policy_file_exists(plain_client, tmp_path):
    """POST /reload with no policy loaded but file present → loads and returns 200."""
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(yaml.dump(POLICY_DATA))

    with patch("os.path.isfile", return_value=True), \
         patch("app.api.policy.PolicyEngine", return_value=PolicyEngine(str(policy_path))):
        response = await plain_client.post("/api/v1/policy/reload")

    assert response.status_code == 200
    assert response.json()["status"] == "reloaded"


@pytest.mark.anyio
async def test_reload_reloads_existing_policy(client_with_policy):
    """POST /reload when policy already loaded → reloads without error."""
    response = await client_with_policy.post("/api/v1/policy/reload")
    assert response.status_code == 200
    assert response.json()["status"] == "reloaded"
