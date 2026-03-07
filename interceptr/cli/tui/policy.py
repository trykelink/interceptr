# policy.py — Policy information panel widget for the Interceptr TUI
from __future__ import annotations

from textual.widget import Widget
from textual.binding import Binding
from rich.text import Text

from interceptr.client import InterceptrClient


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
        self.refresh_data()
        self.set_interval(10, self.refresh_data)

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

    def render(self) -> Text:
        text = Text()

        if self._error:
            text.append("⚠ Could not load policy\n", style="red")
            text.append(self._error, style="dim red")
            return text

        loaded = self._data.get("loaded", False)
        if not loaded:
            text.append("No policy loaded\n", style="yellow")
            text.append("All tool calls are ALLOWED by default.", style="dim")
            return text

        agent = self._data.get("agent", "*")
        allow = self._data.get("allow", [])
        deny = self._data.get("deny", [])
        default = self._data.get("default", "allow")

        text.append("Agent: ", style="bold")
        text.append(agent + "\n\n")

        text.append("Allow list:\n", style="bold green")
        if allow:
            for t in allow:
                text.append(f"  ✓ {t}\n", style="green")
        else:
            text.append("  (none)\n", style="dim")

        text.append("\nDeny list:\n", style="bold red")
        if deny:
            for t in deny:
                text.append(f"  ✗ {t}\n", style="red")
        else:
            text.append("  (none)\n", style="dim")

        text.append("\nDefault: ", style="bold")
        color = "green" if default == "allow" else "red"
        text.append(default, style=color)

        return text
