# policy.py — Policy information panel widget for the Interceptr TUI
from __future__ import annotations

from textual.widget import Widget
from textual.binding import Binding
from rich.text import Text

from interceptr.client import InterceptrClient

COL_WIDTH = 28


class PolicyWidget(Widget):
    """Shows current policy: agent, allow list, deny list, and default action."""

    DEFAULT_CSS = """
    PolicyWidget {
        height: 1fr;
        padding: 1 2;
        background: #1e1e1e;
        color: #cccccc;
        overflow-y: auto;
    }
    """

    BINDINGS = [Binding("r", "refresh", "Refresh")]

    def __init__(self) -> None:
        super().__init__()
        self._client = InterceptrClient()
        self._data: dict = {}
        self._error: str = ""

    def on_mount(self) -> None:
        self.set_timer(0.5, self.refresh_data)
        self.set_interval(3, self.refresh_data)

    def refresh_data(self) -> None:
        try:
            self._data = self._client.get_policy()
            self._error = ""
        except Exception as exc:
            self._data = {}
            self._error = str(exc)
        self.refresh()

    def action_refresh(self) -> None:
        self.refresh_data()

    def _is_loaded(self) -> bool:
        return "detail" not in self._data and (
            "agent" in self._data or "allow" in self._data or "deny" in self._data
        )

    def render(self) -> Text:
        text = Text()

        if self._error:
            text.append("⚠ Could not load policy\n", style="red")
            text.append(self._error, style="dim red")
            return text

        if not self._is_loaded():
            text.append("No policy loaded\n", style="yellow")
            text.append("All tool calls are ALLOWED by default.", style="dim")
            return text

        agent = self._data.get("agent", "*")
        allow = self._data.get("allow", [])
        deny = self._data.get("deny", [])
        default = self._data.get("default", "allow")

        # Header
        text.append("Policy: ", style="bold white")
        text.append(agent + "\n", style="bold white")

        default_color = "bold green" if default == "allow" else "bold red"
        text.append("Default: ", style="bold")
        text.append(default.upper() + "\n\n", style=default_color)

        if not allow and not deny:
            text.append("No rules defined", style="dim")
            return text

        # Column headers
        text.append("✅ ALLOWED".ljust(COL_WIDTH), style="bold green")
        text.append("  🚫 BLOCKED\n", style="bold red")
        text.append("─" * (COL_WIDTH * 2 + 2) + "\n", style="dim")

        # Rows
        row_count = max(len(allow), len(deny))
        for i in range(row_count):
            left = allow[i] if i < len(allow) else ""
            right = deny[i] if i < len(deny) else ""
            text.append(left.ljust(COL_WIDTH), style="green")
            text.append("  ")
            text.append(right + "\n", style="red")

        # Hint when deny-by-default with no allow list
        if default == "deny" and not allow:
            text.append("\nAll tool calls blocked unless explicitly allowed", style="dim")

        return text
