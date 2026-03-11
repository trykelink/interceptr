# policy_editor.py — Interactive policy editor TUI for Interceptr
from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import yaml
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import (
    Checkbox,
    Collapsible,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Static,
)

CONFIG_DIR = Path.home() / ".interceptr"
POLICY_FILE = CONFIG_DIR / "policy.yaml"
_RELOAD_URL = "http://localhost:8000/api/v1/policy/reload"

TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "category": "Database",
        "tools": [
            {"name": "read_customer", "description": "Read customer record"},
            {"name": "list_customers", "description": "List all customers"},
            {"name": "create_customer", "description": "Create a new customer"},
            {"name": "update_customer", "description": "Update customer data"},
            {"name": "delete_customer", "description": "Delete a customer record"},
            {"name": "export_customers", "description": "Export all customer data"},
            {"name": "read_order", "description": "Read an order"},
            {"name": "list_orders", "description": "List all orders"},
            {"name": "create_order", "description": "Create a new order"},
            {"name": "update_order", "description": "Update an order"},
            {"name": "delete_order", "description": "Delete an order"},
            {"name": "run_query", "description": "Execute a raw database query"},
            {"name": "drop_table", "description": "Drop a database table"},
        ],
    },
    {
        "category": "Files",
        "tools": [
            {"name": "read_file", "description": "Read a file from disk"},
            {"name": "write_file", "description": "Write a file to disk"},
            {"name": "delete_file", "description": "Delete a file"},
            {"name": "list_files", "description": "List files in a directory"},
            {"name": "execute_file", "description": "Execute a file"},
            {"name": "upload_file", "description": "Upload a file to storage"},
            {"name": "download_file", "description": "Download a file from storage"},
        ],
    },
    {
        "category": "Network",
        "tools": [
            {"name": "http_request", "description": "Make an HTTP request"},
            {"name": "webhook_call", "description": "Trigger a webhook"},
            {"name": "dns_lookup", "description": "Perform a DNS lookup"},
            {"name": "send_email", "description": "Send an email"},
            {"name": "send_slack_message", "description": "Post a Slack message"},
            {"name": "send_sms", "description": "Send an SMS"},
        ],
    },
    {
        "category": "Auth & Users",
        "tools": [
            {"name": "create_user", "description": "Create a new user account"},
            {"name": "delete_user", "description": "Delete a user account"},
            {"name": "update_user", "description": "Update user info"},
            {"name": "reset_password", "description": "Reset a user password"},
            {"name": "elevate_permissions", "description": "Grant elevated permissions"},
            {"name": "revoke_permissions", "description": "Revoke permissions"},
            {"name": "list_users", "description": "List all users"},
        ],
    },
    {
        "category": "System",
        "tools": [
            {"name": "execute_command", "description": "Run a shell command"},
            {"name": "restart_service", "description": "Restart a system service"},
            {"name": "modify_config", "description": "Modify a config file"},
            {"name": "read_env", "description": "Read environment variables"},
            {"name": "write_env", "description": "Write environment variables"},
            {"name": "get_system_info", "description": "Get system info"},
        ],
    },
    {
        "category": "LLM",
        "tools": [
            {"name": "call_model", "description": "Call an LLM model"},
            {"name": "fine_tune_model", "description": "Fine-tune a model"},
            {"name": "export_model_weights", "description": "Export model weights"},
            {"name": "list_models", "description": "List available models"},
            {"name": "create_embedding", "description": "Generate embeddings"},
        ],
    },
]


def parse_policy_yaml(content: str) -> dict[str, Any]:
    """Parse a YAML policy string and return a normalized dict.

    Supports both the PolicyEngine format (rules.allow / rules.deny) and the
    legacy flat format (top-level allow / deny) for backwards compatibility.
    """
    data = yaml.safe_load(content) or {}
    if not isinstance(data, dict):
        return {"agent": "*", "allow": [], "deny": [], "default": "allow"}
    rules = data.get("rules") or {}
    if not isinstance(rules, dict):
        rules = {}
    return {
        "agent": str(data.get("agent", "*")),
        "allow": list(rules.get("allow") or data.get("allow") or []),
        "deny": list(rules.get("deny") or data.get("deny") or []),
        "default": str(data.get("default", "allow")),
    }


def apply_deny_precedence(allow: list[str], deny: list[str]) -> tuple[list[str], list[str]]:
    """Return (allow, deny) with any tool in deny removed from allow."""
    deny_set = set(deny)
    return [t for t in allow if t not in deny_set], deny


def load_existing_policy() -> dict[str, Any]:
    """Load ~/.interceptr/policy.yaml; return a normalized state dict."""
    if not POLICY_FILE.exists():
        return {"agent": "*", "allow": [], "deny": [], "default": "allow"}
    try:
        policy = parse_policy_yaml(POLICY_FILE.read_text())
        policy["allow"], policy["deny"] = apply_deny_precedence(
            policy["allow"], policy["deny"]
        )
        return policy
    except Exception:
        return {
            "agent": "*",
            "allow": [],
            "deny": [],
            "default": "allow",
            "_parse_error": True,
        }


def build_yaml_content(
    agent: str, allow: list[str], deny: list[str], default: str
) -> str:
    """Build a YAML string in PolicyEngine format (version + rules nesting)."""
    data: dict[str, Any] = {
        "version": "1.0",
        "agent": agent or "*",
        "rules": {
            "allow": allow,
            "deny": deny,
        },
        "default": default,
    }
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


CSS = """
Screen {
    background: #1a1a1a;
}

Header {
    background: #1a1a1a;
    color: #a8e63d;
}

Footer {
    background: #111111;
    color: #888888;
}

#editor-scroll {
    height: 1fr;
}

#config-row {
    height: auto;
    padding: 1 2;
    background: #222222;
    border-bottom: solid #444444;
    align: left middle;
}

#agent-label, #default-label {
    width: auto;
    padding: 0 1;
    content-align: left middle;
}

#agent-input {
    width: 24;
    margin: 0 1;
}

#default-radio {
    width: auto;
    height: auto;
    margin: 0 1;
    background: transparent;
}

.tool-row {
    height: auto;
    padding: 0 2;
    align: left middle;
}

.tool-row:hover {
    background: #252525;
}

.allow-box {
    width: 14;
    color: #4ec94e;
}

.deny-box {
    width: 12;
    color: #e64e4e;
}

.tool-info {
    width: 1fr;
    color: #aaaaaa;
    padding: 0 2;
    content-align: left middle;
}

Collapsible {
    background: #1e1e1e;
    margin: 0;
    padding: 0;
}
"""


class PolicyEditorApp(App[None]):
    """Full-screen TUI for creating and editing the Interceptr policy."""

    TITLE = "interceptr policy editor"
    CSS = CSS
    BINDINGS = [
        Binding("s", "save", "Save & Apply"),
        Binding("r", "reset", "Reset"),
        Binding("q", "quit", "Quit without saving"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._initial_policy = load_existing_policy()

    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer(id="editor-scroll"):
            with Horizontal(id="config-row"):
                yield Label("Agent: ", id="agent-label")
                yield Input(
                    value=self._initial_policy.get("agent", "*"),
                    id="agent-input",
                    placeholder="*",
                )
                yield Label("  Default:", id="default-label")
                with RadioSet(id="default-radio"):
                    yield RadioButton("allow", id="radio-allow")
                    yield RadioButton("deny", id="radio-deny")
            for i, cat in enumerate(TOOL_CATALOG):
                with Collapsible(title=cat["category"], collapsed=(i > 0)):
                    for tool in cat["tools"]:
                        with Horizontal(classes="tool-row"):
                            yield Checkbox(
                                "ALLOW",
                                id=f"allow__{tool['name']}",
                                classes="allow-box",
                            )
                            yield Checkbox(
                                "DENY",
                                id=f"deny__{tool['name']}",
                                classes="deny-box",
                            )
                            yield Static(
                                f"{tool['name']:<28}  {tool['description']}",
                                classes="tool-info",
                            )
        yield Footer()

    def on_mount(self) -> None:
        policy = self._initial_policy

        if policy.get("_parse_error"):
            self.notify(
                "Could not parse existing policy.yaml — starting fresh",
                severity="warning",
                timeout=5,
            )

        # Set default radio button (allow is selected by default; only change if deny)
        if policy.get("default") == "deny":
            try:
                self.query_one("#radio-deny", RadioButton).value = True
            except Exception:
                pass

        # Pre-check allow first, then deny (deny wins via on_checkbox_changed)
        for tool in policy.get("allow", []):
            try:
                self.query_one(f"#allow__{tool}", Checkbox).value = True
            except Exception:
                pass
        for tool in policy.get("deny", []):
            try:
                self.query_one(f"#deny__{tool}", Checkbox).value = True
            except Exception:
                pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Enforce mutual exclusivity: checking ALLOW unchecks DENY and vice versa."""
        if not event.value:
            return  # only act on a box being checked
        cid = event.checkbox.id or ""
        if cid.startswith("allow__"):
            tool = cid[7:]
            try:
                self.query_one(f"#deny__{tool}", Checkbox).value = False
            except Exception:
                pass
        elif cid.startswith("deny__"):
            tool = cid[6:]
            try:
                self.query_one(f"#allow__{tool}", Checkbox).value = False
            except Exception:
                pass

    def _collect_state(self) -> tuple[str, list[str], list[str], str]:
        """Return (agent, allow_list, deny_list, default) from current widget state."""
        agent = self.query_one("#agent-input", Input).value.strip() or "*"
        deny_radio = self.query_one("#radio-deny", RadioButton)
        default = "deny" if deny_radio.value else "allow"
        allow: list[str] = []
        deny: list[str] = []
        for checkbox in self.query(Checkbox):
            cid = checkbox.id or ""
            if cid.startswith("allow__") and checkbox.value:
                allow.append(cid[7:])
            elif cid.startswith("deny__") and checkbox.value:
                deny.append(cid[6:])
        return agent, allow, deny, default

    def action_save(self) -> None:
        """Write policy.yaml and reload the server if it's running."""
        agent, allow, deny, default = self._collect_state()
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        POLICY_FILE.write_text(build_yaml_content(agent, allow, deny, default))
        server_up = False
        try:
            resp = httpx.post(_RELOAD_URL, timeout=3.0)
            server_up = resp.status_code == 200
        except Exception:
            pass
        msg = (
            "Policy saved and reloaded"
            if server_up
            else "Policy saved — start Interceptr to apply"
        )
        self.notify(msg, severity="information", timeout=4)
        self.set_timer(1.5, self.exit)

    def action_reset(self) -> None:
        """Uncheck all tools and reset agent/default to defaults."""
        for checkbox in self.query(Checkbox):
            checkbox.value = False
        self.query_one("#agent-input", Input).value = "*"
        try:
            self.query_one("#radio-allow", RadioButton).value = True
        except Exception:
            pass

    def action_quit(self) -> None:
        """Exit without saving."""
        self.exit()
