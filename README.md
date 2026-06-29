# Stress Testing Tool

A modular, cloud-ready application for defining custom **stress scenarios**
(equity, interest-rate, FX and credit shocks) and simulating their impact on a
portfolio of **loans and collateralised mortgages**. Results — expected losses,
risk metrics and value changes — are visualised in an interactive dashboard.

This is an **MVP** built as a clean foundation for an enterprise-grade platform.

```
┌────────────────────┐      HTTP/JSON       ┌──────────────────────────┐
│  React + Plotly UI │  ───────────────────▶│  FastAPI backend          │
│  (Vite, TS)        │                      │  ┌────────────────────┐  │
│  - scenario builder│ ◀─────────────────── │  │ stress engine      │  │
│  - results charts  │                      │  │ asset handlers     │  │
└────────────────────┘                      │  │ risk metrics       │  │
                                             │  │ CSV data loader    │  │
                                             │  └────────────────────┘  │
                                             └──────────────────────────┘
```

---

## Quick start (local dev)

### 1. Backend (Python 3.11+)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload     # http://localhost:8000  (docs at /docs)
```

Run the tests:

```bash
cd backend
pytest -q
```

### 2. Frontend (Node 18+)

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The Vite dev server proxies `/api` → `http://localhost:8000`, so start the
backend first.

### 3. One-command run (Docker)

```bash
docker compose up --build
# Frontend → http://localhost:8080   (nginx proxies /api to the backend)
# Backend  → http://localhost:8000
```

---

## How it works

### The risk model (pragmatic MVP)

For each position the engine applies **linear shocks** and recomputes credit
**Expected Loss** `EL = PD × LGD × EAD`:

| Shock | Effect on market value |
|-------|------------------------|
| Equity | `ΔV = MV × equity_beta × equity_shock` |
| Interest rate | `ΔV = −MV × duration × Δy` (`Δy` = bps / 10,000) |
| FX | `ΔV = V × fx_shock` (non-base-currency positions only) |

Credit deterioration under stress:

- **Stressed PD** = `min(1, PD × pd_stress_multiplier)`
- **Stressed LGD** rises as collateral erodes:
  `LGD = max(input_LGD, 1 − stressed_collateral / EAD)`.
  Collateral is revalued by the relevant shock (property dampened vs. equities).
  With no collateral, LGD keeps its input value, so a baseline run is neutral.

Headline metric: **stressed loss ratio** = total stressed EL ÷ total exposure.

### Portfolio CSV schema (unified across asset classes)

| Column | Meaning | Default |
|--------|---------|---------|
| `asset_id` | Unique identifier | — (required) |
| `asset_class` | `loan` or `mortgage` | — (required) |
| `currency` | ISO code; FX shocks apply vs. base (USD) | `USD` |
| `exposure_at_default` | EAD in asset currency | — (required) |
| `market_value` | Current mark-to-market | `0` |
| `pd` | Probability of default (0–1) | `0` |
| `lgd` | Loss given default (0–1) | `0.45` |
| `collateral_value` | Collateral amount | `0` |
| `collateral_type` | `none` / `property` / `equity` | `none` |
| `duration` | Modified duration, years (IR sensitivity) | `0` |
| `equity_beta` | Equity-shock sensitivity | `0` |

A ready-to-use sample lives at `backend/data/portfolio_sample.csv`.

### API

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/api/health` | Liveness probe |
| `GET`  | `/api/scenarios` | Preset scenario library |
| `GET`  | `/api/portfolio/sample` | Bundled sample portfolio |
| `POST` | `/api/portfolio/upload` | Upload + validate a portfolio CSV |
| `POST` | `/api/stress/run` | Run one scenario, get full results |
| `POST` | `/api/stress/compare` | Run many scenarios, get a summary |

Interactive docs: `http://localhost:8000/docs`.

---

## Project structure

```
backend/
  app/
    main.py            FastAPI app + CORS
    config.py          Settings (base currency, data dir, future DB URL)
    api/routes.py      HTTP endpoints
    core/
      engine.py        Orchestrates a scenario across the portfolio
      asset_handlers.py Per-asset-class revaluation + credit logic
      risk.py          EL formula + per-asset evaluation
      scenarios.py     Preset scenario library
      data_loader.py   CSV parsing + PortfolioRepository (DB seam)
    models/schemas.py  Pydantic contracts (portfolio, scenario, results)
  data/                Sample CSV
  tests/               Engine + parsing tests
frontend/
  src/
    App.tsx            State + data flow
    api.ts             Typed API client
    types.ts           TS mirror of backend schemas
    components/        ScenarioBuilder, PortfolioPanel, ResultsDashboard, charts
```

---

## Extending the tool

- **New asset class:** add a member to `AssetClass`, subclass `AssetHandler`,
  register it in `_HANDLERS`. The engine and API need no changes.
- **Database transition:** implement a `PortfolioRepository` backed by SQL
  (e.g. SQLAlchemy + Postgres) and set `STRESS_DATABASE_URL`. The engine already
  depends only on the repository abstraction, not on CSV.
- **Richer quant:** the linear handlers are the place to add duration+convexity,
  full repricing, correlated/Monte-Carlo scenarios, or VaR/ES — without touching
  the API or UI contracts.

## Roadmap

1. Persist portfolios & scenarios in Postgres (replace CSV repository).
2. AuthN/Z + multi-tenant workspaces.
3. Sensitivity-based and Monte-Carlo engines behind the same API.
4. Scenario versioning, audit trail, and scheduled batch runs.
```
