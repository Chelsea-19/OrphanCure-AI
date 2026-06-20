"""Tests for full-pipeline diagnostics and calibration utilities."""

from __future__ import annotations

import pandas as pd

from app.evaluation.full_pipeline_diagnostics import (
    add_alternative_scores,
    calibrate_thresholds,
    correctness_type,
    triage_classification,
)


def diagnostic_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "expected_label": "positive",
                "predicted_label": "positive",
                "confidence_score": 0.8,
                "status": "completed",
                "split": "dev",
                "pubmed_evidence_score": 0.8,
                "opentargets_support_score": 0.6,
                "graph_connectivity_score": 0.4,
                "citation_verified_rate": 1.0,
                "unsupported_claim_rate": 0.0,
                "n_pmids_clinical": 8,
                "n_pmids_mechanism": 4,
                "n_pmids_negative": 0,
                "n_unique_pmids": 10,
            },
            {
                "pair_id": "p2",
                "expected_label": "negative_or_failed",
                "predicted_label": "negative_or_failed",
                "confidence_score": 0.3,
                "status": "completed",
                "split": "dev",
                "pubmed_evidence_score": 0.1,
                "opentargets_support_score": 0.0,
                "graph_connectivity_score": 0.0,
                "citation_verified_rate": 0.0,
                "unsupported_claim_rate": 0.0,
                "n_pmids_clinical": 0,
                "n_pmids_mechanism": 0,
                "n_pmids_negative": 5,
                "n_unique_pmids": 5,
            },
            {
                "pair_id": "p3",
                "expected_label": "positive",
                "predicted_label": "",
                "confidence_score": 0.0,
                "status": "partial_success",
                "split": "test",
                "pubmed_evidence_score": 0.0,
                "opentargets_support_score": 0.0,
                "graph_connectivity_score": 0.0,
                "citation_verified_rate": 0.0,
                "unsupported_claim_rate": 0.0,
                "n_pmids_clinical": 0,
                "n_pmids_mechanism": 0,
                "n_pmids_negative": 0,
                "n_unique_pmids": 0,
            },
        ]
    )


def test_correctness_type_assignment():
    assert correctness_type({"expected_label": "positive", "predicted_label": "positive", "status": "completed"}) == "TP"
    assert correctness_type({"expected_label": "negative_or_failed", "predicted_label": "negative_or_failed", "status": "completed"}) == "TN"
    assert correctness_type({"expected_label": "negative_or_failed", "predicted_label": "positive", "status": "completed"}) == "FP"
    assert correctness_type({"expected_label": "positive", "predicted_label": "negative_or_failed", "status": "completed"}) == "FN"
    assert correctness_type({"expected_label": "positive", "predicted_label": "", "status": "partial_success"}) == "partial"
    assert correctness_type({"expected_label": "positive", "predicted_label": "", "status": "failed"}) == "skipped"


def test_threshold_calibration_handles_small_dev_split():
    df = add_alternative_scores(diagnostic_rows())
    calibration, best = calibrate_thresholds(df)
    assert best["exploratory"] is True
    assert best["n_dev_rows"] == 2
    assert set(calibration["threshold_name"]) == {
        "default_threshold",
        "best_f1_threshold",
        "best_balanced_accuracy_threshold",
        "high_precision_threshold",
        "high_recall_threshold",
    }


def test_alternative_score_calculation_uses_existing_features():
    scored = add_alternative_scores(diagnostic_rows())
    high = scored.loc[scored["pair_id"] == "p1"].iloc[0]
    low = scored.loc[scored["pair_id"] == "p2"].iloc[0]
    assert high["evidence_strength_score"] > low["evidence_strength_score"]
    assert high["clinical_support_score"] > low["clinical_support_score"]
    assert low["safety_penalized_score"] <= low["clinical_support_score"]


def test_triage_classification_abstains_on_middle_band():
    df = add_alternative_scores(diagnostic_rows())
    df.loc[df["pair_id"] == "p3", "clinical_support_score"] = 0.5
    df.loc[df["pair_id"] == "p3", "safety_penalized_score"] = 0.5
    triage, metrics = triage_classification(df, low_threshold=0.25, high_threshold=0.65)
    assert "uncertain_mixed" in set(triage["triage_label"])
    assert 0.0 < metrics["coverage_rate"] < 1.0
    assert metrics["abstention_rate"] > 0.0


def test_threshold_calibration_no_dev_rows_falls_back_to_all_rows():
    df = add_alternative_scores(diagnostic_rows())
    df["split"] = "test"
    _, best = calibrate_thresholds(df)
    assert best["calibration_source"] == "all_rows_exploratory_no_dev_rows"
    assert best["exploratory"] is True
