"""Centralized configuration loader with startup validation."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


# Locate .env relative to project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"

if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)


# ------------------------------------------------------------------
# Settings dataclass — single source of truth for all config
# ------------------------------------------------------------------

@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment."""

    # LLM
    gemini_api_key: str = ""
    default_model: str = "gemini-2.5-flash-lite"
    fallback_model: str = "gemini-2.5-flash"

    # Quality gate
    quality_threshold: float = 0.70
    max_reruns: int = 2

    # PubMed defaults
    pubmed_max_fetch: int = 20
    pubmed_year_start: int = 2015
    pubmed_target_expansion: bool = True

    # Entity resolution
    resolution_min_score: float = 0.6
    resolution_min_delta: float = 0.15

    # API endpoints (not configurable by the user, but centralized here)
    api_opentargets: str = "https://api.platform.opentargets.org/api/v4/graphql"
    api_pubmed_search: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    api_pubmed_fetch: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _get_secret(key: str, default: str = "") -> str:
    """Try os.environ first, then st.secrets (Streamlit Cloud), then default."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


def load_settings() -> Settings:
    """Load settings from environment variables / Streamlit secrets with sensible defaults."""

    def _bool(val: str) -> bool:
        return val.strip().lower() in ("1", "true", "yes")

    return Settings(
        gemini_api_key=_get_secret("GEMINI_API_KEY"),
        default_model=_get_secret("ORPHANCURE_DEFAULT_MODEL", "gemini-2.5-flash-lite"),
        fallback_model=_get_secret("ORPHANCURE_FALLBACK_MODEL", "gemini-2.5-flash"),
        quality_threshold=float(_get_secret("ORPHANCURE_QUALITY_THRESHOLD", "0.70")),
        max_reruns=int(_get_secret("ORPHANCURE_MAX_RERUNS", "2")),
        pubmed_max_fetch=int(_get_secret("ORPHANCURE_PUBMED_MAX_FETCH", "20")),
        pubmed_year_start=int(_get_secret("ORPHANCURE_PUBMED_YEAR_START", "2015")),
        pubmed_target_expansion=_bool(_get_secret("ORPHANCURE_PUBMED_TARGET_EXPANSION", "true")),
        resolution_min_score=float(_get_secret("ORPHANCURE_RESOLUTION_MIN_SCORE", "0.6")),
        resolution_min_delta=float(_get_secret("ORPHANCURE_RESOLUTION_MIN_DELTA", "0.15")),
    )


def validate_settings(settings: Settings) -> list[str]:
    """Return a list of validation error messages (empty = all good)."""
    errors: list[str] = []
    if not settings.gemini_api_key:
        errors.append(
            "GEMINI_API_KEY is not set. "
            "Please set it as an environment variable or in a .env file. "
            "See .env.example for details."
        )
    return errors
