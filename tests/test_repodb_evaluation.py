"""Tests for Phase 1 repoDB evaluation utilities."""

from pathlib import Path

import pytest

from app.evaluation.repodb import (
    EvaluationConfig,
    average_precision,
    load_predictions,
    load_repodb,
    match_predictions,
    roc_auc,
    run_repodb_evaluation,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_repodb_normalizes_statuses_and_traceability():
    df = load_repodb(FIXTURE_DIR / "repodb_toy.csv")
    assert set(df["label"]) == {0, 1}
    assert set(df["benchmark_row_id"]) == {"repoDB:0", "repoDB:1", "repoDB:2", "repoDB:3"}
    assert df.loc[df["drug_name"] == "Drug Alpha", "label"].iloc[0] == 1
    assert df.loc[df["drug_name"] == "Drug Beta", "label"].iloc[0] == 0


def test_predictions_match_by_ids_then_names():
    repodb = load_repodb(FIXTURE_DIR / "repodb_toy.csv")
    predictions = load_predictions(FIXTURE_DIR / "repodb_predictions_toy.csv")
    matched, unmatched = match_predictions(repodb, predictions)
    assert len(matched) == 3
    assert len(unmatched) == 1
    assert set(matched["benchmark_row_id"]) == {"repoDB:0", "repoDB:1", "repoDB:2"}


def test_ranking_metrics_without_sklearn():
    labels = [1, 0, 1, 0]
    scores = [0.9, 0.8, 0.7, 0.1]
    assert roc_auc(labels, scores) == pytest.approx(0.75)
    assert average_precision(labels, scores) == pytest.approx((1.0 + 2 / 3) / 2)


def test_run_repodb_evaluation_writes_audit_outputs(tmp_path):
    config = EvaluationConfig(
        repodb_path=FIXTURE_DIR / "repodb_toy.csv",
        predictions_path=FIXTURE_DIR / "repodb_predictions_toy.csv",
        out_dir=tmp_path,
        threshold=0.5,
        top_k=(1, 2),
        smoke=True,
    )
    metrics = run_repodb_evaluation(config)
    assert metrics["matched_rows"] == 3
    assert metrics["coverage"] == pytest.approx(0.75)
    assert metrics["confusion_matrix"] == {"tp": 1, "tn": 1, "fp": 1, "fn": 0}
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "matched_predictions.csv").exists()
    assert (tmp_path / "unmatched_predictions.csv").exists()

