"""Entity resolution stage UI."""

from __future__ import annotations

import streamlit as st

from app.models.entities import Entity
from app.models.state import UnifiedRunState


def render_resolution_stage(state: UnifiedRunState) -> tuple[bool, str | None, str | None]:
    """
    Show ambiguous entity candidates for manual selection.

    Returns (confirmed, drug_id, disease_id).
    """
    st.info("Ambiguous entities detected. Please confirm your selection.")

    with st.form("resolution_form"):
        c1, c2 = st.columns(2)

        d_sel = None
        dis_sel = None

        with c1:
            st.subheader("Drug Selection")
            if state.drug_entity:
                st.success(f"Auto-selected: **{state.drug_entity.name}**")
                d_sel = state.drug_entity.id
            else:
                if not state.drug_candidates:
                    st.error("No drug candidates found.")
                else:
                    opts = {
                        f"{c.name} (Score: {c.score:.2f})": c.id
                        for c in state.drug_candidates
                    }
                    sel_label = st.radio("Choose Drug:", list(opts.keys()))
                    d_sel = opts.get(sel_label)

        with c2:
            st.subheader("Disease Selection")
            if state.disease_entity:
                st.success(f"Auto-selected: **{state.disease_entity.name}**")
                dis_sel = state.disease_entity.id
            else:
                if not state.disease_candidates:
                    st.error("No disease candidates found.")
                else:
                    opts = {
                        f"{c.name} (Score: {c.score:.2f})": c.id
                        for c in state.disease_candidates
                    }
                    sel_label = st.radio("Choose Disease:", list(opts.keys()))
                    dis_sel = opts.get(sel_label)

        confirmed = st.form_submit_button("Confirm & Analyze", use_container_width=True)

    return confirmed, d_sel, dis_sel


def apply_manual_resolution(state: UnifiedRunState, drug_id: str | None, disease_id: str | None) -> bool:
    """Apply manual selections. Returns True if both entities are resolved."""
    if not state.drug_entity and drug_id:
        cand = next((c for c in state.drug_candidates if c.id == drug_id), None)
        if cand:
            state.drug_entity = Entity(
                id=cand.id, name=cand.name, entity_type="drug", source_method="manual",
                confidence=cand.score, candidates=state.drug_candidates,
            )

    if not state.disease_entity and disease_id:
        cand = next((c for c in state.disease_candidates if c.id == disease_id), None)
        if cand:
            state.disease_entity = Entity(
                id=cand.id, name=cand.name, entity_type="disease", source_method="manual",
                confidence=cand.score, candidates=state.disease_candidates,
            )

    return bool(state.drug_entity and state.disease_entity)
