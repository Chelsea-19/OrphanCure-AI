"""Sidebar configuration panel."""

from __future__ import annotations

import streamlit as st

from app.config.settings import Settings


def render_sidebar(settings: Settings) -> dict:
    """Render the sidebar and return runtime config overrides."""
    with st.sidebar:
        st.header("Configuration")

        # API key status
        if settings.gemini_api_key:
            st.success("Gemini API key loaded")
        else:
            st.error("No Gemini API key — set GEMINI_API_KEY in .env")

        st.divider()

        # Model info
        st.caption(f"Default model: `{settings.default_model}`")
        st.caption(f"Fallback model: `{settings.fallback_model}`")

        st.divider()

        # Resolution thresholds
        st.subheader("Entity Resolution")
        th_score = st.slider(
            "Min Score (Auto-select)", 0.0, 1.0, settings.resolution_min_score, key="th_score"
        )
        th_delta = st.slider(
            "Min Delta (Auto-select)", 0.0, 0.5, settings.resolution_min_delta, key="th_delta"
        )

        st.divider()

        # PubMed params
        st.subheader("PubMed Parameters")
        year_start = st.number_input("Year Start", 2000, 2026, settings.pubmed_year_start, key="cfg_year")
        max_fetch = st.slider("Max Papers per query", 5, 50, settings.pubmed_max_fetch, key="cfg_max_fetch")
        use_expansion = st.checkbox("Target Expansion", settings.pubmed_target_expansion, key="cfg_expansion")

        st.divider()

        # Quality gate
        st.subheader("Quality Gate")
        quality_threshold = st.slider(
            "Quality Threshold", 0.0, 1.0, settings.quality_threshold, key="cfg_quality"
        )
        max_reruns = st.number_input("Max Reruns", 0, 5, settings.max_reruns, key="cfg_reruns")

        st.divider()

        # Reset
        if st.button("Reset State", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("run_state"):
                    del st.session_state[key]
            st.rerun()

    return {
        "resolution_min_score": th_score,
        "resolution_min_delta": th_delta,
        "pubmed_year_start": int(year_start),
        "pubmed_max_fetch": max_fetch,
        "pubmed_target_expansion": use_expansion,
        "quality_threshold": quality_threshold,
        "max_reruns": int(max_reruns),
    }
