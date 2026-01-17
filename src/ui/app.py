"""Main Textual App class."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from src.storage.storage_manager import StorageManager
from src.ui.messages import CredentialsChanged
from src.ui.screens.credentials.credentials_screen import CredentialsScreen
from src.ui.screens.create_workload.create_workload_screen import CreateWorkloadScreen
from src.ui.screens.execution_overview.execution_overview_screen import ExecutionOverviewScreen
from src.ui.screens.home.home_screen import HomeScreen
from src.ui.screens.global_timeline.timeline_screen import TimelineScreen
from src.ui.screens.list_workloads.workloads_list_screen import WorkloadsListScreen
from src.ui.widgets.header.global_header import GlobalHeader


class L5InterfaceApp(App[None]):
    """Textual app shell + global navigation."""

    TITLE = "L5 Scheduler Interface"
    SUB_TITLE = "Carbon-, application-, and availability-aware scheduling"

    CSS_PATH = "themes/default.tcss"

    BINDINGS = [
        Binding("h", "go_home", "Home"),
        Binding("w", "go_workloads", "Workloads"),
        Binding("c", "go_create", "Create"),
        Binding("t", "go_timeline", "Timeline"),
        Binding("e", "go_execution", "Execution"),
        Binding("r", "go_credentials", "Credentials"),
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        self.storage = StorageManager(repo_root / "data")

        self.install_screen(HomeScreen(), name="home")
        self.install_screen(CreateWorkloadScreen(), name="create_workload")
        self.install_screen(CredentialsScreen(), name="credentials")
        self.install_screen(WorkloadsListScreen(), name="workloads")
        self.install_screen(TimelineScreen(), name="timeline")
        self.install_screen(ExecutionOverviewScreen(), name="execution")
        self.push_screen("home")

    def compose(self) -> ComposeResult:
        # No widgets at app level - all widgets are in screens
        yield from ()

    def action_go_home(self) -> None:
        self.switch_screen("home")

    def action_go_workloads(self) -> None:
        self.switch_screen("workloads")

    def action_go_create(self) -> None:
        self.switch_screen("create_workload")
        screen = self.get_screen("create_workload")
        start = getattr(screen, "start_new_draft", None)
        if callable(start):
            start()

    def action_go_timeline(self) -> None:
        self.switch_screen("timeline")

    def action_go_execution(self) -> None:
        self.switch_screen("execution")

    def action_go_credentials(self) -> None:
        self.switch_screen("credentials")

    def on_credentials_changed(self, message: CredentialsChanged) -> None:
        """Refresh any mounted headers immediately after credentials are saved."""
        # Textual queries are CSS-selector based; query for the widget type name.
        # We query the active screen since that's where the mounted GlobalHeader lives.
        for header in self.screen.query("GlobalHeader"):
            # `header` will be a GlobalHeader instance due to the selector.
            header._refresh_freshness_from_api()
            header.update_freshness()


