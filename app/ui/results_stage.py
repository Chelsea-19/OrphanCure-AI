"""Results stage UI — 7-tab results view."""

from __future__ import annotations

import json

import graphviz
import pandas as pd
import streamlit as st

from app.models.evidence import VerificationStatus
from app.models.state import UnifiedRunState
from app.reporting.report_builder import ReportBuilder
from app.ui.components import (
    confidence_badge,
    polarity_badge,
    render_metric_bar,
    verification_badge,
)


def render_results_stage(state: UnifiedRunState) -> None:
    """Render the full results view with 7 tabs."""

    if st.button("New Search"):
        for key in list(st.session_state.keys()):
            if key.startswith("run_state"):
                del st.session_state[key]
        st.rerun()

    # If running in disease_only discovery mode, route to the Workbench view
    if state.input_mode == "disease_only":
        _render_discovery_workbench(state)
        return

    # Build the structured report (1v1 mode)
    builder = ReportBuilder(state)
    structured_report = builder.build()

    # Top-level metrics
    _render_top_metrics(state)

    # 7 tabs
    tabs = st.tabs([
        "Summary",
        "Mechanisms",
        "Literature",
        "Claims & Verification",
        "Quality Scorecard",
        "Run Trace / Logs",
        "Export / JSON",
    ])

    with tabs[0]:
        _tab_summary(state, structured_report)
    with tabs[1]:
        _tab_mechanisms(state, structured_report)
    with tabs[2]:
        _tab_literature(state, structured_report)
    with tabs[3]:
        _tab_claims(state)
    with tabs[4]:
        _tab_scorecard(state)
    with tabs[5]:
        _tab_logs(state)
    with tabs[6]:
        _tab_export(state, structured_report)


# ==================================================================
# Top metrics row
# ==================================================================

def _render_top_metrics(state: UnifiedRunState) -> None:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Overlap Targets", len(state.common_targets))
    m2.metric("Papers Retrieved", state.evidence_matrix.total_retrieved)
    m3.metric("Supporting", state.evidence_matrix.supports)
    m4.metric("Contradicting", state.evidence_matrix.contradicts)

    vs = state.final_report.get("verification_summary", {}).get("status", "N/A")
    m5.metric("Verification", vs)


# ==================================================================
# Workbench Rendering (Disease-Only Discovery Mode)
# ==================================================================

def _render_discovery_workbench(state: UnifiedRunState) -> None:
    st.subheader(f"Repurposing Workbench for {state.disease_entity.name}")
    st.caption("Candidates mathematically ranked by mechanism fit, literature proxy, and translational feasibility.")
    
    tabs = st.tabs(["Top Ranked Candidates", "Discovery Logs", "Export"])
    
    with tabs[0]:
        if not state.generated_candidates:
            st.info("No candidates generated or ranked.")
        else:
            for cand in state.generated_candidates:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"### {cand.name}")
                    col1.markdown(f"**Mechanism / Source:** {cand.mechanism_category}")
                    col1.markdown(f"**Rationale:** {cand.rationale}")
                    
                    # Rendering priority visually
                    p_cls = cand.priority_class
                    color = "green" if "1" in p_cls else ("orange" if "2" in p_cls else "red" if "3" in p_cls else "gray")
                    col2.markdown(f"#### Priority: :{color}[{p_cls}]")
                    col2.markdown(f"**Composite Score:** `{cand.score:.2f}`")
                    
                    brk = cand.ranking_breakdown
                    col1.caption(
                        f"Fit: {brk.mechanism_fit:.1f}/10 | "
                        f"Evid: {brk.evidence_strength:.1f}/10 | "
                        f"Safety: {brk.safety_feasibility:.1f}/10 | "
                        f"Readiness: {brk.translational_readiness:.1f}/10 | "
                        f"Contra: {brk.contradiction_burden:.1f}/10"
                    )
                    
                    if cand.evidence_gaps:
                        col1.warning("Evidence Gaps: " + ", ".join(cand.evidence_gaps))
                    
                    if st.button("Deep Evaluate 1v1", key=f"eval_{cand.id}"):
                        state.input_mode = "drug_and_disease"
                        state.drug_input = cand.name
                        
                        from app.models.entities import Entity, AliasExpansion
                        state.drug_entity = Entity(
                            id=cand.id,
                            name=cand.name,
                            entity_type="drug",
                            source_method="candidate_workbench",
                            confidence=1.0,
                            aliases=AliasExpansion(canonical_name=cand.name)
                        )
                        state.common_targets = []
                        state.drug_data = {}
                        state.papers = []
                        state.retrieval_queries = []
                        state.draft_claims = []
                        state.verified_claims = []
                        state.final_report = {}
                        from app.models.evidence import EvidenceMatrixSummary
                        state.evidence_matrix = EvidenceMatrixSummary()
                        
                        state.stage = "analysis"
                        st.rerun()
    
    with tabs[1]:
        _tab_logs(state)
        
    with tabs[2]:
        state_json = state.export_json()
        st.download_button(
            "Download Full Workbench State JSON",
            state_json,
            f"orphancure_workbench_state_{state.run_id}.json",
            "application/json",
            use_container_width=True,
        )


# ==================================================================
# Tab 1: Summary
# ==================================================================

def _tab_summary(state: UnifiedRunState, report: dict) -> None:
    sections = report.get("sections", {})
    exec_sum = sections.get("1_executive_summary", {})

    col1, col2 = st.columns([3, 1])
    col1.subheader(f"Conclusion: {exec_sum.get('conclusion', 'N/A')}")
    col2.metric("Confidence", exec_sum.get("confidence", "N/A"))

    if exec_sum.get("summary"):
        st.markdown(exec_sum["summary"])

    # Risk flags
    risk_section = sections.get("8_risk_flags_limitations", {})
    flags = risk_section.get("risk_flags", [])
    if flags:
        st.warning(f"**Risk Flags:** {', '.join(flags)}")

    limitations = risk_section.get("limitations", [])
    if limitations:
        st.info(f"**Limitations:** {', '.join(limitations)}")

    # Evidence counts
    st.divider()
    ec = exec_sum.get("evidence_counts", {})
    st.markdown(
        f"**Evidence:** {ec.get('total_papers', 0)} papers — "
        f"{ec.get('supporting', 0)} supporting, "
        f"{ec.get('contradicting', 0)} contradicting, "
        f"{ec.get('inconclusive', 0)} inconclusive"
    )

    # Normalized hypothesis
    hyp = sections.get("2_normalized_hypothesis", {})
    with st.expander("Normalized Hypothesis"):
        st.json(hyp)

    # Confidence assessment
    conf = sections.get("7_confidence_assessment", {})
    with st.expander("Confidence Assessment"):
        st.json(conf.get("dimensions", {}))

    # Next steps
    steps = sections.get("9_recommended_next_steps", {}).get("clinical_next_steps", [])
    if steps:
        st.subheader("Recommended Next Steps")
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. {step}")


# ==================================================================
# Tab 2: Mechanisms
# ==================================================================

def _tab_mechanisms(state: UnifiedRunState, report: dict) -> None:
    sections = report.get("sections", {})
    mech = sections.get("3_mechanistic_rationale", {})

    st.subheader(f"Mechanistic Rationale ({mech.get('total_mechanisms', 0)} mechanisms)")

    # Table
    if state.common_targets:
        df = pd.DataFrame([
            {
                "Symbol": t.symbol,
                "Name": t.name,
                "Drug Action": t.drug_action,
                "Disease Score": round(t.disease_assoc_score, 3),
            }
            for t in state.common_targets
        ])
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Pathway summaries
    if state.mechanism_evidence:
        with st.expander("Pathway Summaries"):
            for me in state.mechanism_evidence:
                if me.pathway_summary:
                    st.markdown(f"**{me.target_symbol}:** {me.pathway_summary}")

    # Graph
    st.divider()
    st.subheader("Target Overlap Graph")
    if state.common_targets and state.drug_entity and state.disease_entity:
        g = graphviz.Digraph()
        g.attr(rankdir="LR")
        g.node("D", state.drug_entity.name, shape="box", style="filled", fillcolor="#E3F2FD")
        g.node("Dis", state.disease_entity.name, shape="box", style="filled", fillcolor="#FFEBEE")
        for t in state.common_targets[:10]:
            g.node(t.symbol, t.symbol, style="filled", fillcolor="#F3E5F5")
            g.edge("D", t.symbol, label=t.drug_action[:15] if t.drug_action != "Unknown" else "")
            g.edge(t.symbol, "Dis")
        st.graphviz_chart(g)


# ==================================================================
# Tab 3: Literature
# ==================================================================

def _tab_literature(state: UnifiedRunState, report: dict) -> None:
    sections = report.get("sections", {})
    lit = sections.get("5_literature_evidence_summary", {})

    st.subheader("Literature Evidence")
    st.markdown(f"**{lit.get('support_ratio', 'N/A')}**")
    st.caption(f"Queries used: {lit.get('queries_used', 0)}")

    # Papers table
    if state.papers:
        df = pd.DataFrame([
            {
                "PMID": p.pmid,
                "Title": p.title[:80] + ("..." if len(p.title) > 80 else ""),
                "Year": p.year,
                "Score": round(p.relevance_score, 1),
                "Polarity": p.polarity.value,
                "Reasons": ", ".join(p.match_reasons),
            }
            for p in state.papers[:20]
        ])
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Detailed reranking scores
    with st.expander("Reranking Score Breakdown"):
        if state.papers:
            for p in state.papers[:5]:
                st.markdown(f"**PMID:{p.pmid}** — {p.title[:60]}...")
                scores = p.reranking
                cols = st.columns(4)
                cols[0].caption(f"Drug: {scores.drug_mention:.1f}")
                cols[1].caption(f"Disease: {scores.disease_mention:.1f}")
                cols[2].caption(f"Target: {scores.target_overlap:.1f}")
                cols[3].caption(f"Clinical: {scores.clinical_signal:.1f}")
                st.divider()

    # Query log
    with st.expander("Retrieval Queries"):
        for q in state.retrieval_queries:
            st.caption(f"[{q.query_type}] {q.result_count} results")
            st.code(q.query_string, language="text")

    # Contradictory evidence
    contra = sections.get("6_contradictory_evidence", {})
    if contra.get("count", 0) > 0:
        st.divider()
        st.subheader(f"Contradictory Evidence ({contra['count']})")
        for c in contra.get("claims", []):
            st.markdown(f"- {c['statement']}")


# ==================================================================
# Tab 4: Claims & Verification
# ==================================================================

def _tab_claims(state: UnifiedRunState) -> None:
    claims = state.verified_claims or state.draft_claims

    st.subheader(f"Claims & Verification ({len(claims)} claims)")

    if not claims:
        st.info("No claims generated yet.")
        return

    for claim in claims:
        badge = verification_badge(claim.verification_status.value)
        pol = polarity_badge(claim.polarity.value)
        conf = confidence_badge(claim.confidence_label)

        with st.container(border=True):
            header_col, badge_col = st.columns([4, 1])
            header_col.markdown(f"**{badge} {claim.claim_id}:** {claim.statement}")
            badge_col.markdown(f"{pol} | {conf}")

            st.caption(
                f"Confidence: {claim.confidence_numeric:.2f} | "
                f"Targets: {', '.join(claim.supported_targets) if claim.supported_targets else 'N/A'}"
            )

            # Paper evidence
            for pe in claim.provenance.paper_evidence:
                v_badge = verification_badge(pe.verification_status.value)
                if pe.verification_error:
                    st.markdown(f"  {v_badge} PMID:{pe.pmid} — :red[{pe.verification_error}]")
                else:
                    st.markdown(f"  {v_badge} PMID:{pe.pmid} — *\"{pe.evidence_snippet[:150]}...\"*")

            # Risk flags
            if claim.risk_flags:
                st.warning(f"Risk: {', '.join(claim.risk_flags)}")


# ==================================================================
# Tab 5: Quality Scorecard
# ==================================================================

def _tab_scorecard(state: UnifiedRunState) -> None:
    sc = state.scorecard
    st.subheader(f"Quality Scorecard — Overall: {sc.overall_score:.2f}")

    col1, col2 = st.columns([2, 1])

    with col1:
        for dim in sc.dimensions:
            color = "#4CAF50" if dim.score >= 0.7 else ("#FF9800" if dim.score >= 0.4 else "#F44336")
            render_metric_bar(dim.name.replace("_", " ").title(), dim.score, color=color)
            if dim.reason:
                st.caption(f"  ↳ {dim.reason}")

    with col2:
        st.metric("Decision", sc.decision.upper())
        if sc.weak_dimensions:
            st.warning(f"Weak: {', '.join(sc.weak_dimensions)}")
        if sc.rerun_targets:
            st.info(f"Rerun targets: {', '.join(sc.rerun_targets)}")

    # Rerun history
    if state.rerun_history:
        st.divider()
        st.subheader("Rerun History")
        for rr in state.rerun_history:
            st.markdown(
                f"**{rr.rerun_id}** — {rr.reason} | "
                f"Agents: {', '.join(rr.target_agents)} | "
                f"Weak: {', '.join(rr.weak_dimensions)}"
            )


# ==================================================================
# Tab 6: Run Trace / Logs
# ==================================================================

def _tab_logs(state: UnifiedRunState) -> None:
    st.subheader(f"Run Trace ({len(state.logs)} entries)")
    st.caption(f"Run ID: {state.run_id} | Created: {state.created_at}")

    # Filter
    agents = sorted(set(log.agent for log in state.logs))
    selected_agent = st.selectbox("Filter by agent:", ["All"] + agents)

    for log in state.logs:
        if selected_agent != "All" and log.agent != selected_agent:
            continue

        icon = "[INFO]" if log.status == "INFO" else ("[WARN]" if log.status == "WARN" else "[ERR]")
        st.text(f"{log.timestamp} {icon} [{log.agent}] {log.message}")

    # UI messages
    if state.ui_messages:
        st.divider()
        st.subheader("UI Messages")
        for msg in state.ui_messages:
            st.info(msg)


# ==================================================================
# Tab 7: Export / JSON
# ==================================================================

def _tab_export(state: UnifiedRunState, structured_report: dict) -> None:
    st.subheader("Export")

    col1, col2 = st.columns(2)

    with col1:
        # Full state JSON
        state_json = state.export_json()
        st.download_button(
            "Download Full State JSON",
            state_json,
            f"orphancure_state_{state.run_id}.json",
            "application/json",
            use_container_width=True,
        )

    with col2:
        # Structured report JSON
        report_json = json.dumps(structured_report, indent=2, default=str)
        st.download_button(
            "Download Structured Report",
            report_json,
            f"orphancure_report_{state.run_id}.json",
            "application/json",
            use_container_width=True,
        )

    # Raw state inspector
    with st.expander("Raw State Inspector"):
        st.json(json.loads(state.export_json()))
