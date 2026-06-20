"""Public Streamlit demo for OrphanCure.

The demo is intentionally evidence-summary only. It does not call biomedical
APIs unless future developers explicitly add that behavior.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
UNIFIED_DIR = ROOT / "eval_results_sample" / "unified"
FULL_PIPELINE_DIR = ROOT / "eval_results_sample" / "full_pipeline"
SCALING_DIR = ROOT / "eval_results_sample" / "scaling_comparison"
FIGURES_DIR = ROOT / "docs" / "figures"
CASE_STUDIES_DIR = ROOT / "docs" / "case_studies"
DISCLAIMER = (
    "This demo is for research and educational purposes only. It is not medical "
    "advice and must not be used for clinical decision-making."
)


FALLBACK_COVERAGE = {
    "Open Targets availability": 0.25,
    "Graph availability": 0.25,
    "Both evidence layers available": 0.25,
    "OT disease resolution": 0.82,
    "Graph disease mapping": 0.16,
    "Target overlap": 0.18,
    "Graph path recovery": 0.12,
}


FALLBACK_BASELINES = pd.DataFrame(
    [
        {"mode": "opentargets_only", "accuracy": 0.50, "f1": 0.667, "roc_auc": 0.5216, "status": "completed"},
        {"mode": "graph_only", "accuracy": 0.50, "f1": 0.667, "roc_auc": 0.5432, "status": "completed"},
        {"mode": "ot_plus_graph", "accuracy": 0.50, "f1": 0.667, "roc_auc": 0.5664, "status": "completed"},
        {"mode": "heuristic_combined", "accuracy": 0.50, "f1": 0.667, "roc_auc": 0.5712, "status": "completed"},
    ]
)


FALLBACK_SCALING = pd.DataFrame(
    [
        {
            "run_name": "20_pair",
            "n_selected": 20,
            "n_completed": 16,
            "n_partial_success": 4,
            "n_failed": 0,
            "original_F1": 0.4,
            "best_score_name": "safety_penalized_score",
            "best_score_F1": 0.72,
            "triage_coverage": 0.65,
            "triage_accuracy_on_covered": 0.6154,
            "unsupported_claim_rate": 0.0625,
            "no_verifier_unsupported_claim_rate": 1.0,
            "notes": "Bundled fallback from the 20-pair diagnostic run.",
        },
        {
            "run_name": "50_pair",
            "n_selected": 50,
            "n_completed": 0,
            "n_partial_success": 0,
            "n_failed": 0,
            "notes": "TODO_NOT_RUN unless scaled full-agent artifacts are bundled.",
        },
    ]
)


def load_baselines() -> pd.DataFrame:
    path = UNIFIED_DIR / "baseline_comparison.csv"
    if path.exists():
        return pd.read_csv(path)
    return FALLBACK_BASELINES.copy()


def load_scaling_summary() -> pd.DataFrame:
    path = SCALING_DIR / "scaling_summary.csv"
    if path.exists():
        return pd.read_csv(path)
    return FALLBACK_SCALING.copy()


def load_selected_cases() -> pd.DataFrame:
    path = CASE_STUDIES_DIR / "selected_cases.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(
        [
            {
                "pair_id": "repodb_0557bc43eff59f45",
                "drug_name": "Theophylline",
                "disease_name": "Asthma",
                "case_type": "correct_positive",
                "full_status": "completed",
                "manual_review_status": "TODO_MANUAL_REVIEW",
                "case_file": "case_01_correct_positive.md",
            },
            {
                "pair_id": "repodb_04246cb3a1c31ef7",
                "drug_name": "Progesterone",
                "disease_name": "Premature Birth",
                "case_type": "verifier_effect",
                "full_status": "completed",
                "manual_review_status": "TODO_MANUAL_REVIEW",
                "case_file": "case_03_verifier_effect.md",
            },
        ]
    )


def load_case_markdown(case_file: str) -> str:
    path = CASE_STUDIES_DIR / str(case_file)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "Detailed case-study markdown is not bundled for this row. "
        "Use `docs/case_studies/selected_cases.csv` for metadata."
    )


def render_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="OrphanCure Research Demo", layout="wide")
    demo_mode = os.getenv("DEMO_MODE", "true").strip().lower() != "false"

    st.title("OrphanCure")
    st.caption("Benchmark-driven evidence assessment for rare-disease drug repurposing")
    st.warning(DISCLAIMER)

    if demo_mode:
        st.info("Demo mode is active. No API keys, PubMed calls, Open Targets calls, or large graph files are required.")
    else:
        st.info("Configured non-demo mode. This release app still displays summaries only unless extended.")

    tab_overview, tab_benchmark, tab_results, tab_pubmed, tab_full, tab_scaling, tab_cases, tab_try, tab_limits = st.tabs(
        [
            "Overview",
            "Benchmarks",
            "Results",
            "PubMed",
            "Full Pipeline",
            "Scaling Diagnostics",
            "Case Studies",
            "Demo Pair",
            "Limitations",
        ]
    )

    with tab_overview:
        st.subheader("Project Overview")
        st.write(
            "OrphanCure organizes repoDB proxy labels, Open Targets target evidence, "
            "and PrimeKG graph mechanism features into a unified benchmark table. "
            "The current website presents evaluated evidence-only baselines, not clinical predictions."
        )
        render_image(FIGURES_DIR / "orphancure_pipeline.png", "OrphanCure system pipeline")

        st.subheader("System Pipeline")
        st.markdown(
            """
            1. repoDB provides approved/failed proxy benchmark labels.
            2. Open Targets provides target-evidence support features.
            3. PrimeKG provides graph mapping and short-path mechanism features.
            4. The unified table preserves every `pair_id` and marks missing evidence.
            5. Deterministic baselines compare evidence scores against repoDB proxy labels.
            """
        )

    with tab_benchmark:
        st.subheader("Benchmark Summary")
        cols = st.columns(4)
        cols[0].metric("repoDB pairs", "200")
        cols[1].metric("Open Targets pairs", "50")
        cols[2].metric("PrimeKG nodes", "84,289")
        cols[3].metric("PrimeKG edges", "4.13M")
        render_image(FIGURES_DIR / "benchmark_design.png", "Benchmark design")

        st.subheader("Evidence Coverage")
        coverage = FALLBACK_COVERAGE
        coverage_df = pd.DataFrame({"metric": list(coverage.keys()), "value": list(coverage.values())})
        st.dataframe(coverage_df, use_container_width=True, hide_index=True)
        render_image(FIGURES_DIR / "evidence_coverage_summary.png", "Evidence coverage summary")

    with tab_results:
        st.subheader("Unified Baseline Comparison")
        baselines = load_baselines()
        visible_cols = [col for col in ["mode", "status", "accuracy", "precision", "recall", "f1", "roc_auc", "n_evaluated_pairs", "n_skipped_pairs"] if col in baselines.columns]
        st.dataframe(baselines[visible_cols], use_container_width=True, hide_index=True)
        render_image(FIGURES_DIR / "unified_baseline_comparison.png", "Unified baseline comparison")
        render_image(FIGURES_DIR / "ot_vs_graph_score_scatter.png", "Open Targets vs graph score scatter")
        st.write(
            "Current baselines are sanity checks over the 50 evidence-covered pairs. "
            "They should not be interpreted as validated biomedical prediction models."
        )

    with tab_pubmed:
        st.subheader("PubMed-Only Baseline")
        st.write(
            "Phase 6B adds a PubMed-only retrieval baseline. It uses fixed NCBI "
            "E-utilities query buckets and a transparent co-mention score. Demo mode "
            "does not call PubMed and does not require an NCBI key."
        )
        st.markdown(
            """
            Query buckets:

            - direct drug-disease co-mention
            - title/abstract co-mention
            - clinical terms: trial, clinical, patient, therapy
            - negative terms: failed, ineffective, toxicity, adverse, discontinued
            - mechanism terms: mechanism, target, pathway
            """
        )
        st.warning(
            "Literature co-mention is not evidence of efficacy. The current release "
            "does not perform abstract polarity classification."
        )
        pubmed_dir = ROOT / "eval_results_sample" / "pubmed"
        pubmed_summary = pubmed_dir / "summary_metrics.json"
        if pubmed_summary.exists():
            st.json(pubmed_summary.read_text(encoding="utf-8"))
        else:
            st.info("No real PubMed sample output is bundled yet. Live PubMed evaluation is TODO_NOT_RUN until configured.")

    with tab_full:
        st.subheader("Full Pipeline Evaluation")
        st.write(
            "Phase 6C adds an evaluation harness for the full OrphanCure agent: "
            "PubMed retrieval, Open Targets evidence, PrimeKG mechanisms, LLM "
            "synthesis, claim verification, quality gating, and report generation."
        )
        st.write(
            "The bundled sample reflects a selected 20-pair full-agent run after "
            "debugging missing Open Targets mechanism details. Rows marked "
            "`partial_success` are retained for audit."
        )
        st.markdown(
            """
            Supported evaluation modes:

            - `full`
            - `no_verifier`
            - `no_target_expansion`
            - `no_graph_features`
            - `pubmed_only_report`
            - `structured_only_report`
            """
        )
        full_results = FULL_PIPELINE_DIR / "per_pair_results_full.csv"
        if full_results.exists():
            full_df = pd.read_csv(full_results)
            st.dataframe(
                full_df[[col for col in ["pair_id", "mode", "status", "error_message"] if col in full_df.columns]].head(20),
                use_container_width=True,
                hide_index=True,
            )
            if (full_df.get("status", pd.Series(dtype=str)) == "TODO_NOT_RUN").all():
                st.info("The bundled full-pipeline output is a TODO_NOT_RUN artifact because no LLM key was configured.")
        else:
            st.info("No full-pipeline output is bundled. Full-agent evaluation remains TODO_NOT_RUN until configured.")
        claim_summary = FULL_PIPELINE_DIR / "claim_verification_summary.csv"
        if claim_summary.exists():
            st.subheader("Claim Verification Summary")
            st.dataframe(pd.read_csv(claim_summary).head(20), use_container_width=True, hide_index=True)
        render_image(FIGURES_DIR / "full_pipeline_vs_baselines.png", "Full pipeline vs evidence baselines")
        render_image(FIGURES_DIR / "claim_verification_summary.png", "Claim verification summary")
        render_image(FIGURES_DIR / "full_pipeline_ablation_summary.png", "Full pipeline ablation summary")
        st.warning(
            "Generated reports, if enabled later, are research artifacts requiring "
            "manual biomedical review. They are not clinical recommendations."
        )

    with tab_scaling:
        st.subheader("Scaling Diagnostics")
        st.write(
            "Phase 6F prepares 50- and 100-pair full-agent evaluation cohorts so "
            "threshold calibration, alternative scoring, triage, and verifier-effect "
            "estimates can be tested beyond the original 20-pair run."
        )
        scaling = load_scaling_summary()
        visible_cols = [
            col
            for col in [
                "run_name",
                "n_selected",
                "n_completed",
                "n_partial_success",
                "n_failed",
                "original_F1",
                "best_score_name",
                "best_score_F1",
                "triage_coverage",
                "triage_accuracy_on_covered",
                "unsupported_claim_rate",
                "no_verifier_unsupported_claim_rate",
                "notes",
            ]
            if col in scaling.columns
        ]
        st.dataframe(scaling[visible_cols], use_container_width=True, hide_index=True)
        render_image(FIGURES_DIR / "scaling_f1_comparison.png", "Scaling F1 comparison")
        render_image(FIGURES_DIR / "scaling_roc_auc_comparison.png", "Scaling ROC-AUC comparison")
        render_image(FIGURES_DIR / "scaling_triage_coverage_accuracy.png", "Scaling triage coverage and accuracy")
        render_image(FIGURES_DIR / "scaling_verifier_effect.png", "Scaling verifier effect")
        st.write(
            "The current public-safe bundle may show 50/100 rows as TODO_NOT_RUN. "
            "That means selected cohorts exist, but real full-agent reports were not "
            "generated in the bundled environment."
        )
        st.warning(
            "Scaling diagnostics compare research-support evidence artifacts against "
            "repoDB proxy labels. They are not clinical validation."
        )

    with tab_cases:
        st.subheader("Case Studies")
        st.write(
            "Phase 6D selected representative full-agent outputs for manual "
            "review. These cases illustrate evidence grounding, verifier behavior, "
            "incorrect-but-informative outputs, and partial-success handling."
        )
        cases = load_selected_cases()
        display_cols = [
            col
            for col in [
                "pair_id",
                "drug_name",
                "disease_name",
                "case_type",
                "full_status",
                "manual_review_status",
            ]
            if col in cases.columns
        ]
        st.dataframe(cases[display_cols], use_container_width=True, hide_index=True)
        if not cases.empty:
            labels = [
                f"{row.get('case_type', 'case')} | {row.get('drug_name', '')} / {row.get('disease_name', '')}"
                for _, row in cases.iterrows()
            ]
            selected_label = st.selectbox("Selected case", labels)
            selected_idx = labels.index(selected_label)
            row = cases.iloc[selected_idx]
            st.markdown(load_case_markdown(str(row.get("case_file", ""))))
        st.warning(
            "All case studies remain TODO_MANUAL_REVIEW. They are research-support "
            "artifacts, not medical advice or clinical evidence."
        )

    with tab_try:
        st.subheader("Research Pair Demo")
        drug = st.text_input("Drug", value="Example Drug")
        disease = st.text_input("Disease", value="Example Disease")
        if st.button("Generate demo assessment"):
            st.markdown(f"**Input pair:** {drug} / {disease}")
            st.write(
                "Demo response: no live biomedical lookup was run. In a configured research workflow, "
                "this pair would be checked against repoDB-style labels, Open Targets evidence, graph "
                "mechanism features, PubMed literature, and verifier outputs."
            )
            st.warning("No medical or treatment claim is generated.")

    with tab_limits:
        st.subheader("Limitations")
        st.markdown(
            """
            - repoDB is a proxy approved/failed benchmark, not clinical truth.
            - Open Targets support is target evidence support, not proof of efficacy.
            - PrimeKG graph connectivity is mechanism support, not proof of efficacy.
            - Current Open Targets and graph coverage is 50 of 200 repoDB pairs.
            - Full-agent ablations are TODO_NOT_RUN until `GEMINI_API_KEY` is configured and real reports are generated.
            - PubMed co-mentions are not evidence of efficacy.
            - Manual biomedical review is still needed for case studies.
            """
        )
        st.error(DISCLAIMER)


if __name__ == "__main__":
    main()
