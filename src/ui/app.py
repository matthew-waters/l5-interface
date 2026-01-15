"""Main Textual App class."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from src.storage.storage_manager import StorageManager
from src.ui.screens.execution_overview_screen import ExecutionOverviewScreen
from src.ui.screens.home_screen import HomeScreen
from src.ui.screens.timeline_screen import TimelineScreen
from src.ui.screens.workloads_list_screen import WorkloadsListScreen


class L5InterfaceApp(App[None]):
    """Textual app shell + global navigation."""

    TITLE = "L5 Scheduler Interface"
    SUB_TITLE = "Carbon-, application-, and availability-aware scheduling"

    CSS_PATH = "themes/default.tcss"

    BINDINGS = [
        Binding("h", "go_home", "Home"),
        Binding("w", "go_workloads", "Workloads"),
        Binding("t", "go_timeline", "Timeline"),
        Binding("e", "go_execution", "Execution"),
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        self.storage = StorageManager(repo_root / "data")

        self.install_screen(HomeScreen(), name="home")
        self.install_screen(WorkloadsListScreen(), name="workloads")
        self.install_screen(TimelineScreen(), name="timeline")
        self.install_screen(ExecutionOverviewScreen(), name="execution")
        self.push_screen("home")

    def compose(self) -> ComposeResult:
        yield Footer()

    def action_go_home(self) -> None:
        self.switch_screen("home")

    def action_go_workloads(self) -> None:
        self.switch_screen("workloads")

    def action_go_timeline(self) -> None:
        self.switch_screen("timeline")

    def action_go_execution(self) -> None:
        self.switch_screen("execution")


