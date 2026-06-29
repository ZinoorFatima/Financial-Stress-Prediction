"""Data ingestion.

Currently loads portfolios from CSV (file path or uploaded bytes). The
`PortfolioRepository` abstraction is the seam for the later database
transition: swap the CSV implementation for a SQL-backed one without touching
the engine or API.
"""
from __future__ import annotations

import csv
import io
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import ValidationError

from app.models.schemas import PortfolioAsset

# CSV columns mapped onto the unified schema. Aliases keep the input friendly.
_NUMERIC_FIELDS = {
    "exposure_at_default",
    "market_value",
    "pd",
    "lgd",
    "collateral_value",
    "duration",
    "equity_beta",
}


class PortfolioParseError(Exception):
    """Raised when a CSV row cannot be parsed into a PortfolioAsset."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"{len(errors)} row(s) failed validation")


def _coerce_row(row: dict[str, str]) -> dict[str, object]:
    """Normalise a raw CSV row: trim keys, blank -> default, numeric coercion."""
    clean: dict[str, object] = {}
    for raw_key, raw_val in row.items():
        if raw_key is None:
            continue
        key = raw_key.strip().lower()
        val = (raw_val or "").strip()
        if val == "":
            continue  # let schema defaults apply
        if key in _NUMERIC_FIELDS:
            clean[key] = float(val)
        else:
            clean[key] = val
    return clean


def parse_portfolio_csv(text: str) -> list[PortfolioAsset]:
    """Parse CSV text into validated PortfolioAsset rows.

    Aggregates all row errors so the user sees every problem at once.
    """
    reader = csv.DictReader(io.StringIO(text))
    assets: list[PortfolioAsset] = []
    errors: list[str] = []

    for line_no, row in enumerate(reader, start=2):  # header is line 1
        try:
            assets.append(PortfolioAsset.model_validate(_coerce_row(row)))
        except (ValidationError, ValueError) as exc:
            errors.append(f"row {line_no}: {exc}")

    if errors:
        raise PortfolioParseError(errors)
    return assets


# --------------------------------------------------------------------------- #
# Repository abstraction (CSV now, DB later)
# --------------------------------------------------------------------------- #
class PortfolioRepository(ABC):
    @abstractmethod
    def load(self) -> list[PortfolioAsset]:
        ...


class CsvPortfolioRepository(PortfolioRepository):
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> list[PortfolioAsset]:
        return parse_portfolio_csv(self.path.read_text(encoding="utf-8"))
