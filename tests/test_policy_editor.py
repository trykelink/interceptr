# test_policy_editor.py — Unit tests for policy editor pure functions (YAML read/write)
import yaml
import pytest

from interceptr.cli.tui.policy_editor import (
    apply_deny_precedence,
    build_yaml_content,
    parse_policy_yaml,
)


# ── build_yaml_content ─────────────────────────────────────────────────────────

def test_build_yaml_basic_structure() -> None:
    content = build_yaml_content(
        agent="*",
        allow=["read_customer", "list_orders"],
        deny=["drop_table", "delete_customer"],
        default="deny",
    )
    data = yaml.safe_load(content)
    assert data["agent"] == "*"
    assert data["rules"]["allow"] == ["read_customer", "list_orders"]
    assert data["rules"]["deny"] == ["drop_table", "delete_customer"]
    assert data["default"] == "deny"


def test_build_yaml_allow_default() -> None:
    content = build_yaml_content(
        agent="customer-support",
        allow=["read_customer"],
        deny=[],
        default="allow",
    )
    data = yaml.safe_load(content)
    assert data["agent"] == "customer-support"
    assert data["default"] == "allow"
    assert data["rules"]["deny"] == [] or data["rules"]["deny"] is None


def test_build_yaml_empty_lists() -> None:
    content = build_yaml_content(agent="*", allow=[], deny=[], default="allow")
    data = yaml.safe_load(content)
    rules = data["rules"]
    assert rules["allow"] == [] or rules["allow"] is None  # PyYAML may emit null or []
    assert rules["deny"] == [] or rules["deny"] is None


def test_build_yaml_agent_fallback_on_empty() -> None:
    content = build_yaml_content(agent="", allow=[], deny=[], default="allow")
    data = yaml.safe_load(content)
    assert data["agent"] == "*"


def test_build_yaml_key_order() -> None:
    content = build_yaml_content(agent="*", allow=["read_file"], deny=[], default="deny")
    lines = content.splitlines()
    # Only top-level keys (not indented)
    top_keys = [line.split(":")[0].strip() for line in lines if ":" in line and not line.startswith(" ")]
    assert top_keys.index("version") < top_keys.index("agent")
    assert top_keys.index("agent") < top_keys.index("rules")
    assert top_keys.index("rules") < top_keys.index("default")


def test_build_yaml_is_valid_yaml() -> None:
    content = build_yaml_content(
        agent="test-agent",
        allow=["read_customer", "list_orders"],
        deny=["drop_table"],
        default="deny",
    )
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict)


# ── parse_policy_yaml ──────────────────────────────────────────────────────────

def test_parse_policy_yaml_full_legacy_format() -> None:
    """Old flat format (top-level allow/deny) is still parsed for backwards compat."""
    yaml_str = """
agent: "customer-support"
allow:
  - read_customer
  - list_orders
deny:
  - delete_customer
  - drop_table
default: deny
"""
    result = parse_policy_yaml(yaml_str)
    assert result["agent"] == "customer-support"
    assert result["allow"] == ["read_customer", "list_orders"]
    assert result["deny"] == ["delete_customer", "drop_table"]
    assert result["default"] == "deny"


def test_parse_policy_yaml_full_engine_format() -> None:
    """New PolicyEngine format (rules.allow / rules.deny) is read correctly."""
    yaml_str = """
version: "1.0"
agent: "customer-support"
rules:
  allow:
    - read_customer
    - list_orders
  deny:
    - delete_customer
    - drop_table
default: deny
"""
    result = parse_policy_yaml(yaml_str)
    assert result["agent"] == "customer-support"
    assert result["allow"] == ["read_customer", "list_orders"]
    assert result["deny"] == ["delete_customer", "drop_table"]
    assert result["default"] == "deny"


def test_parse_policy_yaml_wildcard_agent() -> None:
    result = parse_policy_yaml("agent: '*'\nallow: []\ndeny: []\ndefault: allow\n")
    assert result["agent"] == "*"


def test_parse_policy_yaml_missing_fields_use_defaults() -> None:
    result = parse_policy_yaml("agent: bot\n")
    assert result["allow"] == []
    assert result["deny"] == []
    assert result["default"] == "allow"


def test_parse_policy_yaml_null_lists_treated_as_empty() -> None:
    result = parse_policy_yaml("agent: '*'\nallow:\ndeny:\ndefault: allow\n")
    assert result["allow"] == []
    assert result["deny"] == []


def test_parse_policy_yaml_empty_string_returns_defaults() -> None:
    result = parse_policy_yaml("")
    assert result["agent"] == "*"
    assert result["allow"] == []
    assert result["deny"] == []
    assert result["default"] == "allow"


def test_parse_policy_yaml_non_dict_returns_defaults() -> None:
    result = parse_policy_yaml("- item1\n- item2\n")
    assert result["agent"] == "*"
    assert result["allow"] == []


# ── apply_deny_precedence ──────────────────────────────────────────────────────

def test_deny_precedence_removes_conflict() -> None:
    allow = ["read_customer", "delete_customer"]
    deny = ["delete_customer", "drop_table"]
    clean_allow, clean_deny = apply_deny_precedence(allow, deny)
    assert "delete_customer" not in clean_allow
    assert "read_customer" in clean_allow
    assert clean_deny == deny


def test_deny_precedence_no_overlap() -> None:
    allow = ["read_customer", "list_orders"]
    deny = ["drop_table", "delete_customer"]
    clean_allow, clean_deny = apply_deny_precedence(allow, deny)
    assert clean_allow == allow
    assert clean_deny == deny


def test_deny_precedence_allow_empty() -> None:
    clean_allow, clean_deny = apply_deny_precedence([], ["drop_table"])
    assert clean_allow == []
    assert clean_deny == ["drop_table"]


def test_deny_precedence_deny_empty() -> None:
    allow = ["read_customer", "list_orders"]
    clean_allow, clean_deny = apply_deny_precedence(allow, [])
    assert clean_allow == allow
    assert clean_deny == []


def test_deny_precedence_both_empty() -> None:
    clean_allow, clean_deny = apply_deny_precedence([], [])
    assert clean_allow == []
    assert clean_deny == []


def test_deny_precedence_all_in_both_lists() -> None:
    tools = ["read_customer", "drop_table"]
    clean_allow, clean_deny = apply_deny_precedence(tools, tools)
    assert clean_allow == []
    assert clean_deny == tools


# ── round-trip: build then parse ───────────────────────────────────────────────

def test_roundtrip_build_parse() -> None:
    agent = "automation-bot"
    allow = ["read_customer", "list_orders", "http_request"]
    deny = ["drop_table", "delete_customer", "execute_command"]
    default = "deny"

    content = build_yaml_content(agent=agent, allow=allow, deny=deny, default=default)
    result = parse_policy_yaml(content)

    assert result["agent"] == agent
    assert result["allow"] == allow
    assert result["deny"] == deny
    assert result["default"] == default


def test_roundtrip_empty_policy() -> None:
    content = build_yaml_content(agent="*", allow=[], deny=[], default="allow")
    result = parse_policy_yaml(content)
    assert result["agent"] == "*"
    assert result["allow"] == [] or result["allow"] is None
    assert result["deny"] == [] or result["deny"] is None
    assert result["default"] == "allow"


# ── build_yaml_content: PolicyEngine compatibility ─────────────────────────────

def test_build_yaml_has_version_field() -> None:
    """Output must include version: '1.0' required by PolicyEngine."""
    content = build_yaml_content(agent="*", allow=[], deny=[], default="allow")
    data = yaml.safe_load(content)
    assert data.get("version") == "1.0"


def test_build_yaml_nests_allow_deny_under_rules() -> None:
    """allow and deny must be under a 'rules' key, not at top level."""
    content = build_yaml_content(agent="*", allow=["read_customer"], deny=["drop_table"], default="allow")
    data = yaml.safe_load(content)
    assert "rules" in data
    assert "allow" not in data  # must NOT be at top level
    assert "deny" not in data   # must NOT be at top level
    assert "read_customer" in (data["rules"].get("allow") or [])
    assert "drop_table" in (data["rules"].get("deny") or [])


def test_build_yaml_loadable_by_policy_engine(tmp_path) -> None:
    """Output of build_yaml_content must be loadable by PolicyEngine without error."""
    from app.core.policy_engine import PolicyEngine
    content = build_yaml_content(
        agent="*",
        allow=["read_customer", "list_orders"],
        deny=["drop_table", "delete_customer"],
        default="deny",
    )
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(content)
    engine = PolicyEngine(str(policy_path))
    assert engine.agent == "*"
    assert "read_customer" in engine.allow_list
    assert "drop_table" in engine.deny_list
    assert engine.default == "deny"


def test_parse_policy_yaml_rules_take_precedence_over_legacy() -> None:
    """When both 'rules' and top-level 'allow'/'deny' exist, rules wins."""
    yaml_str = """
version: "1.0"
agent: "bot"
allow:
  - legacy_tool
rules:
  allow:
    - real_tool
  deny: []
default: allow
"""
    result = parse_policy_yaml(yaml_str)
    assert "real_tool" in result["allow"]
    assert "legacy_tool" not in result["allow"]


def test_parse_policy_yaml_null_rules_falls_back_to_legacy() -> None:
    """If 'rules' key exists but is null, fall back to top-level allow/deny."""
    yaml_str = "agent: bot\nrules:\nallow:\n  - fallback_tool\ndeny: []\ndefault: allow\n"
    result = parse_policy_yaml(yaml_str)
    assert "fallback_tool" in result["allow"]
