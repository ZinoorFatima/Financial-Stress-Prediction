"""Pydantic models — the contract shared between the API and the engine.

These define the unified portfolio schema, the stress scenario definition,
and the shape of results returned to the dashboard.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AssetClass(str, Enum):
    """Supported asset classes. Add new members + a handler to extend."""

    LOAN = "loan"
    MORTGAGE = "mortgage"


class CollateralType(str, Enum):
    NONE = "none"
    PROPERTY = "property"
    EQUITY = "equity"


# --------------------------------------------------------------------------- #
# Portfolio
# --------------------------------------------------------------------------- #
class PortfolioAsset(BaseModel):
    """One position in the portfolio (unified schema across asset classes).

    Not every column is meaningful for every asset class; per-class handlers
    decide which fields drive their revaluation. Sensible defaults keep the
    input CSV forgiving.
    """

    asset_id: str
    asset_class: AssetClass
    currency: str = "USD"

    # Exposure / valuation
    exposure_at_default: float = Field(..., ge=0, description="EAD in asset currency")
    market_value: float = Field(0.0, description="Current mark-to-market value")

    # Credit risk parameters
    probability_of_default: float = Field(0.0, ge=0, le=1, alias="pd")
    loss_given_default: float = Field(0.45, ge=0, le=1, alias="lgd")

    # Collateral
    collateral_value: float = Field(0.0, ge=0)
    collateral_type: CollateralType = CollateralType.NONE

    # Market sensitivities (linear, pragmatic MVP)
    duration: float = Field(0.0, description="Modified duration in years (IR sensitivity)")
    equity_beta: float = Field(0.0, description="Sensitivity of value to equity shock")

    model_config = {"populate_by_name": True}

    @field_validator("currency")
    @classmethod
    def _upper_currency(cls, v: str) -> str:
        return v.strip().upper()


# --------------------------------------------------------------------------- #
# Scenario
# --------------------------------------------------------------------------- #
class Scenario(BaseModel):
    """A custom stress scenario the user defines in the dashboard."""

    name: str = Field(..., min_length=1)
    description: str = ""

    # Equity market shock, e.g. -0.30 == a 30% equity crash.
    equity_shock: float = 0.0
    # Parallel interest-rate shock in basis points, e.g. 200 == +200bps.
    rate_shock_bps: float = 0.0
    # FX shocks per currency vs. base currency, e.g. {"EUR": -0.10}.
    # Positive == that currency strengthens vs. base.
    fx_shocks: dict[str, float] = Field(default_factory=dict)

    # Credit overlay: multiplicative stress on PD under this scenario.
    # e.g. 1.5 == PDs rise by 50% (capped at 1.0).
    pd_stress_multiplier: float = Field(1.0, ge=0)

    @field_validator("fx_shocks")
    @classmethod
    def _upper_fx_keys(cls, v: dict[str, float]) -> dict[str, float]:
        return {k.strip().upper(): val for k, val in v.items()}


# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #
class AssetResult(BaseModel):
    """Per-asset stress outcome."""

    asset_id: str
    asset_class: AssetClass
    currency: str

    base_value: float
    stressed_value: float
    value_change: float

    base_expected_loss: float
    stressed_expected_loss: float
    expected_loss_change: float

    stressed_pd: float
    stressed_lgd: float


class Breakdown(BaseModel):
    """Aggregated metrics grouped by some key (asset class, currency, ...)."""

    key: str
    exposure: float
    base_expected_loss: float
    stressed_expected_loss: float
    expected_loss_change: float
    value_change: float


class StressResult(BaseModel):
    """Full result payload returned to the dashboard."""

    scenario: Scenario

    total_exposure: float
    total_base_value: float
    total_stressed_value: float
    total_value_change: float

    total_base_expected_loss: float
    total_stressed_expected_loss: float
    total_expected_loss_change: float

    # Headline risk metric: stressed EL as % of exposure.
    stressed_loss_ratio: float

    by_asset_class: list[Breakdown]
    by_currency: list[Breakdown]
    assets: list[AssetResult]


class StressRequest(BaseModel):
    """Run a scenario against an in-memory portfolio (used by the API)."""

    scenario: Scenario
    portfolio: list[PortfolioAsset]


class ScenarioComparison(BaseModel):
    """Side-by-side summary across multiple scenarios."""

    scenario_name: str
    total_stressed_expected_loss: float
    total_expected_loss_change: float
    total_value_change: float
    stressed_loss_ratio: float
