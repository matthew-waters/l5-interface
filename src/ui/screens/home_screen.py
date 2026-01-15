"""Home dashboard screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen

from src.ui.widgets.carbon_snapshot import CarbonSnapshot
from src.ui.widgets.global_header import GlobalHeader
from src.ui.widgets.navigation_bar import NavigationBar
from src.ui.widgets.system_timeline import SystemTimeline
from src.ui.widgets.workload_card import UpcomingWorkloads


class HomeScreen(Screen[None]):
    """Status dashboard + navigation hub."""

    BINDINGS = [
        ("c", "create_workload", "Create"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        with Container(id="home_grid"):
            yield UpcomingWorkloads(classes="card")
            yield CarbonSnapshot(classes="card")
            yield SystemTimeline(classes="card")
        yield NavigationBar(id="home_nav")

    def action_create_workload(self) -> None:
        getattr(self.app, "storage").workloads.create_draft("New workload")
        self.app.switch_screen("workloads")

