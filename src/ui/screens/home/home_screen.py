"""Home dashboard screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen

from src.ui.widgets.carbon_snapshot import CarbonSnapshot
from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.global_widgets.navigation_bar import NavigationBar
from src.ui.widgets.system_timeline import SystemTimeline
from src.ui.widgets.workload_card import UpcomingWorkloads

from textual import log

class HomeScreen(Screen[None]):
    """Status dashboard + navigation hub."""
    HEADER_TITLE = "Home"

    BINDINGS = [
        ("c", "create_workload", "Create"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        with Container(id="home_grid"):
            yield UpcomingWorkloads(classes="card")
            yield CarbonSnapshot(classes="card")
            yield SystemTimeline(classes="card")
        yield NavigationBar(id="global_nav")

    def action_create_workload(self) -> None:
        self.app.switch_screen("create_workload")

