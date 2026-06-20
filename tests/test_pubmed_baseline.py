"""Tests for PubMed-only baseline utilities without live NCBI calls."""

import json
import sys

import pandas as pd

from app.evaluation.pubmed_baseline import (
    PUBMED_EVIDENCE_COLUMNS,
    PUBMED_FEATURE_COLUMNS,
    PubMedConfig,
    build_pubmed_queries,
    calculate_pubmed_features,
    cache_key_for,
    parse_pubmed_xml,
    prepare_pubmed_outputs,
    pubmed_evidence_score,
    read_json_cache,
    write_json_cache,
)
from app.evaluation.repodb_benchmark import validate_benchmark_files
from app.evaluation.unified_benchmark import build_unified_benchmark_table, evaluate_unified_mode
from scripts.run_ablation_suite import main as run_ablation_main


PUBMED_XML = """<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>123</PMID>
      <Article>
        <Journal><Title>Journal One</Title><JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue></Journal>
        <ArticleTitle>Drug A in Disease A</ArticleTitle>
        <Abstract><AbstractText>Clinical mechanism abstract.</AbstractText></Abstract>
        <PublicationTypeList><PublicationType>Clinical Trial</PublicationType></PublicationTypeList>
      </Article>
    </MedlineCitation>
    <PubmedData><ArticleIdList><ArticleId IdType="doi">10.1/example</ArticleId></ArticleIdList></PubmedData>
  </PubmedArticle>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>456</PMID>
      <Article>
        <Journal><Title>Journal Two</Title><JournalIssue><PubDate><MedlineDate>2018 Jan-Feb</MedlineDate></PubDate></JournalIssue></Journal>
        <ArticleTitle>Pathway study</ArticleTitle>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


class FakePubMedClient:
    def __init__(self):
        self.config = PubMedConfig(cache_dir="unused")

    def search(self, query):
        if "Title/Abstract" in query:
            return ["123"]
        if "trial OR clinical" in query:
            return ["123"]
        if "failed OR failure" in query:
            return []
        if "mechanism OR target" in query:
            return ["123", "456"]
        return ["123", "456", "123"]

    def fetch_metadata(self, pmids):
        return parse_pubmed_xml(PUBMED_XML)


def pairs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "pair_id": "p1",
                "drug_name": "Drug A",
                "disease_name": "Disease A",
                "raw_status": "Approved",
                "expected_label": "positive",
                "source": "fixture",
                "source_id": "row:1",
                "notes": "",
            }
        ]
    )


def test_pubmed_query_construction():
    queries = build_pubmed_queries("Drug A", "Disease B")
    assert queries["direct"] == '"Drug A" AND "Disease B"'
    assert "[Title/Abstract]" in queries["title_abstract"]
    assert "failed OR failure" in queries["negative"]


def test_pubmed_xml_parsing():
    records = parse_pubmed_xml(PUBMED_XML)
    assert records["123"]["title"] == "Drug A in Disease A"
    assert records["123"]["publication_year"] == 2020
    assert records["123"]["doi"] == "10.1/example"
    assert records["456"]["publication_year"] == 2018


def test_cache_read_write(tmp_path):
    key = cache_key_for("search", {"q": "x"})
    write_json_cache(tmp_path, key, {"pmids": ["1"]})
    assert read_json_cache(tmp_path, key)["pmids"] == ["1"]


def test_feature_calculation_and_pmid_deduplication():
    metadata = parse_pubmed_xml(PUBMED_XML)
    feature = calculate_pubmed_features(
        "p1",
        "Drug A",
        "Disease A",
        "positive",
        {"direct": ["123", "123"], "title_abstract": ["123"], "clinical": ["123"], "negative": [], "mechanism": ["456"]},
        metadata,
        [],
    )
    assert feature["n_unique_pmids"] == 2
    assert feature["abstract_available_rate"] == 0.5
    assert feature["has_clinical_evidence"]
    assert feature["status"] == "success"


def test_pubmed_evidence_score_is_transparent():
    with_negative = pubmed_evidence_score(10, 2, 1, 1, 1)
    without_negative = pubmed_evidence_score(10, 2, 1, 1, 0)
    assert 0 <= with_negative <= 1
    assert without_negative > with_negative


def test_prepare_pubmed_outputs_schema():
    evidence, features = prepare_pubmed_outputs(pairs(), FakePubMedClient(), max_pairs=1)
    assert list(evidence.columns) == list(PUBMED_EVIDENCE_COLUMNS)
    assert list(features.columns) == list(PUBMED_FEATURE_COLUMNS)
    assert features.loc[0, "n_unique_pmids"] == 2


def test_pubmed_feature_validation(tmp_path):
    pair_path = tmp_path / "pairs.csv"
    split_path = tmp_path / "split.csv"
    evidence_path = tmp_path / "evidence.csv"
    features_path = tmp_path / "features.csv"
    pairs().to_csv(pair_path, index=False)
    pd.DataFrame([{"pair_id": "p1", "split": "dev"}]).to_csv(split_path, index=False)
    evidence, features = prepare_pubmed_outputs(pairs(), FakePubMedClient(), max_pairs=1)
    evidence.to_csv(evidence_path, index=False)
    features.to_csv(features_path, index=False)
    assert validate_benchmark_files(pair_path, split_path, pubmed_features_path=features_path, pubmed_evidence_path=evidence_path) == []


def test_pubmed_only_unified_evaluation():
    _, features = prepare_pubmed_outputs(pairs(), FakePubMedClient(), max_pairs=1)
    unified = build_unified_benchmark_table(pairs(), pd.DataFrame(), pd.DataFrame(), pubmed_features=features)
    results, metrics = evaluate_unified_mode(unified, "pubmed_only")
    assert metrics["mode"] == "pubmed_only"
    assert metrics["n_evaluated_pairs"] == 1
    assert set(results["evaluation_status"]) == {"evaluated"}


def test_ablation_suite_includes_pubmed_only_when_features_exist(tmp_path, monkeypatch):
    _, features = prepare_pubmed_outputs(pairs(), FakePubMedClient(), max_pairs=1)
    unified = build_unified_benchmark_table(pairs(), pd.DataFrame(), pd.DataFrame(), pubmed_features=features)
    input_path = tmp_path / "unified.csv"
    output_dir = tmp_path / "out"
    unified.to_csv(input_path, index=False)
    monkeypatch.setattr(sys, "argv", ["run_ablation_suite.py", "--input", str(input_path), "--output_dir", str(output_dir)])
    assert run_ablation_main() == 0
    comparison = pd.read_csv(output_dir / "baseline_comparison.csv")
    pubmed = comparison[comparison["mode"] == "pubmed_only"].iloc[0]
    assert pubmed["status"] == "completed"


def test_ablation_suite_marks_pubmed_todo_without_features(tmp_path, monkeypatch):
    unified = build_unified_benchmark_table(pairs(), pd.DataFrame(), pd.DataFrame())
    input_path = tmp_path / "unified.csv"
    output_dir = tmp_path / "out"
    unified.to_csv(input_path, index=False)
    monkeypatch.setattr(sys, "argv", ["run_ablation_suite.py", "--input", str(input_path), "--output_dir", str(output_dir)])
    assert run_ablation_main() == 0
    comparison = pd.read_csv(output_dir / "baseline_comparison.csv")
    pubmed = comparison[comparison["mode"] == "pubmed_only"].iloc[0]
    assert pubmed["status"] == "TODO_NOT_RUN"
