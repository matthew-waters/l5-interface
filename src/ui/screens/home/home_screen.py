"""Home dashboard screen."""

from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer
from textual.binding import Binding

from src.ui.widgets.carbon_snapshot import CarbonSnapshot
from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.system_timeline import SystemTimeline
from src.ui.widgets.workload_card import UpcomingWorkloads

from textual import log

class HomeScreen(Screen[None]):
    """Status dashboard + navigation hub."""
    HEADER_TITLE = "Home"

    BINDINGS = [
        Binding("w", "go_workloads", "Workloads"),
        Binding("c", "go_create", "Create"),
        Binding("t", "go_timeline", "Timeline"),
        Binding("e", "go_execution", "Execution"),
        Binding("r", "go_credentials", "Credentials"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        with Container(id="home_grid"):
            yield UpcomingWorkloads(classes="card")
            yield CarbonSnapshot(classes="card")
            yield SystemTimeline(classes="card")
        yield Footer(show_command_palette=False)

    def action_go_workloads(self) -> None:
        self.app.switch_screen("workloads")

    def action_go_create(self) -> None:
        self.app.switch_screen("create_workload")

    def action_go_timeline(self) -> None:
        self.app.switch_screen("timeline")

    def action_go_execution(self) -> None:
        self.app.switch_screen("execution")

    def action_go_credentials(self) -> None:
        self.app.switch_screen("credentials")
