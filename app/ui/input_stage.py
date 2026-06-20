"""Input stage UI."""

from __future__ import annotations

import streamlit as st

from app.models.state import UnifiedRunState


def render_input_stage(state: UnifiedRunState) -> tuple[str, str, str, bool]:
    """Render the input form. Returns (mode, drug, disease, submitted)."""
    with st.container(border=True):
        mode = st.radio(
            "Analysis Mode",
            options=["drug_and_disease", "disease_only"],
            format_func=lambda x: "Deep 1v1 Evaluation (Drug + Disease)" if x == "drug_and_disease" else "Workbench Discovery (Disease Only)",
            horizontal=True
        )
        
        with st.form("input_form"):
            c1, c2 = st.columns(2)
            
            if mode == "drug_and_disease":
                drug_input = c1.text_input("Drug Name", value="Metformin", placeholder="e.g., Metformin, Imatinib")
            else:
                drug_input = ""
                
            disease_input = c2.text_input("Disease Name", value="Alzheimer's disease", placeholder="e.g., Alzheimer's disease")

            btn_label = "Generate & Rank Candidates" if mode == "disease_only" else "Start 1v1 Analysis"
            submitted = st.form_submit_button(btn_label, use_container_width=True)

    return mode, drug_input, disease_input, submitted
