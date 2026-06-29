"""Application configuration.

Centralised settings so that environment-specific values (base currency,
data directory, DB URL for the later migration) live in one place.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STRESS_", env_file=".env", extra="ignore")

    app_name: str = "Stress Testing Tool"
    # Reporting currency that FX shocks are expressed relative to.
    base_currency: str = "USD"
    # Where bundled sample CSV/JSON live.
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    # CORS origins for the frontend dev server.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Placeholder for the later CSV -> database transition.
    database_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
