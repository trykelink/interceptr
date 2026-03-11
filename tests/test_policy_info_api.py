# test_policy_info_api.py — Tests for GET /api/v1/policy/ loaded flag and info shape
import itertools
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
_CLIENT_COUNTER = itertools.count(start=1)

POLICY_DATA = {
    "version": "1.0",
    "agent": "test-agent",
    "rules": {
        "allow": ["read_customer", "list_orders"],
        "deny": ["drop_table", "delete_customer"],
    },
    "default": "deny",
}


@pytest.fixture
async def no_policy_client():
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
    transport = ASGITransport(app=app, client=(f"10.40.0.{octet}", 50_010))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    interceptor_service.policy_engine = None
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def policy_client(tmp_path):
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
    transport = ASGITransport(app=app, client=(f"10.40.0.{octet}", 50_011))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    interceptor_service.policy_engine = None
    Base.metadata.drop_all(bind=engine)


# ── GET /api/v1/policy/ with no policy loaded ────────────────────────────────

@pytest.mark.anyio
async def test_get_policy_no_policy_loaded_is_200(no_policy_client):
    response = await no_policy_client.get("/api/v1/policy/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_policy_no_policy_loaded_flag_is_false(no_policy_client):
    response = await no_policy_client.get("/api/v1/policy/")
    assert response.json()["loaded"] is False


@pytest.mark.anyio
async def test_get_policy_no_policy_has_status_field(no_policy_client):
    response = await no_policy_client.get("/api/v1/policy/")
    assert response.json().get("status") == "no_policy_loaded"


# ── GET /api/v1/policy/ with a policy loaded ─────────────────────────────────

@pytest.mark.anyio
async def test_get_policy_loaded_flag_is_true(policy_client):
    response = await policy_client.get("/api/v1/policy/")
    assert response.json()["loaded"] is True


@pytest.mark.anyio
async def test_get_policy_has_agent_field(policy_client):
    response = await policy_client.get("/api/v1/policy/")
    assert response.json()["agent"] == "test-agent"


@pytest.mark.anyio
async def test_get_policy_has_allow_list(policy_client):
    response = await policy_client.get("/api/v1/policy/")
    data = response.json()
    assert "allow" in data
    assert isinstance(data["allow"], list)
    assert "read_customer" in data["allow"]


@pytest.mark.anyio
async def test_get_policy_has_deny_list(policy_client):
    response = await policy_client.get("/api/v1/policy/")
    data = response.json()
    assert "deny" in data
    assert isinstance(data["deny"], list)
    assert "drop_table" in data["deny"]


@pytest.mark.anyio
async def test_get_policy_has_default_field(policy_client):
    response = await policy_client.get("/api/v1/policy/")
    assert response.json()["default"] == "deny"


# ── PolicyEngine.info property ────────────────────────────────────────────────

def test_policy_engine_info_includes_loaded_true(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.dump(POLICY_DATA))
    engine = PolicyEngine(str(path))
    assert engine.info["loaded"] is True


def test_policy_engine_info_includes_allow_list(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.dump(POLICY_DATA))
    engine = PolicyEngine(str(path))
    assert engine.info["allow"] == ["read_customer", "list_orders"]


def test_policy_engine_info_includes_deny_list(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.dump(POLICY_DATA))
    engine = PolicyEngine(str(path))
    assert engine.info["deny"] == ["drop_table", "delete_customer"]


def test_policy_engine_info_no_longer_has_count_fields(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.dump(POLICY_DATA))
    engine = PolicyEngine(str(path))
    assert "allow_count" not in engine.info
    assert "deny_count" not in engine.info
