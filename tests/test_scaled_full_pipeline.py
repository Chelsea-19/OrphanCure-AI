"""Tests for Phase 6F scaled full-pipeline utilities."""

from __future__ import annotations

from pathlib import Path

import importlib.util
import pandas as pd

from app.evaluation.full_pipeline_diagnostics import write_diagnostics
from app.evaluation.scaled_selection import evidence_availability_score, make_scaled_selection_outputs
from app.evaluation.scaling_comparison import build_scaling_summary


def fixture_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    split_rows = []
    unified_rows = []
    for idx in range(20):
        pair_id = f"p{idx:02d}"
        label = "positive" if idx % 2 == 0 else "negative_or_failed"
        split = "dev" if idx < 4 else "test"
        rows.append({"pair_id": pair_id, "drug_name": f"Drug {idx}", "disease_name": f"Disease {idx}", "expected_label": label})
        split_rows.append({"pair_id": pair_id, "split": split})
        unified_rows.append(
            {
                "pair_id": pair_id,
                "pubmed_available": idx < 8,
                "opentargets_available": idx < 12,
                "graph_available": idx < 10,
                "pubmed_evidence_score": 1.0 if idx < 8 else 0.0,
                "opentargets_support_score": 0.5 if idx < 12 else 0.0,
                "graph_connectivity_score": 0.25 if idx < 10 else 0.0,
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(split_rows), pd.DataFrame(unified_rows)


def test_evidence_availability_score_prioritizes_pubmed_then_structured_layers():
    _, _, unified = fixture_tables()
    scores = evidence_availability_score(unified)
    assert scores.iloc[0] > scores.iloc[9] > scores.iloc[13]


def test_scaled_selection_preserves_label_balance_and_split_rows():
    pairs, split, unified = fixture_tables()
    outputs = make_scaled_selection_outputs(pairs, split, unified, sizes=(10,), seed=7)
    selected = outputs[10]
    assert len(selected) == 10
    assert selected["expected_label"].value_counts().to_dict() == {"positive": 5, "negative_or_failed": 5}
    assert set(["dev", "test"]).issubset(set(selected["split"]))
    assert "evidence_availability_score" in selected.columns


def test_diagnostics_support_arbitrary_output_dir(tmp_path):
    results = pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Drug A",
                "disease_name": "Disease A",
                "expected_label": "positive",
                "mode": "full",
                "predicted_label": "positive",
                "confidence_score": 0.8,
                "status": "completed",
                "n_claims": 1,
                "n_verified_claims": 1,
                "n_unsupported_claims": 0,
                "citation_verified_rate": 1.0,
                "unsupported_claim_rate": 0.0,
                "n_pmids_used": 2,
                "n_opentargets_evidence_items": 1,
                "n_graph_paths_used": 1,
            }
        ]
    )
    unified = pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "split": "dev",
                "pubmed_available": True,
                "opentargets_available": True,
                "graph_available": True,
                "pubmed_evidence_score": 0.8,
                "opentargets_support_score": 0.4,
                "graph_connectivity_score": 0.3,
                "n_pmids_clinical": 2,
                "n_pmids_mechanism": 1,
                "n_pmids_negative": 0,
                "n_unique_pmids": 2,
            }
        ]
    )
    results_path = tmp_path / "results.csv"
    unified_path = tmp_path / "unified.csv"
    out_dir = tmp_path / "diagnostics"
    results.to_csv(results_path, index=False)
    unified.to_csv(unified_path, index=False)
    write_diagnostics(results_path, unified_path, out_dir, out_dir / "threshold_curve.png")
    assert (out_dir / "error_analysis_full.csv").exists()
    assert (out_dir / "triage_output.csv").exists()
    assert (out_dir / "threshold_curve.png").exists()


def test_scaling_comparison_generates_table_and_figures(tmp_path):
    run20 = tmp_path / "run20"
    run20.mkdir()
    pd.DataFrame(
        [
            {"pair_id": "p1", "status": "completed", "runtime_seconds": 1.0},
            {"pair_id": "p2", "status": "partial_success", "runtime_seconds": 2.0},
        ]
    ).to_csv(run20 / "per_pair_results_full.csv", index=False)
    (run20 / "summary_metrics_full.json").write_text(
        '{"accuracy":0.5,"precision":0.5,"recall":1.0,"f1":0.6667,"roc_auc":0.5,"citation_verified_rate":1.0,"unsupported_claim_rate":0.0,"mean_runtime_seconds":1.5}',
        encoding="utf-8",
    )
    pd.DataFrame([{"score_name": "safety_penalized_score", "f1": 0.7, "roc_auc": 0.6}]).to_csv(
        run20 / "alternative_score_comparison.csv", index=False
    )
    (run20 / "triage_metrics_full.json").write_text(
        '{"coverage_rate":0.8,"abstention_rate":0.2,"accuracy_on_covered_cases":0.75}',
        encoding="utf-8",
    )
    out_dir = tmp_path / "scaling"
    figures = tmp_path / "figures"
    summary = build_scaling_summary(
        [{"run_name": "20_pair", "run_dir": run20, "diagnostics_dir": run20}],
        out_dir,
        figures,
    )
    assert len(summary) == 1
    assert (out_dir / "scaling_summary.csv").exists()
    assert (figures / "scaling_f1_comparison.png").exists()


def test_streamlit_scaling_loader_falls_back():
    path = Path("orphancure_release/app/streamlit_app.py").resolve()
    spec = importlib.util.spec_from_file_location("release_streamlit_app", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.load_scaling_summary()
    assert "run_name" in summary.columns
    assert not summary.empty


def test_release_scaling_copy_excludes_secret_and_raw_cache_paths():
    release = Path("orphancure_release")
    assert not (release / ".env").exists()
    forbidden_dirs = {"pubmed_cache", "opentargets_cache", "primekg"}
    copied_dir_names = {path.name.lower() for path in release.rglob("*") if path.is_dir()}
    assert forbidden_dirs.isdisjoint(copied_dir_names)
