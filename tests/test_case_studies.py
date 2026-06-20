from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "docs" / "case_studies"
RELEASE_DIR = ROOT / "orphancure_release"
DISCLAIMER = "not medical advice"


def test_case_inventory_schema_and_row_count() -> None:
    inventory = pd.read_csv(CASE_DIR / "case_inventory.csv")
    required = {
        "pair_id",
        "drug_name",
        "disease_name",
        "expected_label",
        "full_status",
        "full_predicted_label",
        "n_claims",
        "n_verified_claims",
        "n_unsupported_claims",
        "has_full_report",
        "recommended_case_type",
        "recommended_for_manual_review",
    }
    assert required.issubset(inventory.columns)
    assert len(inventory) == 20
    assert inventory["pair_id"].notna().all()


def test_selected_cases_schema_and_pair_ids() -> None:
    selected = pd.read_csv(CASE_DIR / "selected_cases.csv")
    required = {"pair_id", "case_type", "case_file", "manual_review_status"}
    assert required.issubset(selected.columns)
    assert 3 <= len(selected) <= 5
    assert selected["pair_id"].notna().all()
    assert selected["pair_id"].is_unique
    assert set(selected["manual_review_status"]) == {"TODO_MANUAL_REVIEW"}


def test_selected_case_markdown_safety_and_review_status() -> None:
    selected = pd.read_csv(CASE_DIR / "selected_cases.csv")
    for filename in selected["case_file"]:
        text = (CASE_DIR / filename).read_text(encoding="utf-8")
        assert DISCLAIMER in text
        assert "- [ ] Biomedical expert review completed" in text
        assert "- [x] Biomedical expert review completed" not in text


def test_release_case_studies_synced_without_raw_data() -> None:
    release_case_dir = RELEASE_DIR / "docs" / "case_studies"
    assert (release_case_dir / "selected_cases.csv").exists()
    assert (release_case_dir / "case_studies_en.md").exists()
    assert not (RELEASE_DIR / ".env").exists()
    assert not (RELEASE_DIR / "data" / "external").exists()
    assert not (RELEASE_DIR / "data" / "external" / "pubmed_cache").exists()
    assert not (RELEASE_DIR / "data" / "external" / "primekg" / "kg.csv").exists()


def test_streamlit_app_case_study_loader_syntax() -> None:
    app_path = RELEASE_DIR / "app" / "streamlit_app.py"
    ast.parse(app_path.read_text(encoding="utf-8"))
    text = app_path.read_text(encoding="utf-8")
    assert "load_selected_cases" in text
    assert "Case Studies" in text
