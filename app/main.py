"""
OrphanCure-AI Pro — Streamlit Entry Point

Run with:
    cd d:\\OrphanCure
    streamlit run app/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root (parent of app/) is on sys.path so that
# `import app.xxx` works regardless of the CWD Streamlit uses.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import logging
from dataclasses import replace

import streamlit as st

from app.config.settings import Settings, load_settings, validate_settings
from app.models.state import UnifiedRunState
from app.orchestrator.pipeline import Pipeline
from app.services.llm_provider import GeminiProvider
from app.ui.input_stage import render_input_stage
from app.ui.resolution_stage import apply_manual_resolution, render_resolution_stage
from app.ui.results_stage import render_results_stage
from app.ui.sidebar import render_sidebar

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="OrphanCure-AI Pro",
    page_icon="OC",
    layout="wide",
)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------


def main() -> None:
    # 1. Load settings
    base_settings = load_settings()

    # 2. Validate
    errors = validate_settings(base_settings)

    # 3. Sidebar (returns runtime overrides)
    overrides = render_sidebar(base_settings)

    # Apply runtime overrides to settings
    settings = replace(
        base_settings,
        resolution_min_score=overrides["resolution_min_score"],
        resolution_min_delta=overrides["resolution_min_delta"],
        pubmed_year_start=overrides["pubmed_year_start"],
        pubmed_max_fetch=overrides["pubmed_max_fetch"],
        pubmed_target_expansion=overrides["pubmed_target_expansion"],
        quality_threshold=overrides["quality_threshold"],
        max_reruns=overrides["max_reruns"],
    )

    # 4. Init state
    if "run_state" not in st.session_state:
        st.session_state.run_state = UnifiedRunState()
    state: UnifiedRunState = st.session_state.run_state

    # 5. Title
    st.title("OrphanCure-AI Pro")
    st.caption("Multi-Agent Scientific Analysis System for Drug Repurposing")

    # 6. Show startup errors (but don't block UI)
    if errors:
        for err in errors:
            st.warning(f"{err}")

    # 7. LLM provider
    llm = GeminiProvider(settings)

    # 8. Stage routing
    if state.stage == "input":
        mode, drug, disease, submitted = render_input_stage(state)
        if submitted:
            state.input_mode = mode
            state.drug_input = drug
            state.disease_input = disease
            state.log("UI", f"Analysis started: {drug} -> {disease} [{mode}]")

            pipeline = Pipeline(state, llm, settings)
            with st.spinner("Running Wave 1: Entity Resolution + Mechanism Discovery..."):
                pipeline.run_wave1()

            # If auto-resolved, continue to Wave 2
            if state.stage == "analysis":
                with st.spinner("Running Wave 2: Literature + Synthesis + Quality Gate..."):
                    pipeline.run_wave2()

            st.rerun()

    elif state.stage == "resolution":
        confirmed, d_sel, dis_sel = render_resolution_stage(state)
        if confirmed:
            resolved = apply_manual_resolution(state, d_sel, dis_sel)
            if resolved:
                state.stage = "analysis"
                st.rerun()
            else:
                st.error("Selection incomplete — please select both drug and disease.")

    elif state.stage == "analysis":
        pipeline = Pipeline(state, llm, settings)
        with st.spinner("Running Phase 4: Mechanism Verification + Literature Retrieval + Quality Gate..."):
            pipeline.run_wave2()
        st.rerun()

    elif state.stage == "results":
        render_results_stage(state)

    # 9. Bottom logs (always visible)
    with st.expander("System Logs", expanded=False):
        for log_entry in state.logs:
            icon = "[INFO]" if log_entry.status == "INFO" else ("[WARN]" if log_entry.status == "WARN" else "[ERR]")
            st.text(f"{log_entry.timestamp} {icon} [{log_entry.agent}] {log_entry.message}")


if __name__ == "__main__":
    main()
