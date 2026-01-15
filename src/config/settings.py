"""Application settings and configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

from src.config.defaults import DEFAULT_SPOT_FLEET_API_BASE_URL, DEFAULT_SPOT_FLEET_API_KEY


def get_spot_fleet_api_base_url() -> str:
    """Get the Spot Fleet API base URL from config or environment.

    Checks environment variable SPOT_FLEET_API_BASE_URL first,
    then falls back to default.

    Returns:
        Base URL string for the Spot Fleet API
    """
    return os.getenv("SPOT_FLEET_API_BASE_URL", DEFAULT_SPOT_FLEET_API_BASE_URL)


def get_spot_fleet_api_key() -> str | None:
    """Get the Spot Fleet API key from config or environment.

    Checks environment variable SPOT_FLEET_API_KEY first, then falls back to default.

    Returns:
        API key string, or None if not configured.
    """
    return os.getenv("SPOT_FLEET_API_KEY", DEFAULT_SPOT_FLEET_API_KEY)