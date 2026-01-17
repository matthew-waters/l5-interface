"""Data models for Spot Fleet API responses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dateutil.parser import isoparse


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO8601 datetime string to datetime object."""
    if value is None:
        return None
    return isoparse(value)


def _parse_jsonish_list_str(value: Any) -> list[Any] | None:
    """Parse a JSON list or a stringified JSON list into a Python list."""
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, list) else None
        except Exception:
            return None
    return None


def _parse_jsonish_dict_str(value: Any) -> dict[str, Any] | None:
    """Parse a JSON dict or a stringified JSON dict into a Python dict."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
    return None


def _parse_datetime_flexible(value: Any) -> datetime | None:
    """Parse ISO8601-ish timestamps, tolerating non-ISO formats from APIs."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return isoparse(str(value))
    except Exception:
        try:
            from dateutil.parser import parse as dtparse

            return dtparse(str(value))
        except Exception:
            return None


@dataclass(frozen=True, slots=True)
class RequestGroup:
    """A request group (fleet) configuration."""

    id: int
    name: str
    instance_request_mode: str | None = None
    region: str | None = None
    include_azs: bool | None = None
    instance_types: list[str] | None = None
    instance_requirements: dict[str, Any] | None = None
    target_capacities: list[int] | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RequestGroup:
        """Create RequestGroup from API response dictionary."""
        instance_types_raw = _parse_jsonish_list_str(data.get("instance_types"))
        target_caps_raw = _parse_jsonish_list_str(data.get("target_capacities"))
        metadata_raw = _parse_jsonish_dict_str(data.get("metadata"))
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            instance_request_mode=(
                str(data["instance_request_mode"])
                if data.get("instance_request_mode") is not None
                else None
            ),
            region=str(data["region"]) if data.get("region") is not None else None,
            include_azs=bool(data["include_azs"]) if data.get("include_azs") is not None else None,
            instance_types=(
                [str(x) for x in instance_types_raw] if instance_types_raw is not None else None
            ),
            instance_requirements=(
                dict(data["instance_requirements"])
                if isinstance(data.get("instance_requirements"), dict)
                else None
            ),
            target_capacities=(
                [int(x) for x in target_caps_raw] if target_caps_raw is not None else None
            ),
            metadata=metadata_raw,
            created_at=_parse_datetime_flexible(data.get("created_at")),
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
            score=float(data["placement_score"]),
            availability_zone=str(data["availability_zone"]),
            target_capacity=int(data["target_capacity"]),
            request_group_id=int(data["group_id"]),
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
