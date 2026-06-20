"""Tests for repoDB benchmark preparation and validation."""

from pathlib import Path

import pandas as pd
import pytest

from app.evaluation.repodb_benchmark import (
    PrepareRepoDBConfig,
    filter_pairs,
    make_pair_id,
    make_split,
    map_repodb_status,
    normalize_repodb_dataframe,
    prepare_repodb_benchmark,
    validate_benchmark_files,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("raw_status", "expected"),
    [
        ("approved", "positive"),
        ("Approved indication", "positive"),
        ("Program Terminated", "negative_or_failed"),
        ("withdrawn", "negative_or_failed"),
        ("Suspended", "negative_or_failed"),
        ("failed", "negative_or_failed"),
        ("No development", "negative_or_failed"),
        ("", "TODO_REVIEW"),
        ("ambiguous", "TODO_REVIEW"),
        (None, "TODO_REVIEW"),
    ],
)
def test_repodb_label_mapping(raw_status, expected):
    assert map_repodb_status(raw_status) == expected


def test_pair_id_is_deterministic_and_name_normalized():
    first = make_pair_id(" Drug Alpha ", "Disease One", "Approved")
    second = make_pair_id("drug alpha", "disease-one", "approved")
    different = make_pair_id("Drug Alpha", "Disease One", "Suspended")
    assert first == second
    assert first.startswith("repodb_")
    assert first != different


def test_filtering_can_balance_classes():
    raw = pd.read_csv(FIXTURE_DIR / "repodb_raw_toy.csv")
    normalized = normalize_repodb_dataframe(raw, source_path_or_url="fixture")
    filtered = filter_pairs(normalized, balanced=True, seed=42, exclude_ambiguous=True)
    counts = filtered["expected_label"].value_counts().to_dict()
    assert counts["positive"] == counts["negative_or_failed"]
    assert "TODO_REVIEW" not in set(filtered["expected_label"])


def test_split_balance_keeps_each_class_in_test_and_dev_when_possible():
    raw = pd.read_csv(FIXTURE_DIR / "repodb_raw_toy.csv")
    normalized = normalize_repodb_dataframe(raw, source_path_or_url="fixture")
    filtered = filter_pairs(normalized, balanced=True, seed=42, exclude_ambiguous=True)
    split = make_split(filtered, seed=42, dev_fraction=0.5)
    joined = filtered.merge(split, on="pair_id")
    by_label = joined.groupby(["expected_label", "split"]).size().unstack(fill_value=0)
    assert set(split["split"]) == {"dev", "test"}
    assert (by_label["dev"] >= 1).all()
    assert (by_label["test"] >= 1).all()


def test_prepare_and_validate_benchmark_files(tmp_path):
    config = PrepareRepoDBConfig(
        input_path=FIXTURE_DIR / "repodb_raw_toy.csv",
        output_path=tmp_path / "repodb_pairs.csv",
        split_path=tmp_path / "repodb_split.csv",
        metadata_path=tmp_path / "repodb_metadata.json",
        balanced=True,
        max_pairs=4,
        seed=42,
    )
    pairs, split, metadata = prepare_repodb_benchmark(config)
    assert len(pairs) == 4
    assert len(split) == 4
    assert metadata["number_of_positive_pairs"] == 2
    assert metadata["number_of_negative_or_failed_pairs"] == 2
    assert validate_benchmark_files(config.output_path, config.split_path) == []


def test_benchmark_validation_reports_errors(tmp_path):
    pairs_path = tmp_path / "bad_pairs.csv"
    split_path = tmp_path / "bad_split.csv"
    pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "",
                "disease_name": "Disease",
                "raw_status": "Approved",
                "expected_label": "made_up",
                "source": "fixture",
                "source_id": "row:1",
                "notes": "",
            }
        ]
    ).to_csv(pairs_path, index=False)
    pd.DataFrame([{"pair_id": "p2", "split": "test"}]).to_csv(split_path, index=False)
    errors = validate_benchmark_files(pairs_path, split_path)
    assert any("drug_name" in error for error in errors)
    assert any("invalid values" in error for error in errors)


def test_benchmark_validation_reports_split_mismatch(tmp_path):
    pairs_path = tmp_path / "pairs.csv"
    split_path = tmp_path / "split.csv"
    pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Drug",
                "disease_name": "Disease",
                "raw_status": "Approved",
                "expected_label": "positive",
                "source": "fixture",
                "source_id": "row:1",
                "notes": "",
            }
        ]
    ).to_csv(pairs_path, index=False)
    pd.DataFrame([{"pair_id": "p2", "split": "test"}]).to_csv(split_path, index=False)
    errors = validate_benchmark_files(pairs_path, split_path)
    assert any("pair_ids" in error for error in errors)
