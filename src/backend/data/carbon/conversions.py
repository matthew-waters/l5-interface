"""Shared carbon-intensity unit conversions."""

from __future__ import annotations

# WattTime commonly returns lbs CO2 / MWh.
# Normalize to gCO2 / kWh.
LBS_TO_GRAMS: float = 453.59237
MWH_TO_KWH: float = 1000.0

