"""Spot Fleet data access module."""

from src.backend.data.fleet.api_client import SpotFleetAPIClient
from src.backend.data.fleet.models import (
    InstancePool,
    InterruptionRate,
    PlacementScore,
    RequestGroup,
    SpotPrice,
)
from src.backend.data.fleet.service import SpotFleetDataService

__all__ = [
    "SpotFleetAPIClient",
    "SpotFleetDataService",
    "RequestGroup",
    "InstancePool",
    "PlacementScore",
    "SpotPrice",
    "InterruptionRate",
]
