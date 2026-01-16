"""Application settings and configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.config.defaults import DEFAULT_SPOT_FLEET_API_BASE_URL
from src.storage.config_store import ConfigStore


def get_spot_fleet_api_base_url() -> str:
    """Get the Spot Fleet API base URL from config or environment.

    Checks environment variable SPOT_FLEET_API_BASE_URL first,
    then falls back to default.

    Returns:
        Base URL string for the Spot Fleet API
    """
    return os.getenv("SPOT_FLEET_API_BASE_URL", DEFAULT_SPOT_FLEET_API_BASE_URL)


def get_spot_fleet_api_key() -> str | None:
    """Get the Spot Fleet API key from config

    Returns:
        API key string, or None if not configured.
    """

    try:
        repo_root = Path(__file__).resolve().parents[2]
        store = ConfigStore(repo_root / "data" / "configs")
        creds = store.load_credentials()
        return creds.spot_fleet_api_key or None
    except Exception:
        return None