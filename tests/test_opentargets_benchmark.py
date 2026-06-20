"""Tests for Open Targets benchmark enrichment without network calls."""

from pathlib import Path

import pandas as pd

from app.evaluation.opentargets_benchmark import (
    EVIDENCE_COLUMNS,
    FEATURE_COLUMNS,
    OpenTargetsClient,
    OpenTargetsConfig,
    calculate_support_features,
    calculate_target_overlap,
    enrich_pairs,
    extract_disease_targets,
    load_cached_json,
    make_cache_key,
    resolve_entity,
    write_cached_json,
)
from app.evaluation.repodb_benchmark import validate_benchmark_files


class FakeOpenTargetsClient:
    def query(self, operation, query, variables):
        if operation == "search_drug":
            if variables["q"] == "Missing Drug":
                return {"data": {"search": {"hits": []}}}
            return {"data": {"search": {"hits": [{"id": "CHEMBL1", "name": variables["q"], "score": 10.0}]}}}
        if operation == "search_disease":
            if variables["q"] == "Missing Disease":
                return {"data": {"search": {"hits": []}}}
            return {"data": {"search": {"hits": [{"id": "EFO_1", "name": variables["q"], "score": 9.0}]}}}
        if operation == "disease_targets":
            return {
                "data": {
                    "disease": {
                        "associatedTargets": {
                            "rows": [
                                {"score": 0.8, "target": {"id": "ENSG1", "approvedSymbol": "GENE1", "approvedName": "Gene 1"}},
                                {"score": 0.2, "target": {"id": "ENSG2", "approvedSymbol": "GENE2", "approvedName": "Gene 2"}},
                            ]
                        }
                    }
                }
            }
        if operation == "drug_targets":
            return {
                "data": {
                    "drug": {
                        "mechanismsOfAction": {
                            "rows": [
                                {
                                    "actionType": "INHIBITOR",
                                    "mechanismOfAction": "GENE1 inhibition",
                                    "targets": [{"id": "ENSG1", "approvedSymbol": "GENE1", "approvedName": "Gene 1"}],
                                }
                            ]
                        }
                    }
                }
            }
        if operation == "known_drugs":
            return {
                "data": {
                    "disease": {
                        "knownDrugs": {
                            "rows": [
                                {
                                    "drug": {"id": "CHEMBL1", "name": "Drug Alpha"},
                                    "mechanismOfAction": "GENE1 inhibition",
                                }
                            ]
                        }
                    }
                }
            }
        raise AssertionError(f"Unexpected operation: {operation}")


def test_cached_json_round_trip(tmp_path):
    payload = {"data": {"x": 1}}
    path = write_cached_json(tmp_path, "cache_key", payload)
    assert path.exists()
    assert load_cached_json(tmp_path, "cache_key") == payload


def test_cached_fixture_mode_without_api(tmp_path):
    key = make_cache_key("search_drug", {"q": "Drug Alpha", "entities": ["drug"]})
    write_cached_json(tmp_path, key, {"data": {"search": {"hits": [{"id": "CHEMBL1", "name": "Drug Alpha", "score": 1.0}]}}})
    client = OpenTargetsClient(OpenTargetsConfig(cache_dir=tmp_path, use_cached=True, skip_api_if_missing=True))
    resolved = resolve_entity(client, "Drug Alpha", "drug")
    assert resolved.resolved
    assert resolved.opentargets_id == "CHEMBL1"


def test_missing_api_fields_are_ignored_gracefully():
    class MissingFieldClient:
        def query(self, operation, query, variables):
            return {"data": {"disease": {"associatedTargets": {"rows": [{"score": 0.5, "target": {}}]}}}}

    targets, error = extract_disease_targets(MissingFieldClient(), "EFO_1")
    assert targets == []
    assert error == ""


def test_unresolved_drug_and_disease_behavior():
    drug = resolve_entity(FakeOpenTargetsClient(), "Missing Drug", "drug")
    disease = resolve_entity(FakeOpenTargetsClient(), "Missing Disease", "disease")
    assert not drug.resolved
    assert "no drug search hits" in drug.error_message
    assert not disease.resolved
    assert "no disease search hits" in disease.error_message


def test_target_overlap_calculation():
    overlaps = calculate_target_overlap(
        [{"target_id": "ENSG1", "target_symbol": "GENE1"}],
        [{"target_id": "ENSG1", "target_symbol": "GENE1", "association_score": 0.7}],
    )
    assert len(overlaps) == 1
    assert overlaps[0]["association_score"] == 0.7


def test_support_score_calculation():
    features = calculate_support_features(
        True,
        True,
        [{"target_id": "ENSG1"}],
        [{"target_id": "ENSG1"}],
        [{"target_id": "ENSG1", "association_score": 0.8}],
        [{"drug_id": "CHEMBL1"}],
    )
    assert features["status"] == "success"
    assert features["has_known_drug_evidence"]
    assert features["has_target_overlap"]
    assert features["opentargets_support_score"] == 0.88


def test_normalized_output_schemas():
    pairs = pd.DataFrame(
        [{"pair_id": "p1", "drug_name": "Drug Alpha", "disease_name": "Disease One"}]
    )
    evidence, features = enrich_pairs(pairs, FakeOpenTargetsClient())
    assert list(evidence.columns) == list(EVIDENCE_COLUMNS)
    assert list(features.columns) == list(FEATURE_COLUMNS)
    assert len(features) == 1
    assert features.loc[0, "status"] == "success"


def test_validation_failure_when_required_opentargets_columns_missing(tmp_path):
    pairs = tmp_path / "pairs.csv"
    split = tmp_path / "split.csv"
    evidence = tmp_path / "bad_evidence.csv"
    features = tmp_path / "bad_features.csv"
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
    ).to_csv(pairs, index=False)
    pd.DataFrame([{"pair_id": "p1", "split": "test"}]).to_csv(split, index=False)
    pd.DataFrame([{"pair_id": "p1"}]).to_csv(evidence, index=False)
    pd.DataFrame([{"pair_id": "p1"}]).to_csv(features, index=False)
    errors = validate_benchmark_files(pairs, split, evidence, features)
    assert any("Open Targets evidence file is missing required columns" in error for error in errors)
    assert any("Open Targets features file is missing required columns" in error for error in errors)
