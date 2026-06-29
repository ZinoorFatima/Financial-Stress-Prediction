"""Per-asset-class adapters.

Each handler knows how to revalue one asset class under a scenario and how to
derive its stressed credit parameters (PD/LGD). New asset classes plug in by
registering a handler — the engine stays untouched.

Modelling approach (pragmatic MVP, linear shocks):

* Market value change:
    - Equity:  ΔV_equity = market_value * equity_beta * equity_shock
    - Rates:   ΔV_rate   = -market_value * duration * Δy   (Δy in decimals)
    - FX:      ΔV_fx      = (value) * fx_shock   (currency vs. base)
* Collateral is revalued by the shock relevant to its type (property collateral
  is hit by the equity/real-asset shock as a proxy in the MVP).
* Stressed PD = min(1, PD * pd_stress_multiplier).
* Stressed LGD rises as collateral coverage falls:
    LGD = clamp(1 - stressed_collateral / EAD, base_lgd_floor, 1).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.schemas import (
    AssetClass,
    CollateralType,
    PortfolioAsset,
    Scenario,
)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class AssetHandler(ABC):
    """Base class for asset-class-specific stress logic."""

    asset_class: AssetClass

    # --- market revaluation ------------------------------------------------ #
    def stressed_value(self, asset: PortfolioAsset, scenario: Scenario, base_currency: str) -> float:
        """Return the asset's market value after applying market shocks."""
        value = asset.market_value

        # Equity shock via beta.
        value += asset.market_value * asset.equity_beta * scenario.equity_shock

        # Interest-rate shock via modified duration. bps -> decimal yield change.
        delta_y = scenario.rate_shock_bps / 10_000.0
        value += -asset.market_value * asset.duration * delta_y

        # FX shock: only positions not in the base currency are affected.
        if asset.currency != base_currency:
            fx = scenario.fx_shocks.get(asset.currency, 0.0)
            value += value * fx

        return value

    # --- collateral revaluation ------------------------------------------- #
    def stressed_collateral(self, asset: PortfolioAsset, scenario: Scenario) -> float:
        """Revalue collateral under the scenario based on its type."""
        if asset.collateral_type == CollateralType.NONE or asset.collateral_value <= 0:
            return asset.collateral_value
        if asset.collateral_type == CollateralType.EQUITY:
            shock = scenario.equity_shock
        elif asset.collateral_type == CollateralType.PROPERTY:
            # Property is treated as a real asset; use equity shock as a proxy
            # but dampened (property typically less volatile than equities).
            shock = scenario.equity_shock * 0.6
        else:
            shock = 0.0
        return max(0.0, asset.collateral_value * (1.0 + shock))

    # --- credit parameters ------------------------------------------------ #
    def stressed_pd(self, asset: PortfolioAsset, scenario: Scenario) -> float:
        return _clamp(asset.probability_of_default * scenario.pd_stress_multiplier, 0.0, 1.0)

    def stressed_lgd(self, asset: PortfolioAsset, scenario: Scenario) -> float:
        """LGD derived from stressed collateral coverage, floored at the input LGD.

        With no collateral the asset simply keeps its input LGD. With collateral,
        stress can only *worsen* recovery: as collateral value erodes the implied
        LGD rises, but it is floored at the input assumption so an unshocked
        (baseline) run leaves LGD unchanged.
        """
        ead = asset.exposure_at_default
        if ead <= 0 or asset.collateral_value <= 0:
            return asset.loss_given_default
        stressed_coll = self.stressed_collateral(asset, scenario)
        coverage_lgd = _clamp(1.0 - stressed_coll / ead, 0.0, 1.0)
        # Stress only ever increases LGD relative to the input assumption.
        return max(asset.loss_given_default, coverage_lgd)


class LoanHandler(AssetHandler):
    """Corporate / retail loans. Credit-driven; usually low market sensitivity."""

    asset_class = AssetClass.LOAN


class MortgageHandler(AssetHandler):
    """Collateralised mortgages. Loss is dominated by property collateral value."""

    asset_class = AssetClass.MORTGAGE

    def stressed_collateral(self, asset: PortfolioAsset, scenario: Scenario) -> float:
        # Mortgages are property-backed by default even if type left unset.
        if asset.collateral_type == CollateralType.NONE and asset.collateral_value > 0:
            shock = scenario.equity_shock * 0.6
            return max(0.0, asset.collateral_value * (1.0 + shock))
        return super().stressed_collateral(asset, scenario)


# Registry: asset_class -> handler instance.
_HANDLERS: dict[AssetClass, AssetHandler] = {
    AssetClass.LOAN: LoanHandler(),
    AssetClass.MORTGAGE: MortgageHandler(),
}


def get_handler(asset_class: AssetClass) -> AssetHandler:
    handler = _HANDLERS.get(asset_class)
    if handler is None:  # pragma: no cover - guarded by enum validation
        raise ValueError(f"No handler registered for asset class: {asset_class}")
    return handler
