"""Credentials screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static, TextArea

from src.storage.config_store import CredentialsConfig
from src.ui.widgets.header.global_header import GlobalHeader


class CredentialsScreen(Screen[None]):
    """Collect and persist credentials for external integrations."""

    BINDINGS = [
        ("s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Credentials", classes="section_title")
        yield Static(
            "Stored locally in data/configs/credentials.json (gitignored).",
            classes="muted",
        )

        with VerticalScroll(id="credentials_scroll"):
            # Spot Fleet
            with Container(classes="card"):
                yield Static("Spot Fleet", classes="section_title")
                yield Static("API key", classes="muted")
                yield Input(
                    id="spot_fleet_api_key",
                    placeholder="Enter Spot Fleet API key",
                    password=True,
                )

            # Carbon Intensity
            with Container(classes="card"):
                yield Static("Carbon Intensity", classes="section_title")
                yield Static(
                    "API keys (one per line). The app will support multiple providers later.",
                    classes="muted",
                )
                yield TextArea(
                    id="carbon_intensity_api_keys",
                    text="",
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

    def on_mount(self) -> None:
        self._load_into_form()

    def _load_into_form(self) -> None:
        cfg = getattr(self.app, "storage").config.load_credentials()
        self.query_one("#spot_fleet_api_key", Input).value = cfg.spot_fleet_api_key or ""

        keys_text = "\n".join(k for k in cfg.carbon_intensity_api_keys if k)
        self.query_one("#carbon_intensity_api_keys", TextArea).text = keys_text

    def _read_from_form(self) -> CredentialsConfig:
        spot_key = self.query_one("#spot_fleet_api_key", Input).value.strip()

        keys_raw = self.query_one("#carbon_intensity_api_keys", TextArea).text
        carbon_keys = [line.strip() for line in keys_raw.splitlines() if line.strip()]

        return CredentialsConfig(
            spot_fleet_api_key=spot_key,
            carbon_intensity_api_keys=carbon_keys,
            aws={},
        )

    def action_save(self) -> None:
        self._save()

    def _save(self) -> None:
        cfg = self._read_from_form()
        getattr(self.app, "storage").config.save_credentials(cfg)
        notify = getattr(self.app, "notify", None)
        if callable(notify):
            notify("Credentials saved.", severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_btn":
            self._save()
        elif event.button.id == "back_btn":
            self.app.switch_screen("home")

