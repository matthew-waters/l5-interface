"""Execution overview screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.binding import Binding

from src.ui.widgets.global_widgets.global_header import GlobalHeader


class ExecutionOverviewScreen(Screen[None]):
    """Execution overview for a selected workload (placeholder)."""
    HEADER_TITLE = "Execution"

    SCREEN_CONTROLS = [
    ]

    NAVIGATION_CONTROLS = [
        Binding("h", "go_home", "Home"),
        Binding("q", "quit", "Quit"),
    ]        

    BINDINGS = SCREEN_CONTROLS + NAVIGATION_CONTROLS

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Execution overview (placeholder)", classes="section_title")
        yield Static("This screen will show logs, interruptions, and plan details.", classes="muted")
        yield Footer()

    def action_go_home(self) -> None:
        self.app.switch_screen("home")