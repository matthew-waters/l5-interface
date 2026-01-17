"""Global system timeline screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.global_widgets.navigation_bar import NavigationBar


class TimelineScreen(Screen[None]):
    """Full system timeline view (placeholder)."""
    HEADER_TITLE = "Timeline"

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Timeline (placeholder)", classes="section_title")
        yield Static("This screen will show a larger planning horizon.", classes="muted")
        yield NavigationBar(id="global_nav")

