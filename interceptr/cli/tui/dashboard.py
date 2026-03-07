# dashboard.py — Main dashboard widget showing server status and summary stats
from __future__ import annotations

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

from interceptr.client import InterceptrClient


class DashboardWidget(Widget):
    """Shows server status, total logs, blocked and allowed counts."""

    DEFAULT_CSS = """
    DashboardWidget {
        height: auto;
        padding: 1 2;
        border: solid #a8e63d;
        background: #1e1e1e;
        color: #cccccc;
    }
    """

    _status: reactive[str] = reactive("unknown")
    _allowed: reactive[int] = reactive(0)
    _blocked: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._client = InterceptrClient()

    def on_mount(self) -> None:
        self.refresh_data()
        self.set_interval(5, self.refresh_data)

    def refresh_data(self) -> None:
        try:
            health = self._client.health()
            self._status = health.get("status", "ok")
            logs = self._client.get_logs(limit=200)
            self._allowed = sum(1 for l in logs if l.get("status") == "ALLOWED")
            self._blocked = sum(1 for l in logs if l.get("status") == "BLOCKED")
        except Exception:
            self._status = "unreachable"

        self.refresh()

    def render(self) -> Text:
        color = "green" if self._status not in ("unreachable", "unknown") else "red"
        icon = "●" if color == "green" else "○"
        text = Text()
        text.append(f"{icon} Server: ", style="bold")
        text.append(self._status + "\n", style=color)
        text.append(f"Allowed: ", style="bold")
        text.append(str(self._allowed) + "\n", style="green")
        text.append(f"Blocked: ", style="bold")
        text.append(str(self._blocked) + "\n", style="red")
        return text
