"""Tests for the stress engine, risk formulas and data loader."""
from __future__ import annotations

import pytest

from app.core import engine
from app.core.data_loader import PortfolioParseError, parse_portfolio_csv
from app.core.risk import expected_loss
from app.models.schemas import AssetClass, CollateralType, PortfolioAsset, Scenario


def _loan(**kw) -> PortfolioAsset:
    base = dict(
        asset_id="LN-1",
        asset_class=AssetClass.LOAN,
        currency="USD",
        exposure_at_default=1_000_000,
        market_value=1_000_000,
        probability_of_default=0.02,
        loss_given_default=0.45,
    )
    base.update(kw)
    return PortfolioAsset(**base)


def test_expected_loss_formula():
    assert expected_loss(1_000_000, 0.02, 0.45) == pytest.approx(9_000)


def test_baseline_scenario_is_neutral():
    portfolio = [_loan()]
    res = engine.run_scenario(portfolio, Scenario(name="Baseline"))
    assert res.total_value_change == pytest.approx(0.0)
    assert res.total_expected_loss_change == pytest.approx(0.0)
    assert res.total_base_expected_loss == pytest.approx(9_000)


def test_pd_multiplier_increases_expected_loss():
    portfolio = [_loan()]
    res = engine.run_scenario(portfolio, Scenario(name="s", pd_stress_multiplier=2.0))
    # PD doubles -> EL roughly doubles (LGD unchanged, no collateral).
    assert res.total_stressed_expected_loss == pytest.approx(18_000)


def test_pd_is_capped_at_one():
    portfolio = [_loan(probability_of_default=0.8)]
    res = engine.run_scenario(portfolio, Scenario(name="s", pd_stress_multiplier=5.0))
    assert res.assets[0].stressed_pd == pytest.approx(1.0)


def test_rate_shock_moves_value_via_duration():
    # +100bps on a 5y-duration bond-like loan -> ~-5% value.
    portfolio = [_loan(duration=5.0)]
    res = engine.run_scenario(portfolio, Scenario(name="s", rate_shock_bps=100))
    assert res.assets[0].value_change == pytest.approx(-50_000)


def test_equity_shock_via_beta():
    portfolio = [_loan(equity_beta=0.5)]
    res = engine.run_scenario(portfolio, Scenario(name="s", equity_shock=-0.20))
    # -20% equity * beta 0.5 -> -10% value.
    assert res.assets[0].value_change == pytest.approx(-100_000)


def test_fx_shock_only_hits_foreign_currency():
    usd = _loan(asset_id="USD", currency="USD")
    eur = _loan(asset_id="EUR", currency="EUR")
    scenario = Scenario(name="s", fx_shocks={"EUR": -0.10})
    res = engine.run_scenario([usd, eur], scenario, base_currency="USD")
    by_id = {a.asset_id: a for a in res.assets}
    assert by_id["USD"].value_change == pytest.approx(0.0)
    assert by_id["EUR"].value_change == pytest.approx(-100_000)


def test_mortgage_collateral_erosion_raises_lgd():
    mtg = PortfolioAsset(
        asset_id="MG-1",
        asset_class=AssetClass.MORTGAGE,
        exposure_at_default=400_000,
        market_value=400_000,
        probability_of_default=0.02,
        loss_given_default=0.10,
        collateral_value=440_000,  # 110% LTV coverage
        collateral_type=CollateralType.PROPERTY,
    )
    # Severe equity/property crash erodes collateral below the exposure.
    res = engine.run_scenario([mtg], Scenario(name="s", equity_shock=-0.40))
    # property shock = -0.40 * 0.6 = -24% -> collateral 334,400 < 400,000 EAD.
    assert res.assets[0].stressed_lgd > 0.10


def test_aggregation_by_asset_class_and_currency():
    portfolio = [_loan(asset_id="A", currency="USD"), _loan(asset_id="B", currency="EUR")]
    res = engine.run_scenario(portfolio, Scenario(name="Baseline"))
    classes = {b.key for b in res.by_asset_class}
    currencies = {b.key for b in res.by_currency}
    assert classes == {"loan"}
    assert currencies == {"USD", "EUR"}


def test_compare_scenarios_returns_one_row_each():
    portfolio = [_loan()]
    scenarios = [Scenario(name="A"), Scenario(name="B", pd_stress_multiplier=2.0)]
    out = engine.compare_scenarios(portfolio, scenarios)
    assert [c.scenario_name for c in out] == ["A", "B"]


def test_csv_parsing_roundtrip():
    csv_text = (
        "asset_id,asset_class,currency,exposure_at_default,market_value,pd,lgd\n"
        "LN-1,loan,usd,1000000,1000000,0.02,0.45\n"
    )
    assets = parse_portfolio_csv(csv_text)
    assert len(assets) == 1
    assert assets[0].currency == "USD"  # normalised to upper
    assert assets[0].probability_of_default == 0.02


def test_csv_parsing_collects_errors():
    bad = (
        "asset_id,asset_class,exposure_at_default\n"
        "LN-1,not_an_asset_class,1000000\n"
    )
    with pytest.raises(PortfolioParseError) as exc:
        parse_portfolio_csv(bad)
    assert len(exc.value.errors) == 1
