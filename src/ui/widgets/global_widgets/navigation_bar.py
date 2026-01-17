"""Navigation/actions bar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import HorizontalScroll
from textual.screen import Screen
from textual.widgets import Button, Static


class NavigationBar(Static):
    """Bottom navigation bar (buttons + key hints)."""

    _BUTTON_TO_SCREEN: dict[str, str] = {
        "nav_home": "home",
        "nav_workloads": "workloads",
        "nav_timeline": "timeline",
        "nav_execution": "execution",
        "nav_credentials": "credentials",
        "nav_create": "create_workload",
    }

    DEFAULT_CSS = """
    NavigationBar {
        dock: bottom;
        width: 100%;
    }

    NavigationBar HorizontalScroll {
        width: 100%;
        height: auto;
        align: center middle;
    }

    NavigationBar Button {
        height: auto;
    }

    NavigationBar Button.active-page {
        background: $primary-muted;
        border: block $primary-muted;
        color: $text-primary;
        text-style: bold;
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

    def on_mount(self) -> None:
        self.update_active_page()

    def _installed_screen_key_for(self, screen: Screen | None) -> str | None:
        """Return the installed screen key (e.g. 'home') for a screen instance."""
        if screen is None:
            return None

        installed = getattr(self.app, "_installed_screens", None)
        if not isinstance(installed, dict):
            return None

        for key, value in installed.items():
            # Value may be a callable factory in Textual, but in this app it's instances.
            if value is screen:
                return str(key)
        return None

    def update_active_page(self) -> None:
        """Highlight the button for the currently active screen."""
        # `Screen.name` is the widget name; it is often None. We need the installed key
        # used by `install_screen(..., name="home")`.
        current_key = self._installed_screen_key_for(getattr(self.app, "screen", None))
        if not current_key:
            return

        for button_id, screen_name in self._BUTTON_TO_SCREEN.items():
            try:
                button = self.query_one(f"#{button_id}", Button)
            except Exception:
                continue
            button.set_class(current_key == screen_name, "active-page")

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
