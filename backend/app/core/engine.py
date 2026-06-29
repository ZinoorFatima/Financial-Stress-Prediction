"""Stress engine — orchestrates scenario application across the portfolio.

Takes a portfolio + scenario, dispatches each asset to its handler, computes
per-asset results, then aggregates into headline metrics and breakdowns.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from app.core.asset_handlers import get_handler
from app.core.risk import evaluate_asset
from app.models.schemas import (
    AssetResult,
    Breakdown,
    PortfolioAsset,
    Scenario,
    ScenarioComparison,
    StressResult,
)


def run_scenario(
    portfolio: list[PortfolioAsset],
    scenario: Scenario,
    base_currency: str = "USD",
) -> StressResult:
    """Run a single scenario against the portfolio and aggregate results."""
    results: list[AssetResult] = [
        evaluate_asset(asset, scenario, get_handler(asset.asset_class), base_currency)
        for asset in portfolio
    ]

    total_exposure = sum(a.exposure_at_default for a in portfolio)
    total_base_value = sum(r.base_value for r in results)
    total_stressed_value = sum(r.stressed_value for r in results)
    total_base_el = sum(r.base_expected_loss for r in results)
    total_stressed_el = sum(r.stressed_expected_loss for r in results)

    return StressResult(
        scenario=scenario,
        total_exposure=total_exposure,
        total_base_value=total_base_value,
        total_stressed_value=total_stressed_value,
        total_value_change=total_stressed_value - total_base_value,
        total_base_expected_loss=total_base_el,
        total_stressed_expected_loss=total_stressed_el,
        total_expected_loss_change=total_stressed_el - total_base_el,
        stressed_loss_ratio=(total_stressed_el / total_exposure) if total_exposure else 0.0,
        by_asset_class=_aggregate(portfolio, results, key=lambda a: a.asset_class.value),
        by_currency=_aggregate(portfolio, results, key=lambda a: a.currency),
        assets=results,
    )


def compare_scenarios(
    portfolio: list[PortfolioAsset],
    scenarios: Iterable[Scenario],
    base_currency: str = "USD",
) -> list[ScenarioComparison]:
    """Run several scenarios and return a compact comparison summary."""
    comparisons: list[ScenarioComparison] = []
    for scenario in scenarios:
        res = run_scenario(portfolio, scenario, base_currency)
        comparisons.append(
            ScenarioComparison(
                scenario_name=scenario.name,
                total_stressed_expected_loss=res.total_stressed_expected_loss,
                total_expected_loss_change=res.total_expected_loss_change,
                total_value_change=res.total_value_change,
                stressed_loss_ratio=res.stressed_loss_ratio,
            )
        )
    return comparisons


def _aggregate(
    portfolio: list[PortfolioAsset],
    results: list[AssetResult],
    key,
) -> list[Breakdown]:
    """Group exposure + EL + value change by an asset attribute."""
    exposure: dict[str, float] = defaultdict(float)
    base_el: dict[str, float] = defaultdict(float)
    stressed_el: dict[str, float] = defaultdict(float)
    value_change: dict[str, float] = defaultdict(float)

    for asset, res in zip(portfolio, results):
        k = key(asset)
        exposure[k] += asset.exposure_at_default
        base_el[k] += res.base_expected_loss
        stressed_el[k] += res.stressed_expected_loss
        value_change[k] += res.value_change

    return [
        Breakdown(
            key=k,
            exposure=exposure[k],
            base_expected_loss=base_el[k],
            stressed_expected_loss=stressed_el[k],
            expected_loss_change=stressed_el[k] - base_el[k],
            value_change=value_change[k],
        )
        for k in sorted(exposure)
    ]
