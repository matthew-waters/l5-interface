"""Data models for Spot Fleet API responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dateutil.parser import isoparse


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO8601 datetime string to datetime object."""
    if value is None:
        return None
    return isoparse(value)


@dataclass(frozen=True, slots=True)
class RequestGroup:
    """A request group (fleet) configuration."""

    id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RequestGroup:
        """Create RequestGroup from API response dictionary."""
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
        )


@dataclass(frozen=True, slots=True)
class InstancePool:
    """An instance pool (instance type + region + AZ combination)."""

    id: int
    instance_type: str
    region: str
    az: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstancePool:
        """Create InstancePool from API response dictionary."""
        return cls(
            id=int(data["id"]),
            instance_type=str(data["instance_type"]),
            region=str(data["region"]),
            az=str(data["az"]),
        )


@dataclass(frozen=True, slots=True)
class PlacementScore:
    """A placement score measurement for a request group."""

    measured_at: datetime
    score: float
    availability_zone: str
    target_capacity: int
    request_group_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlacementScore:
        """Create PlacementScore from API response dictionary."""
        return cls(
            measured_at=_parse_iso_datetime(data["measured_at"]),
            score=float(data["score"]),
            availability_zone=str(data["availability_zone"]),
            target_capacity=int(data["target_capacity"]),
            request_group_id=int(data["request_group_id"]),
        )


@dataclass(frozen=True, slots=True)
class SpotPrice:
    """A spot price measurement for an instance pool."""

    measured_at: datetime
    price: float
    pool_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpotPrice:
        """Create SpotPrice from API response dictionary."""
        return cls(
            measured_at=_parse_iso_datetime(data["measured_at"]),
            price=float(data["price"]),
            pool_id=int(data["pool_id"]),
        )


@dataclass(frozen=True, slots=True)
class InterruptionRate:
    """An interruption rate measurement for an instance pool."""

    measured_at: datetime
    rate: float
    pool_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterruptionRate:
        """Create InterruptionRate from API response dictionary."""
        return cls(
            measured_at=_parse_iso_datetime(data["measured_at"]),
            rate=float(data["rate"]),
            pool_id=int(data["pool_id"]),
        )
