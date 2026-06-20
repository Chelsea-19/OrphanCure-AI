"""Tests for full-pipeline evaluation harness without live LLM/API calls."""

from __future__ import annotations

import os
import sys

import pandas as pd

from app.evaluation.full_pipeline_eval import (
    FULL_PIPELINE_COLUMNS,
    TODO_STATUS,
    claim_verification_counts,
    normalize_full_pipeline_output,
    run_full_pipeline_for_pair,
    select_evaluation_subset,
    summarize_full_pipeline_results,
)
from scripts.run_ablation_suite import main as run_ablation_main


def pairs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"pair_id": "p1", "drug_name": "Drug A", "disease_name": "Disease A", "expected_label": "positive"},
            {"pair_id": "p2", "drug_name": "Drug B", "disease_name": "Disease B", "expected_label": "negative_or_failed"},
            {"pair_id": "p3", "drug_name": "Drug C", "disease_name": "Disease C", "expected_label": "positive"},
        ]
    )


def unified_features() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "pubmed_available": True,
                "opentargets_available": True,
                "graph_available": True,
                "n_unique_pmids": 4,
                "n_overlapping_targets": 2,
                "n_paths_len_2": 1,
            },
            {"pair_id": "p2", "pubmed_available": True, "opentargets_available": False, "graph_available": False},
            {"pair_id": "p3", "pubmed_available": False, "opentargets_available": True, "graph_available": True},
        ]
    )


def test_select_subset_prefers_all_evidence_layers():
    selected = select_evaluation_subset(pairs(), unified_features(), max_pairs=2)
    assert selected.iloc[0]["pair_id"] == "p1"
    assert set(selected["pair_id"]) == {"p1", "p3"}


def test_todo_result_when_llm_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = run_full_pipeline_for_pair(
        pairs().iloc[0],
        "full",
        tmp_path,
        skip_llm_if_missing=True,
    )
    assert result["status"] == TODO_STATUS
    assert result["predicted_label"] == TODO_STATUS
    assert (tmp_path / "raw_outputs" / "full" / "p1.json").exists()
    assert (tmp_path / "reports" / "full" / "p1.md").exists()


def test_normalization_extracts_claim_and_evidence_metrics(tmp_path):
    raw = {
        "status": "completed",
        "predicted_label": "positive",
        "confidence_score": 0.8,
        "final_assessment": "Potential",
        "state": {
            "common_targets": [{"symbol": "ABC"}],
            "mechanism_evidence": [{"target_symbol": "ABC"}],
            "papers": [{"pmid": "1"}, {"pmid": "2"}],
            "verified_claims": [
                {"verification_status": "VERIFIED", "provenance": {"paper_evidence": [{"pmid": "1"}]}},
                {"verification_status": "UNVERIFIED", "provenance": {"paper_evidence": [{"pmid": "2"}]}},
            ],
        },
    }
    row = normalize_full_pipeline_output(pairs().iloc[0], "full", raw, tmp_path / "raw.json", tmp_path / "report.md")
    assert list(row.keys()) == list(FULL_PIPELINE_COLUMNS)
    assert row["n_claims"] == 2
    assert row["n_verified_claims"] == 1
    assert row["n_unsupported_claims"] == 1
    assert row["citation_verified_rate"] == 0.5
    assert row["n_pmids_used"] == 2


def test_claim_verification_counts():
    counts = claim_verification_counts(
        [
            {"verification_status": "VERIFIED"},
            {"verification_status": "PARTIALLY_VERIFIED"},
            {"verification_status": "UNVERIFIED"},
        ]
    )
    assert counts == (3, 1, 1)


def test_full_pipeline_metrics_calculation():
    results = pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "expected_label": "positive",
                "predicted_label": "positive",
                "confidence_score": 0.9,
                "status": "completed",
                "n_claims": 2,
                "n_verified_claims": 2,
                "n_unsupported_claims": 0,
                "citation_verified_rate": 1.0,
                "unsupported_claim_rate": 0.0,
                "n_pmids_used": 3,
                "n_opentargets_evidence_items": 2,
                "n_graph_paths_used": 1,
                "runtime_seconds": 1.0,
            },
            {
                "pair_id": "p2",
                "expected_label": "negative_or_failed",
                "predicted_label": "negative_or_failed",
                "confidence_score": 0.1,
                "status": "completed",
                "n_claims": 1,
                "n_verified_claims": 0,
                "n_unsupported_claims": 1,
                "citation_verified_rate": 0.0,
                "unsupported_claim_rate": 1.0,
                "n_pmids_used": 1,
                "n_opentargets_evidence_items": 0,
                "n_graph_paths_used": 0,
                "runtime_seconds": 2.0,
            },
        ]
    )
    metrics = summarize_full_pipeline_results(results, "full")
    assert metrics["accuracy"] == 1.0
    assert metrics["mean_n_claims"] == 1.5
    assert metrics["success_rate"] == 1.0


def test_ablation_suite_reads_full_pipeline_outputs(tmp_path, monkeypatch):
    unified = pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Drug A",
                "disease_name": "Disease A",
                "expected_label": "positive",
                "split": "dev",
                "opentargets_available": False,
                "graph_available": False,
                "pubmed_available": False,
                "drug_resolved_ot": False,
                "disease_resolved_ot": False,
                "n_disease_targets": 0,
                "n_drug_targets": 0,
                "n_overlapping_targets": 0,
                "has_target_overlap": False,
                "opentargets_support_score": 0,
                "drug_mapped_graph": False,
                "disease_mapped_graph": False,
                "has_graph_path": False,
                "shortest_path_length": 0,
                "n_paths_len_2": 0,
                "n_paths_len_3": 0,
                "n_paths_len_4": 0,
                "graph_connectivity_score": 0,
                "n_unique_pmids": 0,
                "n_pmids_direct": 0,
                "n_pmids_title_abstract": 0,
                "n_pmids_clinical": 0,
                "n_pmids_negative": 0,
                "n_pmids_mechanism": 0,
                "has_direct_evidence": False,
                "has_clinical_evidence": False,
                "has_negative_signal": False,
                "has_mechanism_signal": False,
                "abstract_available_rate": 0,
                "pubmed_evidence_score": 0,
                "unified_status": "missing_evidence",
                "notes": "",
            }
        ]
    )
    input_path = tmp_path / "unified.csv"
    output_dir = tmp_path / "unified_out"
    unified.to_csv(input_path, index=False)
    full_dir = tmp_path / "full_pipeline"
    full_dir.mkdir()
    pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Drug A",
                "disease_name": "Disease A",
                "expected_label": "positive",
                "mode": "full",
                "predicted_label": "positive",
                "confidence_score": 0.9,
                "status": "completed",
                "runtime_seconds": 1.0,
            }
        ]
    ).to_csv(full_dir / "per_pair_results_full.csv", index=False)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_ablation_suite.py",
            "--input",
            str(input_path),
            "--output_dir",
            str(output_dir),
            "--full_pipeline_dir",
            str(full_dir),
        ],
    )
    assert run_ablation_main() == 0
    comparison = pd.read_csv(output_dir / "baseline_comparison.csv")
    full = comparison[comparison["mode"] == "full"].iloc[0]
    assert full["status"] == "completed"
