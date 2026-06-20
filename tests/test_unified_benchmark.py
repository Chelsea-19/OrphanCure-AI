"""Tests for unified repoDB/Open Targets/graph benchmark evaluation."""

import json

import pandas as pd

from app.evaluation.unified_benchmark import (
    build_unified_benchmark_table,
    classification_metrics,
    evaluate_unified_mode,
    normalize_score,
    select_threshold,
    write_unified_outputs,
)


def repodb_pairs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"pair_id": "p1", "drug_name": "Drug A", "disease_name": "Disease A", "expected_label": "positive"},
            {"pair_id": "p2", "drug_name": "Drug B", "disease_name": "Disease B", "expected_label": "negative_or_failed"},
            {"pair_id": "p3", "drug_name": "Drug C", "disease_name": "Disease C", "expected_label": "positive"},
        ]
    )


def split() -> pd.DataFrame:
    return pd.DataFrame([{"pair_id": "p1", "split": "dev"}, {"pair_id": "p2", "split": "test"}, {"pair_id": "p3", "split": "test"}])


def opentargets_features() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_resolved": True,
                "disease_resolved": True,
                "n_disease_targets": 4,
                "n_drug_targets": 2,
                "n_overlapping_targets": 1,
                "has_target_overlap": True,
                "opentargets_support_score": 0.8,
            },
            {
                "pair_id": "p2",
                "drug_resolved": True,
                "disease_resolved": False,
                "n_disease_targets": 0,
                "n_drug_targets": 1,
                "n_overlapping_targets": 0,
                "has_target_overlap": False,
                "opentargets_support_score": 0.0,
            },
        ]
    )


def graph_features() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_mapped": True,
                "disease_mapped": True,
                "has_path": True,
                "shortest_path_length": 2,
                "n_paths_len_2": 1,
                "n_paths_len_3": 0,
                "n_paths_len_4": 0,
                "graph_connectivity_score": 0.75,
            },
            {
                "pair_id": "p3",
                "drug_mapped": True,
                "disease_mapped": False,
                "has_path": False,
                "shortest_path_length": 0,
                "n_paths_len_2": 0,
                "n_paths_len_3": 0,
                "n_paths_len_4": 0,
                "graph_connectivity_score": 0.0,
            },
        ]
    )


def unified_fixture() -> pd.DataFrame:
    return build_unified_benchmark_table(repodb_pairs(), opentargets_features(), graph_features(), split())


def test_left_join_preserves_all_repodb_pairs():
    unified = unified_fixture()
    assert len(unified) == 3
    assert list(unified["pair_id"]) == ["p1", "p2", "p3"]


def test_missing_opentargets_features_are_retained():
    unified = unified_fixture()
    row = unified[unified["pair_id"] == "p3"].iloc[0]
    assert not row["opentargets_available"]
    assert pd.isna(row["opentargets_support_score"])
    assert "Open Targets features missing" in row["notes"]


def test_missing_graph_features_are_retained():
    unified = unified_fixture()
    row = unified[unified["pair_id"] == "p2"].iloc[0]
    assert not row["graph_available"]
    assert pd.isna(row["graph_connectivity_score"])
    assert "Graph features missing" in row["notes"]


def test_score_normalization():
    normalized = normalize_score(pd.Series([2.0, 4.0, None, 6.0]))
    assert normalized.tolist() == [0.0, 0.5, 0.0, 1.0]


def test_threshold_selection_uses_dev_split_only():
    results = pd.DataFrame(
        [
            {"split": "dev", "expected_label": "positive", "confidence_score": 0.7, "evaluation_status": "evaluated"},
            {"split": "dev", "expected_label": "negative_or_failed", "confidence_score": 0.2, "evaluation_status": "evaluated"},
        ]
        * 5
        + [
            {"split": "test", "expected_label": "positive", "confidence_score": 0.01, "evaluation_status": "evaluated"},
            {"split": "test", "expected_label": "negative_or_failed", "confidence_score": 0.99, "evaluation_status": "evaluated"},
        ]
    )
    threshold, source = select_threshold(results, "opentargets_only")
    assert threshold == 0.7
    assert source == "dev_split_max_f1"


def test_metric_calculation():
    metrics = classification_metrics([1, 0, 1, 0], [1, 0, 0, 1], [0.9, 0.2, 0.4, 0.7])
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5
    assert metrics["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}


def test_summary_output_generation(tmp_path):
    unified = unified_fixture()
    results, metrics = evaluate_unified_mode(unified, "heuristic_combined")
    summary = write_unified_outputs(unified, results, metrics, tmp_path)
    assert (tmp_path / "unified_per_pair_results.csv").exists()
    assert (tmp_path / "baseline_comparison.csv").exists()
    assert (tmp_path / "summary_metrics.json").exists()
    assert (tmp_path / "summary_table.md").exists()
    saved = json.loads((tmp_path / "summary_metrics.json").read_text(encoding="utf-8"))
    assert saved["coverage_metrics"]["n_pairs"] == 3
    assert "heuristic_combined" in summary["modes"]


def test_no_fabricated_full_results():
    unified = unified_fixture()
    results, metrics = evaluate_unified_mode(unified, "full_placeholder")
    assert metrics["status"] == "TODO_NOT_RUN"
    assert metrics["n_evaluated_pairs"] == 0
    assert set(results["evaluation_status"]) == {"TODO_NOT_RUN"}
