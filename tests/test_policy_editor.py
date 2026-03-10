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
    assert data["allow"] == ["read_customer", "list_orders"]
    assert data["deny"] == ["drop_table", "delete_customer"]
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
    assert data["deny"] == []


def test_build_yaml_empty_lists() -> None:
    content = build_yaml_content(agent="*", allow=[], deny=[], default="allow")
    data = yaml.safe_load(content)
    assert data["allow"] == [] or data["allow"] is None  # PyYAML may emit null or []
    assert data["deny"] == [] or data["deny"] is None


def test_build_yaml_agent_fallback_on_empty() -> None:
    content = build_yaml_content(agent="", allow=[], deny=[], default="allow")
    data = yaml.safe_load(content)
    assert data["agent"] == "*"


def test_build_yaml_key_order() -> None:
    content = build_yaml_content(agent="*", allow=["read_file"], deny=[], default="deny")
    lines = content.splitlines()
    keys = [line.split(":")[0].strip() for line in lines if ":" in line and not line.startswith(" ")]
    assert keys.index("agent") < keys.index("allow")
    assert keys.index("allow") < keys.index("deny")
    assert keys.index("deny") < keys.index("default")


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

def test_parse_policy_yaml_full() -> None:
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
