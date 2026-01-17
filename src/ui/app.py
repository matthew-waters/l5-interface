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


class L5InterfaceApp(App[None]):
    """Textual app shell + global navigation."""

    TITLE = "L5 Scheduler Interface"
    SUB_TITLE = "Carbon-, application-, and availability-aware scheduling"

    CSS_PATH = "themes/default.tcss"

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
        yield from ()

    def on_credentials_changed(self, message: CredentialsChanged) -> None:
        """Refresh any mounted headers immediately after credentials are saved."""
        # Textual queries are CSS-selector based; query for the widget type name.
        # We query the active screen since that's where the mounted GlobalHeader lives.
        for header in self.screen.query("GlobalHeader"):
            # `header` will be a GlobalHeader instance due to the selector.
            header._refresh_freshness_from_api()
            header.update_freshness()


