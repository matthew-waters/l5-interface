"""Credentials screen."""

from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from src.storage.config_store import CredentialsConfig
from src.ui.messages import CredentialsChanged
from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.global_widgets.navigation_bar import NavigationBar


class CredentialsScreen(Screen[None]):
    """Collect and persist credentials for external integrations."""
    HEADER_TITLE = "Credentials"

    DEFAULT_CSS = """
    /* Ensure the scroll area takes the remaining space under the header/title. */
    #credentials_scroll {
        height: 1fr;
    }

    /* Keep cards compact so inputs fit in smaller terminals. */
    #credentials_scroll .card {
        height: auto;
        padding: 1 1;
    }

    #credentials_scroll Input {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()


        with VerticalScroll(id="credentials_scroll"):
            # Spot Fleet
            with Container(classes="card"):
                yield Static("Spot Fleet Data API Key", classes="section_title")
                yield Input(
                    id="spot_fleet_api_key",
                    placeholder="Enter Spot Fleet API key",
                    password=True,
                )

            # WattTime (Carbon Intensity)
            with Container(classes="card"):
                yield Static("WattTime", classes="section_title")
                yield Static("Username", classes="muted")
                yield Input(
                    id="watttime_username",
                    placeholder="Enter WattTime username",
                )
                yield Static("Password", classes="muted")
                yield Input(
                    id="watttime_password",
                    placeholder="Enter WattTime password",
                    password=True,
                )

            # AWS (placeholder)
            with Container(classes="card"):
                yield Static("AWS Account Linking", classes="section_title")
                yield Static(
                    "Coming soon: link AWS account details/credentials here.",
                    classes="muted",
                )

            with Horizontal(classes="card"):
                yield Button("(s) Save", id="save_btn", variant="primary")
                yield Button("Back to Home", id="back_btn")

        yield NavigationBar(id="global_nav")

    def on_mount(self) -> None:
        self._load_into_form()
        # Make scrolling work immediately on smaller terminals.
        self.query_one("#credentials_scroll", VerticalScroll).focus()

    def _load_into_form(self) -> None:
        cfg = getattr(self.app, "storage").config.load_credentials()
        self.query_one("#spot_fleet_api_key", Input).value = cfg.spot_fleet_api_key or ""
        self.query_one("#watttime_username", Input).value = cfg.watttime_username or ""
        self.query_one("#watttime_password", Input).value = cfg.watttime_password or ""

    def _read_from_form(self) -> CredentialsConfig:
        spot_key = self.query_one("#spot_fleet_api_key", Input).value.strip()
        watttime_username = self.query_one("#watttime_username", Input).value.strip()
        watttime_password = self.query_one("#watttime_password", Input).value

        return CredentialsConfig(
            spot_fleet_api_key=spot_key,
            watttime_username=watttime_username,
            watttime_password=watttime_password,
            aws={},
        )

    def action_save(self) -> None:
        self._save()

    def _save(self) -> None:
        cfg = self._read_from_form()
        getattr(self.app, "storage").config.save_credentials(cfg)

        # Trigger immediate refresh of header freshness indicators (e.g., Spot Fleet API key).
        self.app.post_message(CredentialsChanged())

        notify = getattr(self.app, "notify", None)
        if callable(notify):
            notify("Credentials saved.", severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_btn":
            self._save()
        elif event.button.id == "back_btn":
            self.app.switch_screen("home")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        # Ensure nav highlight is correct immediately when this screen becomes active.
        try:
            self.query_one(NavigationBar).update_active_page()
        except Exception:
            pass
