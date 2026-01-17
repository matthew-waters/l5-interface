"""Configuration persistence (JSON files in `data/configs/`).

We keep credentials/config local to the machine and store them under `data/`,
which is gitignored by default for configs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class CredentialsConfig:
    """User-provided credentials for external services (stored locally)."""

    spot_fleet_api_key: str = ""
    watttime_username: str = ""
    watttime_password: str = ""

    # Placeholder for future AWS-linked credentials / metadata.
    aws: dict[str, str] = field(default_factory=dict)


class ConfigStore:
    """Store for local configuration JSON files."""

    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir = configs_dir
        self.configs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def credentials_path(self) -> Path:
        return self.configs_dir / "credentials.json"

    def load_credentials(self) -> CredentialsConfig:
        """Load credentials config from disk (or return defaults)."""
        path = self.credentials_path
        if not path.exists():
            return CredentialsConfig()

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return CredentialsConfig()

        return CredentialsConfig(
            spot_fleet_api_key=str(data.get("spot_fleet_api_key", "") or ""),
            watttime_username=str(data.get("watttime_username", "") or ""),
            watttime_password=str(data.get("watttime_password", "") or ""),
            aws=dict(data.get("aws", {}) or {}),
        )

    def save_credentials(self, config: CredentialsConfig) -> None:
        """Save credentials config to disk."""
        path = self.credentials_path
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=2, sort_keys=True)

