"""Navigation/actions bar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import HorizontalScroll
from textual.widgets import Button, Static


class NavigationBar(Static):
    """Bottom navigation bar (buttons + key hints)."""

    DEFAULT_CSS = """
    NavigationBar {
        width: 100%;
    }

    NavigationBar HorizontalScroll {
        width: 100%;
        height: auto;
        align: center middle;
    }

    NavigationBar Button {
        margin: 0 1;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with HorizontalScroll():
            yield Button("(h) Home", id="nav_home", variant="default", flat=True)
            yield Button("(w) Workloads", id="nav_workloads", variant="default", flat=True)
            yield Button("(t) Timeline", id="nav_timeline", variant="default", flat=True)
            yield Button("(e) Execution", id="nav_execution", variant="default", flat=True)
            yield Button("(r) Credentials", id="nav_credentials", variant="default", flat=True)
            yield Button("(c) Create", id="nav_create", variant="primary", flat=True)
            yield Button("(q) Quit", id="nav_quit", variant="error", flat=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "nav_home":
            self.app.switch_screen("home")
        elif button_id == "nav_workloads":
            self.app.switch_screen("workloads")
        elif button_id == "nav_timeline":
            self.app.switch_screen("timeline")
        elif button_id == "nav_execution":
            self.app.switch_screen("execution")
        elif button_id == "nav_credentials":
            self.app.switch_screen("credentials")
        elif button_id == "nav_create":
            # Always route to the Create Workload wizard.
            self.app.switch_screen("create_workload")
        elif button_id == "nav_quit":
            self.app.exit()

