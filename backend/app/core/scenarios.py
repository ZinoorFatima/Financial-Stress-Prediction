"""Predefined scenario library.

Ships a handful of regulator-style scenarios so the dashboard has something to
run out of the box. Users can clone and tweak these in the scenario builder.
"""
from __future__ import annotations

from app.models.schemas import Scenario

PRESET_SCENARIOS: list[Scenario] = [
    Scenario(
        name="Baseline",
        description="No shocks — sanity check / reference point.",
    ),
    Scenario(
        name="Equity Crash",
        description="Severe equity sell-off with mild credit deterioration.",
        equity_shock=-0.35,
        rate_shock_bps=-50,
        pd_stress_multiplier=1.4,
    ),
    Scenario(
        name="Rate Spike",
        description="Sharp parallel rise in interest rates (+250bps).",
        rate_shock_bps=250,
        pd_stress_multiplier=1.2,
    ),
    Scenario(
        name="FX Crisis",
        description="Base-currency strength: foreign exposures lose value.",
        fx_shocks={"EUR": -0.15, "GBP": -0.18, "JPY": -0.20},
        pd_stress_multiplier=1.3,
    ),
    Scenario(
        name="Severe Recession",
        description="Combined equity, rate and FX stress with high default risk.",
        equity_shock=-0.40,
        rate_shock_bps=150,
        fx_shocks={"EUR": -0.12, "GBP": -0.15},
        pd_stress_multiplier=2.0,
    ),
]


def preset_by_name(name: str) -> Scenario | None:
    for s in PRESET_SCENARIOS:
        if s.name.lower() == name.lower():
            return s
    return None
