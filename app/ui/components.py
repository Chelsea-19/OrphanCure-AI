"""Shared UI components."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st


def render_metric_bar(label: str, value: float, max_val: float = 1.0, color: str = "#4CAF50") -> None:
    """Render a simple progress-style metric bar."""
    pct = min(value / max_val * 100, 100) if max_val > 0 else 0
    st.markdown(
        f"""
        <div style="margin-bottom: 4px;">
            <span style="font-size: 0.85em; color: #666;">{label}</span>
            <span style="float: right; font-size: 0.85em; font-weight: 600;">{value:.2f}</span>
        </div>
        <div style="background: #e0e0e0; border-radius: 4px; height: 8px; margin-bottom: 12px;">
            <div style="background: {color}; width: {pct:.0f}%; height: 100%; border-radius: 4px;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def verification_badge(status: str) -> str:
    """Return a colored text badge for verification status."""
    badges = {
        "VERIFIED": ":green[[VERIFIED]]",
        "PARTIALLY_VERIFIED": ":orange[[PARTIAL]]",
        "UNVERIFIED": ":red[[UNVERIFIED]]",
    }
    return badges.get(status, ":gray[[UNKNOWN]]")


def polarity_badge(polarity: str) -> str:
    """Return a colored label for evidence polarity."""
    badges = {
        "SUPPORTS": ":green[SUPPORTS]",
        "CONTRADICTS": ":red[CONTRADICTS]",
        "INCONCLUSIVE": ":orange[INCONCLUSIVE]",
    }
    return badges.get(polarity, polarity)


def confidence_badge(label: str) -> str:
    """Return colored confidence label."""
    colors = {
        "HIGH": ":green[HIGH]",
        "MEDIUM": ":orange[MEDIUM]",
        "LOW": ":red[LOW]",
    }
    return colors.get(label, label)
