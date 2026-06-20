"""Tests for repoDB source download/provenance utilities."""

from pathlib import Path

import pandas as pd
import pytest

from app.evaluation.repodb_source import (
    RepoDBDownloadError,
    SourceCandidate,
    create_source_metadata,
    download_repodb_source,
    sha256_file,
    validate_source_file,
    write_prepared_source,
)


def _valid_repodb_csv(path: Path, rows: int = 101) -> Path:
    pd.DataFrame(
        {
            "drug_name": [f"Drug {i}" for i in range(rows)],
            "ind_name": [f"Disease {i}" for i in range(rows)],
            "status": ["Approved" if i % 2 else "Terminated" for i in range(rows)],
        }
    ).to_csv(path, index=False)
    return path


def test_sha256_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    assert sha256_file(path) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_source_file_validation_accepts_realistic_csv(tmp_path):
    path = _valid_repodb_csv(tmp_path / "repodb.csv")
    result = validate_source_file(path)
    assert result.valid
    assert result.row_count == 101
    assert result.column_names == ["drug_name", "ind_name", "status"]


def test_source_file_validation_rejects_too_small_or_missing_columns(tmp_path):
    small = tmp_path / "small.csv"
    pd.DataFrame({"drug_name": ["Drug"], "ind_name": ["Disease"], "status": ["Approved"]}).to_csv(small, index=False)
    small_result = validate_source_file(small)
    assert not small_result.valid
    assert any("row count" in error for error in small_result.errors)

    missing = tmp_path / "missing.csv"
    pd.DataFrame({"x": range(101), "y": range(101)}).to_csv(missing, index=False)
    missing_result = validate_source_file(missing)
    assert not missing_result.valid
    assert any("drug column" in error for error in missing_result.errors)
    assert any("disease/indication" in error for error in missing_result.errors)
    assert any("status column" in error for error in missing_result.errors)


def test_metadata_creation_records_hash_and_columns(tmp_path):
    raw = _valid_repodb_csv(tmp_path / "raw.csv")
    normalized = tmp_path / "repodb.csv"
    normalized.write_bytes(raw.read_bytes())
    validation = validate_source_file(normalized)
    metadata = create_source_metadata(
        source_name="fixture",
        source_url="https://example.org/repodb.csv",
        original_filename="repodb.csv",
        local_raw_path=raw,
        normalized_csv_path=normalized,
        validation=validation,
        notes="test",
    )
    assert metadata["source_name"] == "fixture"
    assert metadata["sha256"] == sha256_file(normalized)
    assert metadata["row_count"] == 101
    assert metadata["column_names"] == ["drug_name", "ind_name", "status"]


def test_write_prepared_source_copies_file_and_metadata(tmp_path):
    raw = _valid_repodb_csv(tmp_path / "raw.csv")
    candidate = SourceCandidate("fixture", "https://example.org/repodb.csv", "raw.csv", 0)
    prepared = write_prepared_source(
        raw,
        candidate,
        tmp_path / "external" / "repodb.csv",
        tmp_path / "external" / "metadata.json",
    )
    assert prepared.normalized_csv_path.exists()
    assert prepared.metadata_path.exists()
    assert prepared.metadata["row_count"] == 101


def test_download_failure_does_not_create_normalized_csv(tmp_path):
    def failing_get(*args, **kwargs):
        raise RuntimeError("network unavailable")

    normalized = tmp_path / "repodb.csv"
    with pytest.raises(RepoDBDownloadError):
        download_repodb_source(
            raw_dir=tmp_path / "raw",
            normalized_csv_path=normalized,
            metadata_path=tmp_path / "metadata.json",
            session_get=failing_get,
        )
    assert not normalized.exists()

