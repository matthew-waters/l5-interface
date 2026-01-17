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
        height: auto;
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
            yield Button("(h) Home", id="nav_home", variant="default")
            yield Button("(w) Workloads", id="nav_workloads", variant="default")
            yield Button("(t) Timeline", id="nav_timeline", variant="default")
            yield Button("(e) Execution", id="nav_execution", variant="default")
            yield Button("(r) Credentials", id="nav_credentials", variant="default")
            yield Button("(c) Create", id="nav_create", variant="primary")
            yield Button("(q) Quit", id="nav_quit", variant="error")

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
            screen = self.app.get_screen("create_workload")
            start = getattr(screen, "start_new_draft", None)
            if callable(start):
                start()
        elif button_id == "nav_quit":
            self.app.exit()

