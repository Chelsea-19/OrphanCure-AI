"""Shared helper utilities — rate limiting, text normalisation, etc."""

from __future__ import annotations

import random
import re
import time
from functools import wraps
from typing import Callable


# ------------------------------------------------------------------
# Rate limit decorator  (preserved from app6.py)
# ------------------------------------------------------------------

def rate_limit(min_interval: float = 0.3) -> Callable:
    """Decorator: simple per-function rate limiter."""

    def decorator(func: Callable) -> Callable:
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed + random.uniform(0, 0.1))
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper

    return decorator


# ------------------------------------------------------------------
# Text cleaning  (preserved from app6.py _verify_evidence)
# ------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove non-word characters and lowercase for fuzzy matching."""
    return re.sub(r"\W+", "", text).lower()


def normalize_text(text: str) -> str:
    """Light normalization: collapse whitespace, strip."""
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------------
# Safe JSON parsing
# ------------------------------------------------------------------

def safe_json_loads(raw: str, fallback: dict | list | None = None):
    """Try to parse JSON; return fallback on failure."""
    import json

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return fallback if fallback is not None else {}
