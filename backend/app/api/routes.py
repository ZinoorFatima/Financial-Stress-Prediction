"""HTTP API for the stress testing tool.

Endpoints:
    GET  /api/health                 - liveness probe
    GET  /api/scenarios              - preset scenario library
    GET  /api/portfolio/sample       - bundled sample portfolio
    POST /api/portfolio/upload       - upload + validate a portfolio CSV
    POST /api/stress/run             - run one scenario on a portfolio
    POST /api/stress/compare         - run several scenarios, get a summary
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.core import engine
from app.core.data_loader import (
    CsvPortfolioRepository,
    PortfolioParseError,
    parse_portfolio_csv,
)
from app.core.scenarios import PRESET_SCENARIOS
from app.models.schemas import (
    PortfolioAsset,
    Scenario,
    ScenarioComparison,
    StressRequest,
    StressResult,
)
from pydantic import BaseModel

router = APIRouter(prefix="/api")
settings = get_settings()


class CompareRequest(BaseModel):
    scenarios: list[Scenario]
    portfolio: list[PortfolioAsset]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "base_currency": settings.base_currency}


@router.get("/scenarios", response_model=list[Scenario])
def list_scenarios() -> list[Scenario]:
    return PRESET_SCENARIOS


@router.get("/portfolio/sample", response_model=list[PortfolioAsset])
def sample_portfolio() -> list[PortfolioAsset]:
    repo = CsvPortfolioRepository(settings.data_dir / "portfolio_sample.csv")
    try:
        return repo.load()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample portfolio not found")
    except PortfolioParseError as exc:
        raise HTTPException(status_code=422, detail={"errors": exc.errors})


@router.post("/portfolio/upload", response_model=list[PortfolioAsset])
async def upload_portfolio(file: UploadFile = File(...)) -> list[PortfolioAsset]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    raw = await file.read()
    try:
        return parse_portfolio_csv(raw.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not valid UTF-8 text")
    except PortfolioParseError as exc:
        raise HTTPException(status_code=422, detail={"errors": exc.errors})


@router.post("/stress/run", response_model=StressResult)
def stress_run(req: StressRequest) -> StressResult:
    if not req.portfolio:
        raise HTTPException(status_code=400, detail="Portfolio is empty")
    return engine.run_scenario(req.portfolio, req.scenario, settings.base_currency)


@router.post("/stress/compare", response_model=list[ScenarioComparison])
def stress_compare(req: CompareRequest) -> list[ScenarioComparison]:
    if not req.portfolio:
        raise HTTPException(status_code=400, detail="Portfolio is empty")
    if not req.scenarios:
        raise HTTPException(status_code=400, detail="No scenarios provided")
    return engine.compare_scenarios(req.portfolio, req.scenarios, settings.base_currency)
