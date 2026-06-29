# Sample portfolios

Upload any of these via the **Upload CSV** button in the dashboard to test the
application. Each file targets a different behaviour.

| File | Positions | What it tests |
|------|-----------|---------------|
| `01_loans_only.csv` | 8 | Pure credit/loan book, no collateral. Sensitive to **PD multiplier** and **rate shocks** (via duration). |
| `02_mortgages_collateral.csv` | 10 | Property-backed mortgages. Watch **stressed LGD rise** as the equity/property shock erodes collateral. |
| `03_multicurrency_fx.csv` | 10 | EUR/GBP/JPY/CHF/AUD/CAD exposures. Add **FX shocks** in the scenario builder to see currency-driven value changes. |
| `04_distressed_highrisk.csv` | 8 | High PDs (9–35%) and high LGDs. Large baseline EL; PD multiplier pushes several positions toward 100% PD (capped). |
| `05_minimal_columns.csv` | 5 | Only the required columns (`asset_id`, `asset_class`, `exposure_at_default`, `pd`). Tests **schema defaults** (LGD defaults to 0.45, etc.). |
| `06_large_diversified.csv` | 30 | Mixed loans + mortgages across 7 currencies. Best file for the **comparison** view and a full dashboard. |
| `07_invalid_for_error_testing.csv` | 5 | **Intentionally broken** rows (unknown asset class `bond`, negative EAD, `pd` > 1, non-numeric value). Upload to confirm the app reports per-row validation errors and rejects the file. |

## Suggested test flow

1. Upload `06_large_diversified.csv`, run **Severe Recession**, then click
   **Compare all presets** to see scenario ranking.
2. Upload `03_multicurrency_fx.csv` and add FX shocks (e.g. EUR −15, JPY −20) to
   isolate FX impact.
3. Upload `02_mortgages_collateral.csv` and crank the **equity shock** negative —
   watch stressed LGD and EL climb as collateral coverage falls.
4. Upload `07_invalid_for_error_testing.csv` to verify the error path.

All files use the unified schema documented in the main
[`README.md`](../README.md#portfolio-csv-schema-unified-across-asset-classes).
