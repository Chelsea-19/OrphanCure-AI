"""repoDB benchmark loading, prediction parsing, and evaluation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


REPO_DB_FIGSHARE_COLLECTION_DOI = "10.6084/m9.figshare.c.3462048"
REPO_DB_FIGSHARE_COLLECTION_API = "https://api.figshare.com/v2/collections/3462048/articles"
REPO_DB_CITATION = "Brown AS, Patel CJ. Scientific Data 4:170029 (2017). doi:10.1038/sdata.2017.29"

APPROVED_STATUSES = {"approve", "approved", "approved indication", "positive"}
FAILED_STATUSES = {
    "failed",
    "failure",
    "negative or failed",
    "negative_or_failed",
    "no development",
    "not approved",
    "program terminated",
    "suspended",
    "terminated",
    "trial halted",
    "withdrawn",
}

DRUG_NAME_COLUMNS = ("drug_name", "drug", "drug label", "drug_label", "drugname", "compound_name")
DRUG_ID_COLUMNS = ("drug_id", "drugbank_id", "drugbank id", "drugbank", "chembl_id", "chembl id")
DISEASE_NAME_COLUMNS = (
    "ind_name",
    "indication",
    "indication_name",
    "disease",
    "disease_name",
    "condition",
    "phenotype",
)
DISEASE_ID_COLUMNS = ("ind_id", "indication_id", "umls_id", "umls", "cui", "disease_id", "efo_id")
STATUS_COLUMNS = ("status", "raw_status", "expected_label", "indication_status", "trial_status", "current_status", "label")
SCORE_COLUMNS = ("score", "prediction_score", "rank_score", "confidence", "candidate_score")


@dataclass(frozen=True)
class EvaluationConfig:
    """Configuration recorded with every repoDB evaluation run."""

    repodb_path: Path
    predictions_path: Path
    out_dir: Path
    threshold: float = 0.5
    top_k: tuple[int, ...] = (1, 5, 10)
    smoke: bool = False
    smoke_limit: int = 20


def normalize_key(value: object) -> str:
    """Normalize free-text names and identifiers for deterministic matching."""
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip().casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_status(value: object) -> str:
    return normalize_key(value)


def _column_map(columns: Iterable[str]) -> dict[str, str]:
    return {normalize_key(col): col for col in columns}


def _find_column(df: pd.DataFrame, candidates: Iterable[str], required: bool = True) -> str | None:
    columns = _column_map(df.columns)
    for candidate in candidates:
        found = columns.get(normalize_key(candidate))
        if found:
            return found
    if required:
        raise ValueError(
            "Could not find any of these required columns: "
            f"{', '.join(candidates)}. Available columns: {', '.join(map(str, df.columns))}"
        )
    return None


def load_repodb(path: str | Path, limit: int | None = None) -> pd.DataFrame:
    """Load repoDB and normalize it to a minimal benchmark schema."""
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(
            f"repoDB file not found: {source_path}. Place the final repoDB CSV there, "
            "pass --download, or run --smoke for the bundled toy fixture."
        )

    raw = pd.read_csv(source_path)
    drug_name_col = _find_column(raw, DRUG_NAME_COLUMNS)
    disease_name_col = _find_column(raw, DISEASE_NAME_COLUMNS)
    status_col = _find_column(raw, STATUS_COLUMNS)
    drug_id_col = _find_column(raw, DRUG_ID_COLUMNS, required=False)
    disease_id_col = _find_column(raw, DISEASE_ID_COLUMNS, required=False)

    df = pd.DataFrame(
        {
            "benchmark": "repoDB",
            "benchmark_row_id": [f"repoDB:{i}" for i in range(len(raw))],
            "drug_name": raw[drug_name_col].fillna("").astype(str),
            "disease_name": raw[disease_name_col].fillna("").astype(str),
            "status": raw[status_col].fillna("").astype(str),
            "drug_id": raw[drug_id_col].fillna("").astype(str) if drug_id_col else "",
            "disease_id": raw[disease_id_col].fillna("").astype(str) if disease_id_col else "",
            "source_file": str(source_path),
            "source_citation": REPO_DB_CITATION,
            "source_doi": REPO_DB_FIGSHARE_COLLECTION_DOI,
        }
    )
    df["status_normalized"] = df["status"].map(normalize_status)
    df["label"] = df["status_normalized"].map(_status_to_label)
    unknown_statuses = sorted(set(df.loc[df["label"].isna(), "status"].astype(str)))
    if unknown_statuses:
        raise ValueError(f"Unsupported repoDB status value(s): {unknown_statuses}")

    df["label"] = df["label"].astype(int)
    df["drug_key"] = df["drug_name"].map(normalize_key)
    df["disease_key"] = df["disease_name"].map(normalize_key)
    df["drug_id_key"] = df["drug_id"].map(normalize_key)
    df["disease_id_key"] = df["disease_id"].map(normalize_key)
    df = df.drop_duplicates(subset=["drug_key", "disease_key", "status_normalized"]).reset_index(drop=True)
    if limit is not None:
        df = df.head(limit).copy()
    return df


def _status_to_label(status: str) -> int | None:
    if status in APPROVED_STATUSES:
        return 1
    if status in FAILED_STATUSES:
        return 0
    return None


def load_predictions(path: str | Path, limit: int | None = None) -> pd.DataFrame:
    """Load prediction CSV/JSON files or exported UnifiedRunState JSON."""
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Predictions file not found: {source_path}")

    if source_path.suffix.lower() == ".json":
        df = _load_json_predictions(source_path)
    else:
        df = pd.read_csv(source_path)

    drug_name_col = _find_column(df, DRUG_NAME_COLUMNS)
    disease_name_col = _find_column(df, DISEASE_NAME_COLUMNS)
    score_col = _find_column(df, SCORE_COLUMNS)
    drug_id_col = _find_column(df, DRUG_ID_COLUMNS, required=False)
    disease_id_col = _find_column(df, DISEASE_ID_COLUMNS, required=False)

    pred = pd.DataFrame(
        {
            "prediction_row_id": [f"prediction:{i}" for i in range(len(df))],
            "drug_name": df[drug_name_col].fillna("").astype(str),
            "disease_name": df[disease_name_col].fillna("").astype(str),
            "score": pd.to_numeric(df[score_col], errors="coerce"),
            "drug_id": df[drug_id_col].fillna("").astype(str) if drug_id_col else "",
            "disease_id": df[disease_id_col].fillna("").astype(str) if disease_id_col else "",
            "source_file": str(source_path),
        }
    )
    if pred["score"].isna().any():
        raise ValueError("Predictions contain non-numeric or missing scores.")
    pred["drug_key"] = pred["drug_name"].map(normalize_key)
    pred["disease_key"] = pred["disease_name"].map(normalize_key)
    pred["drug_id_key"] = pred["drug_id"].map(normalize_key)
    pred["disease_id_key"] = pred["disease_id"].map(normalize_key)
    if limit is not None:
        pred = pred.head(limit).copy()
    return pred


def _load_json_predictions(path: Path) -> pd.DataFrame:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return pd.DataFrame(data)

    if not isinstance(data, dict):
        raise ValueError("JSON predictions must be a list of rows or an exported UnifiedRunState object.")

    candidates = data.get("generated_candidates", [])
    disease = data.get("disease_entity") or {}
    disease_name = disease.get("name") or data.get("disease_input") or ""
    disease_id = disease.get("id") or ""
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "drug_name": candidate.get("name", ""),
                "drug_id": candidate.get("id", ""),
                "disease_name": disease_name,
                "disease_id": disease_id,
                "score": candidate.get("score", 0.0),
            }
        )
    return pd.DataFrame(rows)


def match_predictions(repodb: pd.DataFrame, predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Match predictions to repoDB by IDs when present, then by normalized names."""
    benchmark_by_id = repodb[
        (repodb["drug_id_key"] != "") & (repodb["disease_id_key"] != "")
    ].drop_duplicates(subset=["drug_id_key", "disease_id_key"])
    id_matches = predictions.merge(
        benchmark_by_id,
        on=["drug_id_key", "disease_id_key"],
        how="inner",
        suffixes=("_prediction", "_benchmark"),
    )

    id_matched_rows = set(id_matches["prediction_row_id"]) if not id_matches.empty else set()
    remaining = predictions[~predictions["prediction_row_id"].isin(id_matched_rows)].copy()
    benchmark_by_name = repodb.drop_duplicates(subset=["drug_key", "disease_key"])
    name_matches = remaining.merge(
        benchmark_by_name,
        on=["drug_key", "disease_key"],
        how="inner",
        suffixes=("_prediction", "_benchmark"),
    )
    matched = pd.concat([id_matches, name_matches], ignore_index=True, sort=False)
    matched_rows = set(matched["prediction_row_id"]) if not matched.empty else set()
    unmatched = predictions[~predictions["prediction_row_id"].isin(matched_rows)].copy()
    return matched, unmatched


def evaluate_matched_predictions(
    matched: pd.DataFrame,
    prediction_count: int,
    threshold: float = 0.5,
    top_k: Iterable[int] = (1, 5, 10),
) -> dict[str, object]:
    """Compute binary and ranking metrics for matched repoDB pairs."""
    if matched.empty:
        return {
            "prediction_rows": prediction_count,
            "matched_rows": 0,
            "coverage": 0.0,
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "roc_auc": None,
            "average_precision": None,
            "top_k": {},
        }

    labels = matched["label"].astype(int).tolist()
    scores = matched["score"].astype(float).tolist()
    predicted = [1 if score >= threshold else 0 for score in scores]
    tp = sum(1 for y, yhat in zip(labels, predicted) if y == 1 and yhat == 1)
    tn = sum(1 for y, yhat in zip(labels, predicted) if y == 0 and yhat == 0)
    fp = sum(1 for y, yhat in zip(labels, predicted) if y == 0 and yhat == 1)
    fn = sum(1 for y, yhat in zip(labels, predicted) if y == 1 and yhat == 0)

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall) if precision is not None and recall is not None else None
    matched_count = len(matched)
    return {
        "prediction_rows": prediction_count,
        "matched_rows": matched_count,
        "coverage": _safe_div(matched_count, prediction_count),
        "threshold": threshold,
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy": _safe_div(tp + tn, matched_count),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc(labels, scores),
        "average_precision": average_precision(labels, scores),
        "top_k": top_k_metrics(matched, top_k),
    }


def top_k_metrics(matched: pd.DataFrame, top_k: Iterable[int]) -> dict[str, dict[str, float | int | None]]:
    ranked = matched.sort_values("score", ascending=False)
    total_positives = int(ranked["label"].sum())
    result: dict[str, dict[str, float | int | None]] = {}
    for k in top_k:
        head = ranked.head(k)
        positives = int(head["label"].sum())
        result[str(k)] = {
            "k": k,
            "evaluated": len(head),
            "positives": positives,
            "precision_at_k": _safe_div(positives, len(head)),
            "recall_at_k": _safe_div(positives, total_positives),
        }
    return result


def roc_auc(labels: list[int], scores: list[float]) -> float | None:
    positives = [(score, i) for i, (label, score) in enumerate(zip(labels, scores)) if label == 1]
    negatives = [(score, i) for i, (label, score) in enumerate(zip(labels, scores)) if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    for pos_score, _ in positives:
        for neg_score, _ in negatives:
            if pos_score > neg_score:
                wins += 1.0
            elif pos_score == neg_score:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def average_precision(labels: list[int], scores: list[float]) -> float | None:
    total_positives = sum(labels)
    if total_positives == 0:
        return None
    ranked = sorted(zip(labels, scores), key=lambda row: row[1], reverse=True)
    precisions = []
    tp = 0
    for rank, (label, _) in enumerate(ranked, start=1):
        if label == 1:
            tp += 1
            precisions.append(tp / rank)
    return sum(precisions) / total_positives


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def run_repodb_evaluation(config: EvaluationConfig) -> dict[str, object]:
    """Run repoDB evaluation and write audit artifacts."""
    limit = config.smoke_limit if config.smoke else None
    repodb = load_repodb(config.repodb_path, limit=limit)
    predictions = load_predictions(config.predictions_path, limit=limit)
    matched, unmatched = match_predictions(repodb, predictions)
    metrics = evaluate_matched_predictions(matched, len(predictions), config.threshold, config.top_k)

    config.out_dir.mkdir(parents=True, exist_ok=True)
    matched.to_csv(config.out_dir / "matched_predictions.csv", index=False)
    unmatched.to_csv(config.out_dir / "unmatched_predictions.csv", index=False)
    (config.out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (config.out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "benchmark": "repoDB",
                "repodb_path": str(config.repodb_path),
                "predictions_path": str(config.predictions_path),
                "out_dir": str(config.out_dir),
                "threshold": config.threshold,
                "top_k": list(config.top_k),
                "smoke": config.smoke,
                "smoke_limit": config.smoke_limit,
                "source_citation": REPO_DB_CITATION,
                "source_doi": REPO_DB_FIGSHARE_COLLECTION_DOI,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return metrics


def download_repodb_csv(destination: str | Path, timeout: int = 30) -> Path:
    """Try to download the final repoDB CSV from Figshare.

    Figshare metadata can change, so callers should keep the documented local-file
    fallback available.
    """
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    articles = requests.get(REPO_DB_FIGSHARE_COLLECTION_API, timeout=timeout)
    articles.raise_for_status()
    for article in articles.json():
        article_url = article.get("url")
        if not article_url:
            continue
        article_resp = requests.get(article_url, timeout=timeout)
        article_resp.raise_for_status()
        details = article_resp.json()
        title = normalize_key(details.get("title", ""))
        for file_info in details.get("files", []):
            file_name = normalize_key(file_info.get("name", ""))
            download_url = file_info.get("download_url")
            if download_url and "csv" in file_name and ("repodb" in title or "final database" in title):
                data_resp = requests.get(download_url, timeout=timeout)
                data_resp.raise_for_status()
                destination_path.write_bytes(data_resp.content)
                return destination_path

    raise RuntimeError(
        "Could not locate a repoDB final CSV in the Figshare collection metadata. "
        "Download the final repoDB CSV manually from DOI 10.6084/m9.figshare.c.3462048 "
        f"and place it at {destination_path}."
    )
