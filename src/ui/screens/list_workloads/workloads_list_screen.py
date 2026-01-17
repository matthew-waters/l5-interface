"""Workloads list screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.binding import Binding

from src.ui.widgets.global_widgets.global_header import GlobalHeader


class WorkloadsListScreen(Screen[None]):
    """Unified list for drafts/scheduled/executing/completed workloads."""
    HEADER_TITLE = "Workloads"

    SCREEN_CONTROLS = [
    ]

    NAVIGATION_CONTROLS = [
        Binding("h", "go_home", "Home"),
        Binding("q", "quit", "Quit"),
    ]  

    def compose(self) -> ComposeResult:
        yield GlobalHeader()

        yield Footer()

    def action_go_home(self) -> None:
            self.app.switch_screen("home")
