"""PubMed-only retrieval and scoring baseline for repoDB pairs."""

from __future__ import annotations

import hashlib
import json
import math
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests


PUBMED_SOURCE = "NCBI PubMed E-utilities"
VALID_PUBMED_STATUSES = {"success", "partial_success", "failed", "skipped"}

QUERY_TYPES = (
    "direct",
    "title_abstract",
    "clinical",
    "negative",
    "mechanism",
)

PUBMED_FEATURE_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "expected_label",
    "n_pmids_direct",
    "n_pmids_title_abstract",
    "n_pmids_clinical",
    "n_pmids_negative",
    "n_pmids_mechanism",
    "n_unique_pmids",
    "has_direct_evidence",
    "has_clinical_evidence",
    "has_negative_signal",
    "has_mechanism_signal",
    "earliest_publication_year",
    "latest_publication_year",
    "mean_publication_year",
    "abstract_available_rate",
    "pubmed_evidence_score",
    "status",
    "error_message",
    "notes",
)

PUBMED_EVIDENCE_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "query_type",
    "query_string",
    "pmid",
    "title",
    "abstract",
    "journal",
    "publication_year",
    "publication_type",
    "doi",
    "source",
    "status",
    "error_message",
    "notes",
)


@dataclass(frozen=True)
class PubMedConfig:
    email: str = ""
    ncbi_api_key: str = ""
    cache_dir: Path = Path("data/external/pubmed_cache")
    max_results_per_query: int = 20
    timeout: int = 20
    retries: int = 2
    backoff: float = 0.4
    use_cached: bool = False
    skip_api_if_missing: bool = False
    tool: str = "orphancure_pubmed_baseline"


class PubMedClient:
    """Small E-utilities client with deterministic JSON/XML caching."""

    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, config: PubMedConfig):
        self.config = config

    def search(self, query: str) -> list[str]:
        cache_key = cache_key_for("search", {"query": query, "retmax": self.config.max_results_per_query})
        cached = read_json_cache(self.config.cache_dir, cache_key)
        if cached is not None:
            return [str(pmid) for pmid in cached.get("pmids", [])]
        if self.config.use_cached and self.config.skip_api_if_missing:
            raise FileNotFoundError(f"Missing cached PubMed search response: {cache_key}.json")

        params = self._base_params() | {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(self.config.max_results_per_query),
            "sort": "relevance",
        }
        payload = self._request_json(self.search_url, params)
        pmids = [str(pmid) for pmid in payload.get("esearchresult", {}).get("idlist", [])]
        write_json_cache(self.config.cache_dir, cache_key, {"query": query, "pmids": pmids, "payload": payload})
        return pmids

    def fetch_metadata(self, pmids: list[str]) -> dict[str, dict[str, Any]]:
        unique_pmids = sorted({str(pmid) for pmid in pmids if str(pmid).strip()}, key=lambda value: int(value) if value.isdigit() else value)
        if not unique_pmids:
            return {}
        cache_key = cache_key_for("fetch", {"pmids": unique_pmids})
        cached = read_json_cache(self.config.cache_dir, cache_key)
        if cached is not None:
            return {str(key): value for key, value in cached.get("records", {}).items()}
        if self.config.use_cached and self.config.skip_api_if_missing:
            raise FileNotFoundError(f"Missing cached PubMed fetch response: {cache_key}.json")

        params = self._base_params() | {"db": "pubmed", "id": ",".join(unique_pmids), "retmode": "xml"}
        text = self._request_text(self.fetch_url, params)
        records = parse_pubmed_xml(text)
        write_json_cache(self.config.cache_dir, cache_key, {"pmids": unique_pmids, "records": records, "xml": text})
        return records

    def _base_params(self) -> dict[str, str]:
        params = {"tool": self.config.tool}
        if self.config.email:
            params["email"] = self.config.email
        if self.config.ncbi_api_key:
            params["api_key"] = self.config.ncbi_api_key
        return params

    def _request_json(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.config.retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                if attempt < self.config.retries:
                    time.sleep(self.config.backoff * (2**attempt))
        raise RuntimeError(str(last_error))

    def _request_text(self, url: str, params: dict[str, str]) -> str:
        last_error: Exception | None = None
        for attempt in range(self.config.retries + 1):
            try:
                response = requests.get(url, params=params, timeout=self.config.timeout)
                response.raise_for_status()
                return response.text
            except Exception as exc:
                last_error = exc
                if attempt < self.config.retries:
                    time.sleep(self.config.backoff * (2**attempt))
        raise RuntimeError(str(last_error))


def build_pubmed_queries(drug_name: str, disease_name: str) -> dict[str, str]:
    drug = quote_term(drug_name)
    disease = quote_term(disease_name)
    return {
        "direct": f"{drug} AND {disease}",
        "title_abstract": f"{drug}[Title/Abstract] AND {disease}[Title/Abstract]",
        "clinical": f"{drug} AND {disease} AND (trial OR clinical OR patient OR therapy)",
        "negative": f"{drug} AND {disease} AND (failed OR failure OR ineffective OR toxicity OR adverse OR discontinued)",
        "mechanism": f"{drug} AND {disease} AND (mechanism OR target OR pathway)",
    }


def quote_term(value: str) -> str:
    escaped = str(value).replace('"', '\\"').strip()
    return f'"{escaped}"'


def cache_key_for(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"


def read_json_cache(cache_dir: str | Path, cache_key: str) -> dict[str, Any] | None:
    path = Path(cache_dir) / f"{cache_key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_cache(cache_dir: str | Path, cache_key: str, payload: dict[str, Any]) -> Path:
    path = Path(cache_dir) / f"{cache_key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_failed_query_log(cache_dir: str | Path, pair_id: str, query_type: str, query: str, error: str) -> Path:
    cache_key = cache_key_for("failed_query", {"pair_id": pair_id, "query_type": query_type, "query": query})
    return write_json_cache(Path(cache_dir) / "failed_queries", cache_key, {"pair_id": pair_id, "query_type": query_type, "query": query, "error": error})


def parse_pubmed_xml(xml_text: str) -> dict[str, dict[str, Any]]:
    root = ET.fromstring(xml_text)
    records: dict[str, dict[str, Any]] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = text_or_empty(article.find(".//MedlineCitation/PMID"))
        if not pmid:
            continue
        article_node = article.find(".//MedlineCitation/Article")
        title = text_or_empty(article_node.find("ArticleTitle") if article_node is not None else None)
        abstract_parts = [
            "".join(node.itertext()).strip()
            for node in article.findall(".//Abstract/AbstractText")
            if "".join(node.itertext()).strip()
        ]
        journal = text_or_empty(article.find(".//Journal/Title"))
        year = extract_publication_year(article)
        pub_types = [text_or_empty(node) for node in article.findall(".//PublicationType") if text_or_empty(node)]
        doi = ""
        for article_id in article.findall(".//ArticleId"):
            if str(article_id.attrib.get("IdType", "")).casefold() == "doi":
                doi = text_or_empty(article_id)
                break
        records[pmid] = {
            "pmid": pmid,
            "title": title,
            "abstract": " ".join(abstract_parts),
            "journal": journal,
            "publication_year": year,
            "publication_type": "; ".join(pub_types),
            "doi": doi,
        }
    return records


def text_or_empty(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def extract_publication_year(article: ET.Element) -> int | None:
    for path in (
        ".//Article/Journal/JournalIssue/PubDate/Year",
        ".//MedlineCitation/DateCompleted/Year",
        ".//MedlineCitation/DateRevised/Year",
    ):
        value = text_or_empty(article.find(path))
        if value.isdigit():
            return int(value)
    medline_date = text_or_empty(article.find(".//Article/Journal/JournalIssue/PubDate/MedlineDate"))
    for token in medline_date.replace("-", " ").split():
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def process_pubmed_pair(pair: dict[str, Any], client: PubMedClient) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pair_id = str(pair.get("pair_id", ""))
    drug_name = str(pair.get("drug_name", ""))
    disease_name = str(pair.get("disease_name", ""))
    expected_label = str(pair.get("expected_label", ""))
    queries = build_pubmed_queries(drug_name, disease_name)
    query_pmids: dict[str, list[str]] = {}
    errors: list[str] = []

    for query_type, query in queries.items():
        try:
            query_pmids[query_type] = client.search(query)
        except Exception as exc:
            query_pmids[query_type] = []
            message = f"{query_type}: {exc}"
            errors.append(message)
            write_failed_query_log(client.config.cache_dir, pair_id, query_type, query, str(exc))

    unique_pmids = sorted({pmid for pmids in query_pmids.values() for pmid in pmids}, key=lambda value: int(value) if value.isdigit() else value)
    metadata: dict[str, dict[str, Any]] = {}
    if unique_pmids:
        try:
            metadata = client.fetch_metadata(unique_pmids)
        except Exception as exc:
            errors.append(f"fetch_metadata: {exc}")
            metadata = {}

    feature = calculate_pubmed_features(pair_id, drug_name, disease_name, expected_label, query_pmids, metadata, errors)
    evidence = make_pubmed_evidence_rows(pair_id, drug_name, disease_name, queries, query_pmids, metadata, feature)
    if not evidence:
        evidence = [status_evidence_row(pair_id, drug_name, disease_name, feature, next(iter(queries.items())))]
    return evidence, feature


def calculate_pubmed_features(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    expected_label: str,
    query_pmids: dict[str, list[str]],
    metadata: dict[str, dict[str, Any]],
    errors: list[str] | None = None,
) -> dict[str, Any]:
    unique_pmids = sorted({pmid for pmids in query_pmids.values() for pmid in pmids})
    years = [int(record["publication_year"]) for record in metadata.values() if record.get("publication_year")]
    abstract_count = sum(1 for record in metadata.values() if str(record.get("abstract", "")).strip())
    n_metadata = len(metadata)
    feature = {
        "pair_id": pair_id,
        "drug_name": drug_name,
        "disease_name": disease_name,
        "expected_label": expected_label,
        "n_pmids_direct": len(set(query_pmids.get("direct", []))),
        "n_pmids_title_abstract": len(set(query_pmids.get("title_abstract", []))),
        "n_pmids_clinical": len(set(query_pmids.get("clinical", []))),
        "n_pmids_negative": len(set(query_pmids.get("negative", []))),
        "n_pmids_mechanism": len(set(query_pmids.get("mechanism", []))),
        "n_unique_pmids": len(unique_pmids),
        "has_direct_evidence": bool(query_pmids.get("direct")),
        "has_clinical_evidence": bool(query_pmids.get("clinical")),
        "has_negative_signal": bool(query_pmids.get("negative")),
        "has_mechanism_signal": bool(query_pmids.get("mechanism")),
        "earliest_publication_year": min(years) if years else "",
        "latest_publication_year": max(years) if years else "",
        "mean_publication_year": sum(years) / len(years) if years else "",
        "abstract_available_rate": abstract_count / n_metadata if n_metadata else 0.0,
        "pubmed_evidence_score": pubmed_evidence_score(
            len(unique_pmids),
            len(set(query_pmids.get("title_abstract", []))),
            len(set(query_pmids.get("clinical", []))),
            len(set(query_pmids.get("mechanism", []))),
            len(set(query_pmids.get("negative", []))),
        ),
        "status": "success" if unique_pmids and not errors else "partial_success" if unique_pmids else "failed" if errors else "skipped",
        "error_message": " | ".join(errors or []),
        "notes": "PubMed co-mention retrieval baseline only; not evidence polarity classification.",
    }
    return feature


def pubmed_evidence_score(
    n_unique_pmids: int,
    n_title_abstract: int,
    n_clinical: int,
    n_mechanism: int,
    n_negative: int,
) -> float:
    base = min(1.0, math.log1p(max(0, n_unique_pmids)) / math.log1p(100))
    score = base
    if n_clinical:
        score += 0.15
    if n_title_abstract:
        score += 0.10
    if n_mechanism:
        score += 0.10
    if n_negative:
        score -= 0.05
    return float(max(0.0, min(1.0, score)))


def make_pubmed_evidence_rows(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    queries: dict[str, str],
    query_pmids: dict[str, list[str]],
    metadata: dict[str, dict[str, Any]],
    feature: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for query_type, query in queries.items():
        for pmid in query_pmids.get(query_type, []):
            record = metadata.get(str(pmid), {"pmid": str(pmid)})
            rows.append(
                {
                    "pair_id": pair_id,
                    "drug_name": drug_name,
                    "disease_name": disease_name,
                    "query_type": query_type,
                    "query_string": query,
                    "pmid": str(pmid),
                    "title": record.get("title", ""),
                    "abstract": record.get("abstract", ""),
                    "journal": record.get("journal", ""),
                    "publication_year": record.get("publication_year", ""),
                    "publication_type": record.get("publication_type", ""),
                    "doi": record.get("doi", ""),
                    "source": PUBMED_SOURCE,
                    "status": feature["status"],
                    "error_message": feature["error_message"],
                    "notes": feature["notes"],
                }
            )
    return rows


def status_evidence_row(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    feature: dict[str, Any],
    query_item: tuple[str, str],
) -> dict[str, Any]:
    query_type, query = query_item
    return {
        "pair_id": pair_id,
        "drug_name": drug_name,
        "disease_name": disease_name,
        "query_type": query_type,
        "query_string": query,
        "pmid": "",
        "title": "",
        "abstract": "",
        "journal": "",
        "publication_year": "",
        "publication_type": "",
        "doi": "",
        "source": PUBMED_SOURCE,
        "status": feature["status"],
        "error_message": feature["error_message"],
        "notes": feature["notes"],
    }


def prepare_pubmed_outputs(
    pairs: pd.DataFrame,
    client: PubMedClient,
    max_pairs: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = pairs.head(max_pairs).copy() if max_pairs else pairs.copy()
    evidence_rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        try:
            evidence, feature = process_pubmed_pair(row.to_dict(), client)
        except Exception as exc:
            pair = row.to_dict()
            query_item = next(iter(build_pubmed_queries(str(pair.get("drug_name", "")), str(pair.get("disease_name", ""))).items()))
            feature = calculate_pubmed_features(
                str(pair.get("pair_id", "")),
                str(pair.get("drug_name", "")),
                str(pair.get("disease_name", "")),
                str(pair.get("expected_label", "")),
                {query_type: [] for query_type in QUERY_TYPES},
                {},
                [str(exc)],
            )
            evidence = [status_evidence_row(feature["pair_id"], feature["drug_name"], feature["disease_name"], feature, query_item)]
        evidence_rows.extend(evidence)
        feature_rows.append(feature)
    return (
        pd.DataFrame(evidence_rows, columns=PUBMED_EVIDENCE_COLUMNS),
        pd.DataFrame(feature_rows, columns=PUBMED_FEATURE_COLUMNS),
    )
