"""Streamlit research demo for OrphanCure.

The app is intentionally demo-first: it reads bundled summary artifacts and
does not call PubMed, Open Targets, LLM APIs, or graph services by default.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "docs" / "figures"
CASE_DIR = ROOT / "docs" / "case_studies"
PUBMED_DIR = ROOT / "eval_results_sample" / "pubmed"
FULL20_DIR = ROOT / "eval_results_sample" / "full_pipeline"
FULL50_DIR = ROOT / "eval_results_sample" / "full_pipeline_scaled_50"
DIAG50_DIR = FULL50_DIR / "diagnostics"
SCALING_DIR = ROOT / "eval_results_sample" / "scaling_comparison"
UNIFIED_DIR = ROOT / "eval_results_sample" / "unified"

DISCLAIMER = (
    "Research and educational demo only. Not medical advice, not clinical "
    "validation, and not for treatment recommendation or clinical decision-making."
)


def read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return fallback
    return fallback


def read_csv(path: Path, fallback: pd.DataFrame | None = None) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return fallback.copy() if fallback is not None else pd.DataFrame()


def metric_row(items: list[tuple[str, str | float | int, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def show_figure(name: str, caption: str) -> None:
    path = FIGURES_DIR / name
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"Figure placeholder: {caption} ({name})")


def show_table(path: Path, cols: list[str] | None = None, limit: int | None = None) -> None:
    df = read_csv(path)
    if df.empty:
        st.info(f"No bundled table found at `{path.relative_to(ROOT)}`.")
        return
    if cols:
        cols = [col for col in cols if col in df.columns]
        df = df[cols]
    if limit:
        df = df.head(limit)
    st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="OrphanCure Research Demo", layout="wide")
    demo_mode = os.getenv("DEMO_MODE", "true").strip().lower() != "false"

    st.title("OrphanCure")
    st.caption("Benchmark-driven biomedical AI agent evaluation for drug-disease evidence assessment")
    st.warning(DISCLAIMER)
    st.info(
        "Demo mode is active by default. This app reads bundled sample summaries "
        "and does not call live APIs or use API keys."
        if demo_mode
        else "DEMO_MODE=false was set, but this release app still renders bundled summaries only."
    )

    tabs = st.tabs(
        [
            "Overview",
            "Benchmark",
            "Evidence Layers",
            "PubMed Baseline",
            "Full Pipeline",
            "Scaling Diagnostics",
            "Case Studies",
            "Reports",
            "Limitations",
        ]
    )

    with tabs[0]:
        st.subheader("What this project does")
        st.write(
            "OrphanCure evaluates drug-disease assessment agents against repoDB "
            "proxy labels while grounding outputs in PubMed retrieval, Open "
            "Targets target evidence, PrimeKG mechanism features, LLM synthesis, "
            "claim verification, ablation analysis, and manually reviewable case studies."
        )
        metric_row(
            [
                ("repoDB pairs", "200", "Balanced benchmark: 100 positive and 100 negative_or_failed."),
                ("Scaled cohort", "50", "Selected full-agent cohort with 25 positive and 25 negative_or_failed rows."),
                ("Full 50 F1", "0.5333", "Original full-agent score, not clinical validation."),
                ("Verifier effect", "1.0 -> 0.1090", "Unsupported claim rate in no_verifier vs full mode on 50 pairs."),
            ]
        )
        show_figure("orphancure_pipeline.png", "Pipeline architecture")
        st.markdown(
            """
            **Why it is not just an LLM wrapper**

            - Benchmark layer: repoDB proxy labels and dev/test split.
            - Evidence layers: PubMed, Open Targets, and PrimeKG features.
            - Agent layer: synthesis plus explicit claim verification.
            - Diagnostics: ablations, alternative scoring, calibration, triage, and error analysis.
            - Release layer: public-safe demo artifacts without raw external data or secrets.
            """
        )

    with tabs[1]:
        st.subheader("Benchmark")
        metric_row(
            [
                ("Total pairs", "200", None),
                ("Positive", "100", None),
                ("Negative/failed", "100", "repoDB failed/withdrawn/discontinued labels are proxy labels."),
                ("Split", "dev/test", "Used for calibration and held-out evaluation where applicable."),
            ]
        )
        show_figure("benchmark_design.png", "Benchmark design")
        show_table(
            ROOT / "data_sample" / "benchmark" / "repodb_pairs.csv",
            ["pair_id", "drug_name", "disease_name", "label", "split"],
            25,
        )

    with tabs[2]:
        st.subheader("Evidence Layers")
        st.markdown(
            """
            PubMed provides literature retrieval features, Open Targets provides
            target evidence, and PrimeKG provides graph mechanism features. These
            are support signals, not proof of therapeutic efficacy.
            """
        )
        metric_row(
            [
                ("PubMed rows", "50 pair features", "2,149 PubMed evidence rows were produced in the source repo."),
                ("Unique PMIDs", "1,058", "Global unique PMIDs in the PubMed evidence run."),
                ("OT rows", "50", "Earlier 50-pair Open Targets enrichment."),
                ("Graph rows", "50", "Earlier 50-pair PrimeKG feature run."),
            ]
        )
        metric_row(
            [
                ("PubMed availability", "37/50", "Evidence-available pairs in earlier PubMed feature run."),
                ("OT drug resolution", "1.00", None),
                ("OT disease resolution", "0.82", None),
                ("Graph path recovery", "0.12", None),
            ]
        )
        show_figure("evidence_coverage_summary.png", "Evidence coverage summary")
        show_table(PUBMED_DIR / "per_pair_features.csv", limit=15)
        ot_summary = ROOT / "eval_results_sample" / "opentargets" / "summary_table.md"
        if ot_summary.exists():
            st.markdown(ot_summary.read_text(encoding="utf-8"))

    with tabs[3]:
        st.subheader("PubMed Baseline")
        pubmed_metrics = read_json(PUBMED_DIR / "summary_metrics.json", {})
        if pubmed_metrics:
            st.json(pubmed_metrics)
        show_table(PUBMED_DIR / "per_pair_results.csv", limit=25)
        show_figure("pubmed_baseline_comparison.png", "PubMed baseline comparison")
        show_figure("pubmed_evidence_by_label.png", "PubMed evidence by label")
        st.warning("PubMed co-mention is not evidence of efficacy.")

    with tabs[4]:
        st.subheader("Full Pipeline")
        metric_row(
            [
                ("20 selected", "20", None),
                ("20 completed", "16", "4 partial_success, 0 failed."),
                ("20 original F1", "0.4000", None),
                ("20 unsupported", "0.0625", "Full verifier mode unsupported claim rate."),
            ]
        )
        metric_row(
            [
                ("50 selected", "50", "25 positive / 25 negative_or_failed."),
                ("50 completed", "42", "8 partial_success, 0 failed."),
                ("50 original F1", "0.5333", None),
                ("Mean runtime", "28.2992s", "Mean runtime over the 50-pair scaled run."),
            ]
        )
        st.json(read_json(FULL50_DIR / "summary_metrics_full.json", {}))
        show_table(
            FULL50_DIR / "per_pair_results_full.csv",
            ["pair_id", "drug_name", "disease_name", "expected_label", "status", "predicted_label", "confidence_score"],
            25,
        )
        show_figure("full_pipeline_vs_baselines.png", "Full pipeline vs baselines")
        show_figure("full_pipeline_ablation_summary.png", "Full pipeline ablation summary")

    with tabs[5]:
        st.subheader("Scaling Diagnostics")
        show_table(SCALING_DIR / "scaling_summary.csv")
        st.subheader("Alternative score comparison")
        show_table(DIAG50_DIR / "alternative_score_comparison.csv")
        metric_row(
            [
                ("Best score", "safety_penalized_score", None),
                ("Threshold", "0.1331279222", "Dev-split exploratory small-n threshold."),
                ("F1", "0.7018", "50-pair alternative score result."),
                ("ROC-AUC", "0.6464", "50-pair alternative score result."),
            ]
        )
        metric_row(
            [
                ("Triage coverage", "0.50", None),
                ("Triage abstention", "0.50", None),
                ("Covered accuracy", "0.64", None),
                ("F1 on covered", "0.40", None),
            ]
        )
        show_figure("scaling_f1_comparison.png", "Scaling F1 comparison")
        show_figure("scaling_roc_auc_comparison.png", "Scaling ROC-AUC comparison")
        show_figure("scaling_verifier_effect.png", "Scaling verifier effect")
        show_figure("scaling_triage_coverage_accuracy.png", "Triage coverage and accuracy")

    with tabs[6]:
        st.subheader("Case Studies")
        cases = read_csv(CASE_DIR / "selected_cases.csv")
        display_cols = [
            "pair_id",
            "drug_name",
            "disease_name",
            "case_type",
            "full_status",
            "manual_review_status",
        ]
        if cases.empty:
            st.info("No selected case table is bundled.")
        else:
            st.dataframe(cases[[c for c in display_cols if c in cases.columns]], use_container_width=True, hide_index=True)
            labels = [
                f"{row.get('case_type', 'case')} | {row.get('drug_name', '')} - {row.get('disease_name', '')}"
                for _, row in cases.iterrows()
            ]
            selected = st.selectbox("Case", labels)
            row = cases.iloc[labels.index(selected)]
            case_file = CASE_DIR / str(row.get("case_file", ""))
            if case_file.exists():
                st.markdown(case_file.read_text(encoding="utf-8"))
        st.warning("All selected cases remain TODO_MANUAL_REVIEW.")

    with tabs[7]:
        st.subheader("Reports")
        st.markdown(
            """
            - Technical report: `docs/technical_report/main.tex`
            - Chinese interview notes: `docs/interview_notes/orphancure_interview_notes_zh.md`
            - Manuscript draft: `docs/manuscript/main.tex`
            - Portfolio one-pager: `docs/portfolio_one_pager.md`
            """
        )
        st.write(
            "The bundled LaTeX and Markdown documents are release artifacts. "
            "They intentionally preserve limitations, TODO_CITATION markers, and "
            "TODO_MANUAL_REVIEW status where review is incomplete."
        )

    with tabs[8]:
        st.subheader("Limitations and Safety")
        st.markdown(
            """
            - This is research support and education, not clinical validation.
            - It must not recommend treatments.
            - repoDB labels are proxy approved/failed labels, not clinical truth.
            - PubMed co-mention is not evidence of efficacy.
            - Open Targets and PrimeKG provide support signals, not proof of efficacy.
            - The selected cohorts are small.
            - LLM-generated case studies require expert manual review.
            """
        )
        st.error(DISCLAIMER)


if __name__ == "__main__":
    main()
