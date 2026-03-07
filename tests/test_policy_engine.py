# test_policy_engine.py — Unit tests for PolicyEngine YAML parsing and evaluation logic
import pytest
import yaml
from app.core.policy_engine import PolicyEngine
from app.schemas.intercept import InterceptDecision, InterceptRequest


def make_policy_file(tmp_path, data: dict) -> str:
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.dump(data))
    return str(path)


def make_request(agent: str, tool: str) -> InterceptRequest:
    return InterceptRequest(agent=agent, tool=tool, arguments={})


BASE_POLICY = {
    "version": "1.0",
    "agent": "test-agent",
    "rules": {
        "allow": ["read_customer", "list_orders"],
        "deny": ["delete_customer", "drop_table"],
    },
    "default": "deny",
}


def test_policy_blocks_denied_tool(tmp_path):
    path = make_policy_file(tmp_path, BASE_POLICY)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("test-agent", "delete_customer"))
    assert decision == InterceptDecision.BLOCKED
    assert reason == "policy_violation"


def test_policy_allows_allowed_tool(tmp_path):
    path = make_policy_file(tmp_path, BASE_POLICY)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("test-agent", "read_customer"))
    assert decision == InterceptDecision.ALLOWED
    assert reason is None


def test_policy_default_deny_blocks_unknown_tool(tmp_path):
    path = make_policy_file(tmp_path, BASE_POLICY)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("test-agent", "send_email"))
    assert decision == InterceptDecision.BLOCKED
    assert reason == "not_in_allowlist"


def test_policy_default_allow_passes_unknown_tool(tmp_path):
    policy = {**BASE_POLICY, "default": "allow"}
    path = make_policy_file(tmp_path, policy)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("test-agent", "send_email"))
    assert decision == InterceptDecision.ALLOWED
    assert reason is None


def test_policy_wildcard_agent_matches_any(tmp_path):
    policy = {**BASE_POLICY, "agent": "*"}
    path = make_policy_file(tmp_path, policy)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("any-random-agent", "delete_customer"))
    assert decision == InterceptDecision.BLOCKED
    assert reason == "policy_violation"


def test_policy_agent_mismatch_allows_all(tmp_path):
    path = make_policy_file(tmp_path, BASE_POLICY)
    engine = PolicyEngine(path)
    # policy is for "test-agent", but request is from "other-agent"
    decision, reason = engine.evaluate(make_request("other-agent", "delete_customer"))
    assert decision == InterceptDecision.ALLOWED
    assert reason is None


def test_policy_deny_takes_precedence(tmp_path):
    policy = {
        "version": "1.0",
        "agent": "test-agent",
        "rules": {
            "allow": ["read_customer"],
            "deny": ["read_customer"],  # same tool in both lists
        },
        "default": "allow",
    }
    path = make_policy_file(tmp_path, policy)
    engine = PolicyEngine(path)
    decision, reason = engine.evaluate(make_request("test-agent", "read_customer"))
    assert decision == InterceptDecision.BLOCKED
    assert reason == "policy_violation"


def test_policy_reload(tmp_path):
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(yaml.dump(BASE_POLICY))
    engine = PolicyEngine(str(policy_path))

    # Initially delete_customer is denied
    decision, _ = engine.evaluate(make_request("test-agent", "delete_customer"))
    assert decision == InterceptDecision.BLOCKED

    # Modify the file to remove delete_customer from deny and set default=allow
    updated = {
        "version": "1.0",
        "agent": "test-agent",
        "rules": {"allow": [], "deny": []},
        "default": "allow",
    }
    policy_path.write_text(yaml.dump(updated))
    engine.reload()

    decision, _ = engine.evaluate(make_request("test-agent", "delete_customer"))
    assert decision == InterceptDecision.ALLOWED


def test_policy_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        PolicyEngine(str(tmp_path / "nonexistent.yaml"))


def test_policy_invalid_yaml_missing_fields(tmp_path):
    policy_path = tmp_path / "bad_policy.yaml"
    policy_path.write_text(yaml.dump({"version": "1.0"}))  # missing agent, rules, default
    with pytest.raises(ValueError):
        PolicyEngine(str(policy_path))
