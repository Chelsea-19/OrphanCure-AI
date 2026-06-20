"""Download and validate the real repoDB source CSV."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd
import requests

from app.evaluation.repodb_benchmark import (
    DISEASE_NAME_COLUMNS,
    DRUG_NAME_COLUMNS,
    REPO_DB_FIGSHARE_COLLECTION_API,
    REPO_DB_SOURCE_DOI,
    STATUS_COLUMNS,
    normalize_key,
)


FIGSHARE_FINAL_DATABASE_API_URL = "https://api.figshare.com/v2/articles/5583040"
FIGSHARE_COLLECTION_ARTICLES_URL = REPO_DB_FIGSHARE_COLLECTION_API
GITHUB_REPO_TREE_URLS = (
    "https://api.github.com/repos/adam-sam-brown/repoDB/git/trees/master?recursive=1",
    "https://api.github.com/repos/adam-sam-brown/repoDB/git/trees/main?recursive=1",
)
GITHUB_RAW_BASE_URLS = (
    "https://raw.githubusercontent.com/adam-sam-brown/repoDB/master",
    "https://raw.githubusercontent.com/adam-sam-brown/repoDB/main",
)


@dataclass(frozen=True)
class SourceCandidate:
    """A downloadable repoDB source candidate."""

    source_name: str
    source_url: str
    original_filename: str
    priority: int


@dataclass(frozen=True)
class SourceValidationResult:
    """Validation details for a candidate source CSV."""

    valid: bool
    row_count: int
    column_names: list[str]
    errors: list[str]


@dataclass(frozen=True)
class PreparedSource:
    """Prepared source file and provenance metadata."""

    normalized_csv_path: Path
    metadata_path: Path
    metadata: dict[str, object]


class RepoDBDownloadError(RuntimeError):
    """Raised when no real repoDB source can be downloaded and validated."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_file(path: str | Path) -> SourceValidationResult:
    source_path = Path(path)
    errors: list[str] = []
    if not source_path.exists():
        return SourceValidationResult(False, 0, [], [f"file does not exist: {source_path}"])
    if source_path.stat().st_size <= 0:
        errors.append("file is empty")

    try:
        df = pd.read_csv(source_path)
    except Exception as exc:
        return SourceValidationResult(False, 0, [], errors + [f"could not read CSV: {exc}"])

    row_count = int(len(df))
    column_names = [str(column) for column in df.columns]
    normalized_columns = {normalize_key(column) for column in column_names}
    if row_count <= 100:
        errors.append("row count must be greater than 100")
    if not _has_any_column(normalized_columns, DRUG_NAME_COLUMNS):
        errors.append("no likely drug column found")
    if not _has_any_column(normalized_columns, DISEASE_NAME_COLUMNS):
        errors.append("no likely disease/indication column found")
    if not _has_any_column(normalized_columns, STATUS_COLUMNS):
        errors.append("no likely status column found")
    return SourceValidationResult(not errors, row_count, column_names, errors)


def _has_any_column(normalized_columns: set[str], candidates: tuple[str, ...]) -> bool:
    return any(normalize_key(candidate) in normalized_columns for candidate in candidates)


def create_source_metadata(
    source_name: str,
    source_url: str,
    original_filename: str,
    local_raw_path: str | Path,
    normalized_csv_path: str | Path,
    validation: SourceValidationResult,
    notes: str = "",
) -> dict[str, object]:
    normalized_path = Path(normalized_csv_path)
    return {
        "source_name": source_name,
        "source_url": source_url,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "original_filename": original_filename,
        "local_raw_path": str(Path(local_raw_path)),
        "normalized_csv_path": str(normalized_path),
        "file_size_bytes": int(normalized_path.stat().st_size),
        "sha256": sha256_file(normalized_path),
        "row_count": validation.row_count,
        "column_names": validation.column_names,
        "notes": notes,
    }


def write_prepared_source(
    raw_path: str | Path,
    candidate: SourceCandidate,
    normalized_csv_path: str | Path,
    metadata_path: str | Path,
    validation: SourceValidationResult | None = None,
) -> PreparedSource:
    raw = Path(raw_path)
    normalized = Path(normalized_csv_path)
    metadata_file = Path(metadata_path)
    normalized.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(raw, normalized)
    result = validation or validate_source_file(normalized)
    if not result.valid:
        normalized.unlink(missing_ok=True)
        raise RepoDBDownloadError(f"Downloaded repoDB source failed validation: {result.errors}")
    metadata = create_source_metadata(
        source_name=candidate.source_name,
        source_url=candidate.source_url,
        original_filename=candidate.original_filename,
        local_raw_path=raw,
        normalized_csv_path=normalized,
        validation=result,
        notes=(
            "Raw public repoDB source selected by scripts/download_repodb_source.py. "
            f"repoDB data DOI: {REPO_DB_SOURCE_DOI}."
        ),
    )
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return PreparedSource(normalized, metadata_file, metadata)


def download_repodb_source(
    raw_dir: str | Path,
    normalized_csv_path: str | Path,
    metadata_path: str | Path,
    timeout: int = 30,
    session_get: Callable[..., requests.Response] | None = None,
) -> PreparedSource:
    """Download, validate, and normalize the real repoDB source CSV."""
    getter = session_get or requests.get
    errors: list[str] = []
    raw_root = Path(raw_dir)
    raw_root.mkdir(parents=True, exist_ok=True)

    candidates = discover_source_candidates(timeout=timeout, session_get=getter)
    if not candidates:
        raise RepoDBDownloadError("No repoDB download candidates were discovered.")

    for candidate in candidates:
        try:
            raw_path = raw_root / _safe_filename(candidate.original_filename)
            response = getter(candidate.source_url, timeout=timeout)
            response.raise_for_status()
            raw_path.write_bytes(response.content)
            validation = validate_source_file(raw_path)
            if validation.valid:
                return write_prepared_source(
                    raw_path=raw_path,
                    candidate=candidate,
                    normalized_csv_path=normalized_csv_path,
                    metadata_path=metadata_path,
                    validation=validation,
                )
            raw_path.unlink(missing_ok=True)
            errors.append(f"{candidate.source_name} {candidate.source_url}: {validation.errors}")
        except Exception as exc:
            errors.append(f"{candidate.source_name} {candidate.source_url}: {exc}")

    raise RepoDBDownloadError("No repoDB source candidate passed validation. " + " | ".join(errors))


def discover_source_candidates(
    timeout: int = 30,
    session_get: Callable[..., requests.Response] | None = None,
) -> list[SourceCandidate]:
    getter = session_get or requests.get
    candidates: list[SourceCandidate] = []
    candidates.extend(_figshare_article_candidates(getter, FIGSHARE_FINAL_DATABASE_API_URL, "Figshare repoDB Final Database", 0, timeout))
    candidates.extend(_figshare_collection_candidates(getter, timeout))
    candidates.extend(_github_candidates(getter, timeout))
    return _dedupe_candidates(candidates)


def _figshare_article_candidates(
    getter: Callable[..., requests.Response],
    article_api_url: str,
    source_name: str,
    priority: int,
    timeout: int,
) -> list[SourceCandidate]:
    try:
        response = getter(article_api_url, timeout=timeout)
        response.raise_for_status()
        article = response.json()
    except Exception:
        return []
    return _candidates_from_figshare_article(article, source_name, priority)


def _figshare_collection_candidates(getter: Callable[..., requests.Response], timeout: int) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    try:
        response = getter(FIGSHARE_COLLECTION_ARTICLES_URL, timeout=timeout)
        response.raise_for_status()
        articles = response.json()
    except Exception:
        return candidates
    for article in articles:
        article_url = article.get("url")
        if not article_url:
            continue
        candidates.extend(
            _figshare_article_candidates(
                getter,
                article_url,
                "Figshare repoDB Data and Code Collection",
                1,
                timeout,
            )
        )
    return candidates


def _candidates_from_figshare_article(article: dict[str, object], source_name: str, priority: int) -> list[SourceCandidate]:
    title = normalize_key(article.get("title", ""))
    result = []
    for file_info in article.get("files", []) or []:
        name = str(file_info.get("name", ""))
        normalized_name = normalize_key(name)
        download_url = file_info.get("download_url")
        if not download_url:
            continue
        if "csv" not in normalized_name:
            continue
        score = _repo_candidate_score(title, normalized_name)
        if score >= 2:
            result.append(SourceCandidate(source_name, str(download_url), name, priority * 100 - score))
    return result


def _github_candidates(getter: Callable[..., requests.Response], timeout: int) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    for tree_url, raw_base in zip(GITHUB_REPO_TREE_URLS, GITHUB_RAW_BASE_URLS):
        try:
            response = getter(tree_url, timeout=timeout)
            response.raise_for_status()
            tree = response.json().get("tree", [])
        except Exception:
            continue
        for item in tree:
            path = item.get("path", "")
            if item.get("type") != "blob" or not str(path).lower().endswith(".csv"):
                continue
            normalized_path = normalize_key(path)
            if _repo_candidate_score("", normalized_path) < 2:
                continue
            raw_url = f"{raw_base}/{path}"
            candidates.append(
                SourceCandidate(
                    "Original repoDB GitHub repository",
                    raw_url,
                    Path(path).name,
                    200 - _repo_candidate_score("", normalized_path),
                )
            )
    return candidates


def _repo_candidate_score(title: str, name: str) -> int:
    text = f"{title} {name}"
    score = 0
    for token in ("repodb", "final", "database", "data"):
        if token in text:
            score += 1
    if "sample" in text or "example" in text:
        score -= 3
    return score


def _dedupe_candidates(candidates: list[SourceCandidate]) -> list[SourceCandidate]:
    seen: set[str] = set()
    unique: list[SourceCandidate] = []
    for candidate in sorted(candidates, key=lambda item: item.priority):
        if candidate.source_url in seen:
            continue
        seen.add(candidate.source_url)
        unique.append(candidate)
    return unique


def _safe_filename(filename: str) -> str:
    safe = "".join(char if char.isalnum() or char in "._-" else "_" for char in filename)
    return safe or "repodb_source.csv"


def manual_download_instructions() -> str:
    return (
        "Automatic repoDB download failed.\n"
        "Manual fallback:\n"
        "1. Open the Figshare repoDB Data and Code Collection DOI: "
        f"https://doi.org/{REPO_DB_SOURCE_DOI}\n"
        "2. Download the repoDB Final Database CSV from Figshare. If Figshare is unavailable, "
        "check the original authors' repository: https://github.com/adam-sam-brown/repoDB\n"
        "3. Place the real CSV here: data/external/repodb.csv\n"
        "4. Re-run: python scripts/prepare_repodb_benchmark.py --input data/external/repodb.csv "
        "--output data/benchmark/repodb_pairs.csv --balanced --max_pairs 200 --seed 42\n"
        "No toy or fabricated data was created."
    )

