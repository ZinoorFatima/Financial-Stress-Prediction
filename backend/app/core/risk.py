"""Risk metric calculations.

Pure functions over a single asset given a (handler, scenario). Kept separate
from the engine so the formulas are easy to unit-test and audit.
"""
from __future__ import annotations

from app.core.asset_handlers import AssetHandler
from app.models.schemas import AssetResult, PortfolioAsset, Scenario


def expected_loss(ead: float, pd: float, lgd: float) -> float:
    """Standard credit Expected Loss: EL = PD x LGD x EAD."""
    return ead * pd * lgd


def evaluate_asset(
    asset: PortfolioAsset,
    scenario: Scenario,
    handler: AssetHandler,
    base_currency: str,
) -> AssetResult:
    """Compute base vs. stressed value and expected loss for one asset."""
    # Base (no shock) expected loss.
    base_el = expected_loss(
        asset.exposure_at_default,
        asset.probability_of_default,
        asset.loss_given_default,
    )

    # Stressed market value.
    stressed_value = handler.stressed_value(asset, scenario, base_currency)

    # Stressed credit parameters.
    s_pd = handler.stressed_pd(asset, scenario)
    s_lgd = handler.stressed_lgd(asset, scenario)
    stressed_el = expected_loss(asset.exposure_at_default, s_pd, s_lgd)

    return AssetResult(
        asset_id=asset.asset_id,
        asset_class=asset.asset_class,
        currency=asset.currency,
        base_value=asset.market_value,
        stressed_value=stressed_value,
        value_change=stressed_value - asset.market_value,
        base_expected_loss=base_el,
        stressed_expected_loss=stressed_el,
        expected_loss_change=stressed_el - base_el,
        stressed_pd=s_pd,
        stressed_lgd=s_lgd,
    )
