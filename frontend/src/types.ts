// Mirrors the backend Pydantic schemas (app/models/schemas.py).

export type AssetClass = "loan" | "mortgage";
export type CollateralType = "none" | "property" | "equity";

export interface PortfolioAsset {
  asset_id: string;
  asset_class: AssetClass;
  currency: string;
  exposure_at_default: number;
  market_value: number;
  probability_of_default: number;
  loss_given_default: number;
  collateral_value: number;
  collateral_type: CollateralType;
  duration: number;
  equity_beta: number;
}

export interface Scenario {
  name: string;
  description: string;
  equity_shock: number;
  rate_shock_bps: number;
  fx_shocks: Record<string, number>;
  pd_stress_multiplier: number;
}

export interface AssetResult {
  asset_id: string;
  asset_class: AssetClass;
  currency: string;
  base_value: number;
  stressed_value: number;
  value_change: number;
  base_expected_loss: number;
  stressed_expected_loss: number;
  expected_loss_change: number;
  stressed_pd: number;
  stressed_lgd: number;
}

export interface Breakdown {
  key: string;
  exposure: number;
  base_expected_loss: number;
  stressed_expected_loss: number;
  expected_loss_change: number;
  value_change: number;
}

export interface StressResult {
  scenario: Scenario;
  total_exposure: number;
  total_base_value: number;
  total_stressed_value: number;
  total_value_change: number;
  total_base_expected_loss: number;
  total_stressed_expected_loss: number;
  total_expected_loss_change: number;
  stressed_loss_ratio: number;
  by_asset_class: Breakdown[];
  by_currency: Breakdown[];
  assets: AssetResult[];
}

export interface ScenarioComparison {
  scenario_name: string;
  total_stressed_expected_loss: number;
  total_expected_loss_change: number;
  total_value_change: number;
  stressed_loss_ratio: number;
}
