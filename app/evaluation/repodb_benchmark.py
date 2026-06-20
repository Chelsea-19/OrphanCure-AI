"""Prepare and validate normalized repoDB benchmark files."""

from __future__ import annotations

import hashlib
import json
import random
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


REPO_DB_SOURCE_NAME = "repoDB"
REPO_DB_SOURCE_DOI = "10.6084/m9.figshare.c.3462048"
REPO_DB_FIGSHARE_COLLECTION_API = "https://api.figshare.com/v2/collections/3462048/articles"

REQUIRED_PAIR_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "raw_status",
    "expected_label",
    "source",
    "source_id",
    "notes",
)
REQUIRED_SPLIT_COLUMNS = ("pair_id", "split")
VALID_LABELS = {"positive", "negative_or_failed", "TODO_REVIEW"}
VALID_SPLITS = {"train", "dev", "test"}
VALID_OPEN_TARGETS_STATUSES = {"success", "partial_success", "failed", "skipped"}
VALID_GRAPH_STATUSES = {"success", "partial_success", "failed", "skipped"}
VALID_PUBMED_STATUSES = {"success", "partial_success", "failed", "skipped"}

OPENTARGETS_EVIDENCE_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "opentargets_drug_id",
    "opentargets_disease_id",
    "target_symbol",
    "target_id",
    "evidence_type",
    "association_score",
    "drug_target_support",
    "disease_target_support",
    "source",
    "source_url_or_id",
    "status",
    "error_message",
    "notes",
)
OPENTARGETS_FEATURE_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "drug_resolved",
    "disease_resolved",
    "n_disease_targets",
    "n_drug_targets",
    "n_overlapping_targets",
    "max_target_disease_score",
    "mean_target_disease_score",
    "has_known_drug_evidence",
    "has_target_overlap",
    "opentargets_support_score",
    "status",
    "error_message",
    "notes",
)
OPENTARGETS_NUMERIC_COLUMNS = (
    "n_disease_targets",
    "n_drug_targets",
    "n_overlapping_targets",
    "max_target_disease_score",
    "mean_target_disease_score",
    "opentargets_support_score",
)
OPENTARGETS_BOOLEAN_COLUMNS = (
    "drug_resolved",
    "disease_resolved",
    "has_known_drug_evidence",
    "has_target_overlap",
)
GRAPH_NODE_COLUMNS = (
    "node_id",
    "node_name",
    "node_type",
    "graph_source",
    "synonyms",
    "external_ids",
    "status",
    "notes",
)
GRAPH_EDGE_COLUMNS = (
    "source_node_id",
    "source_node_name",
    "source_node_type",
    "relation",
    "target_node_id",
    "target_node_name",
    "target_node_type",
    "graph_source",
    "evidence",
    "status",
    "notes",
)
GRAPH_MAPPING_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "mapped_drug_node_id",
    "mapped_drug_node_name",
    "mapped_disease_node_id",
    "mapped_disease_node_name",
    "drug_mapped",
    "disease_mapped",
    "mapping_confidence",
    "mapping_method",
    "status",
    "error_message",
    "notes",
)
GRAPH_PATH_COLUMNS = (
    "pair_id",
    "path_id",
    "path_length",
    "path_nodes",
    "path_relations",
    "path_node_types",
    "graph_source",
    "path_score",
    "status",
    "notes",
)
GRAPH_FEATURE_COLUMNS = (
    "pair_id",
    "graph_source",
    "drug_name",
    "disease_name",
    "drug_mapped",
    "disease_mapped",
    "has_path",
    "shortest_path_length",
    "n_paths_len_2",
    "n_paths_len_3",
    "n_paths_len_4",
    "n_drug_target_disease_paths",
    "n_gene_mediated_paths",
    "graph_connectivity_score",
    "status",
    "error_message",
    "notes",
)
GRAPH_MAPPING_NUMERIC_COLUMNS = ("mapping_confidence",)
GRAPH_PATH_NUMERIC_COLUMNS = ("path_length", "path_score")
GRAPH_FEATURE_NUMERIC_COLUMNS = (
    "shortest_path_length",
    "n_paths_len_2",
    "n_paths_len_3",
    "n_paths_len_4",
    "n_drug_target_disease_paths",
    "n_gene_mediated_paths",
    "graph_connectivity_score",
)
GRAPH_MAPPING_BOOLEAN_COLUMNS = ("drug_mapped", "disease_mapped")
GRAPH_FEATURE_BOOLEAN_COLUMNS = ("drug_mapped", "disease_mapped", "has_path")
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
PUBMED_NUMERIC_COLUMNS = (
    "n_pmids_direct",
    "n_pmids_title_abstract",
    "n_pmids_clinical",
    "n_pmids_negative",
    "n_pmids_mechanism",
    "n_unique_pmids",
    "earliest_publication_year",
    "latest_publication_year",
    "mean_publication_year",
    "abstract_available_rate",
    "pubmed_evidence_score",
)
PUBMED_BOOLEAN_COLUMNS = (
    "has_direct_evidence",
    "has_clinical_evidence",
    "has_negative_signal",
    "has_mechanism_signal",
)

DRUG_NAME_COLUMNS = ("drug_name", "drug", "drug label", "drug_label", "drugname", "compound_name")
DISEASE_NAME_COLUMNS = (
    "disease_name",
    "disease",
    "ind_name",
    "indication",
    "indication_name",
    "condition",
    "phenotype",
)
STATUS_COLUMNS = ("status", "raw_status", "indication_status", "trial_status", "current_status", "label")
SOURCE_ID_COLUMNS = (
    "source_id",
    "id",
    "drug_id",
    "drugbank_id",
    "drugbank",
    "chembl_id",
    "ind_id",
    "indication_id",
    "umls_id",
    "cui",
)

POSITIVE_STATUS_RULES = ("approved indication", "approved", "approve")
NEGATIVE_STATUS_RULES = (
    "not approved",
    "terminated",
    "withdrawn",
    "suspended",
    "failed",
    "failure",
    "no development",
    "program terminated",
    "trial halted",
)


@dataclass(frozen=True)
class PrepareRepoDBConfig:
    """Configuration for normalizing repoDB into benchmark files."""

    input_path: Path
    output_path: Path
    split_path: Path
    metadata_path: Path
    include_positive: bool = True
    include_negative: bool = True
    max_pairs: int | None = None
    balanced: bool = False
    seed: int = 42
    min_name_length: int = 2
    exclude_ambiguous: bool = True
    source_path_or_url: str = ""
    filtering_rules: dict[str, object] = field(default_factory=dict)


def normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def normalize_key(value: object) -> str:
    text = normalize_text(value).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def map_repodb_status(raw_status: object) -> str:
    """Map raw repoDB status text to a conservative benchmark label."""
    status = normalize_key(raw_status)
    if not status:
        return "TODO_REVIEW"
    if any(rule in status for rule in NEGATIVE_STATUS_RULES):
        return "negative_or_failed"
    if status in POSITIVE_STATUS_RULES or any(rule == status for rule in POSITIVE_STATUS_RULES):
        return "positive"
    return "TODO_REVIEW"


def make_pair_id(drug_name: object, disease_name: object, raw_status: object) -> str:
    """Create a deterministic pair ID from normalized names and status."""
    key = "|".join([normalize_key(drug_name), normalize_key(disease_name), normalize_key(raw_status)])
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"repodb_{digest}"


def _column_map(columns: Iterable[str]) -> dict[str, str]:
    return {normalize_key(column): column for column in columns}


def _find_column(df: pd.DataFrame, candidates: Iterable[str], required: bool = True) -> str | None:
    columns = _column_map(df.columns)
    for candidate in candidates:
        found = columns.get(normalize_key(candidate))
        if found:
            return found
    if required:
        raise ValueError(
            "Missing required repoDB column. Tried "
            f"{', '.join(candidates)}. Available columns: {', '.join(map(str, df.columns))}"
        )
    return None


def load_raw_repodb(path: str | Path) -> pd.DataFrame:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"repoDB input file not found: {source_path}")
    return pd.read_csv(source_path)


def normalize_repodb_dataframe(raw: pd.DataFrame, source_path_or_url: str = "") -> pd.DataFrame:
    """Normalize a raw repoDB CSV frame to the required benchmark schema."""
    drug_col = _find_column(raw, DRUG_NAME_COLUMNS)
    disease_col = _find_column(raw, DISEASE_NAME_COLUMNS)
    status_col = _find_column(raw, STATUS_COLUMNS)
    source_id_col = _find_column(raw, SOURCE_ID_COLUMNS, required=False)

    rows = []
    for index, row in raw.iterrows():
        drug_name = normalize_text(row[drug_col])
        disease_name = normalize_text(row[disease_col])
        raw_status = normalize_text(row[status_col])
        source_id = normalize_text(row[source_id_col]) if source_id_col else f"row:{index}"
        if not source_id:
            source_id = f"row:{index}"
        label = map_repodb_status(raw_status)
        rows.append(
            {
                "pair_id": make_pair_id(drug_name, disease_name, raw_status),
                "drug_name": drug_name,
                "disease_name": disease_name,
                "raw_status": raw_status,
                "expected_label": label,
                "source": source_path_or_url or REPO_DB_SOURCE_NAME,
                "source_id": source_id,
                "notes": "Needs manual review before scientific interpretation." if label == "TODO_REVIEW" else "",
            }
        )
    return pd.DataFrame(rows, columns=REQUIRED_PAIR_COLUMNS)


def filter_pairs(
    pairs: pd.DataFrame,
    include_positive: bool = True,
    include_negative: bool = True,
    max_pairs: int | None = None,
    balanced: bool = False,
    seed: int = 42,
    min_name_length: int = 2,
    exclude_ambiguous: bool = True,
) -> pd.DataFrame:
    """Apply deterministic filtering and optional class balancing."""
    filtered = pairs.copy()
    filtered = filtered[
        (filtered["drug_name"].str.len() >= min_name_length)
        & (filtered["disease_name"].str.len() >= min_name_length)
    ]
    if exclude_ambiguous:
        filtered = filtered[filtered["expected_label"] != "TODO_REVIEW"]
    if not include_positive:
        filtered = filtered[filtered["expected_label"] != "positive"]
    if not include_negative:
        filtered = filtered[filtered["expected_label"] != "negative_or_failed"]

    filtered = filtered.drop_duplicates(subset=["pair_id"]).reset_index(drop=True)
    if balanced:
        filtered = _balance_pairs(filtered, seed=seed)
    if max_pairs is not None:
        filtered = _sample_by_label(filtered, max_pairs=max_pairs, seed=seed)
    return filtered.sort_values("pair_id").reset_index(drop=True)


def _balance_pairs(pairs: pd.DataFrame, seed: int) -> pd.DataFrame:
    groups = [
        group.copy()
        for label, group in pairs.groupby("expected_label")
        if label in {"positive", "negative_or_failed"} and not group.empty
    ]
    if len(groups) < 2:
        return pairs
    min_count = min(len(group) for group in groups)
    sampled = [group.sample(n=min_count, random_state=seed) for group in groups]
    return pd.concat(sampled, ignore_index=True)


def _sample_by_label(pairs: pd.DataFrame, max_pairs: int, seed: int) -> pd.DataFrame:
    if len(pairs) <= max_pairs:
        return pairs
    rng = random.Random(seed)
    labels = sorted(pairs["expected_label"].unique())
    buckets = {label: pairs[pairs["expected_label"] == label].copy() for label in labels}
    selected_indices: list[int] = []
    while len(selected_indices) < max_pairs and any(not bucket.empty for bucket in buckets.values()):
        for label in labels:
            bucket = buckets[label]
            if bucket.empty or len(selected_indices) >= max_pairs:
                continue
            choice = rng.choice(list(bucket.index))
            selected_indices.append(choice)
            buckets[label] = bucket.drop(index=choice)
    return pairs.loc[selected_indices].copy()


def make_split(pairs: pd.DataFrame, seed: int = 42, dev_fraction: float = 0.2) -> pd.DataFrame:
    """Create dev/test splits while preserving class balance as much as possible."""
    split_rows = []
    for _, group in pairs.groupby("expected_label"):
        shuffled = group.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        if len(shuffled) == 1:
            dev_count = 0
        else:
            dev_count = max(1, round(len(shuffled) * dev_fraction))
            dev_count = min(dev_count, len(shuffled) - 1)
        for index, row in shuffled.iterrows():
            split_rows.append({"pair_id": row["pair_id"], "split": "dev" if index < dev_count else "test"})
    return pd.DataFrame(split_rows, columns=REQUIRED_SPLIT_COLUMNS).sort_values("pair_id").reset_index(drop=True)


def prepare_repodb_benchmark(config: PrepareRepoDBConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    raw = load_raw_repodb(config.input_path)
    source = config.source_path_or_url or str(config.input_path)
    normalized = normalize_repodb_dataframe(raw, source_path_or_url=source)
    pairs = filter_pairs(
        normalized,
        include_positive=config.include_positive,
        include_negative=config.include_negative,
        max_pairs=config.max_pairs,
        balanced=config.balanced,
        seed=config.seed,
        min_name_length=config.min_name_length,
        exclude_ambiguous=config.exclude_ambiguous,
    )
    split = make_split(pairs, seed=config.seed)
    metadata = make_metadata(config, normalized, pairs)

    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    config.split_path.parent.mkdir(parents=True, exist_ok=True)
    config.metadata_path.parent.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(config.output_path, index=False)
    split.to_csv(config.split_path, index=False)
    config.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return pairs, split, metadata


def make_metadata(
    config: PrepareRepoDBConfig,
    normalized: pd.DataFrame,
    pairs: pd.DataFrame,
) -> dict[str, object]:
    counts = pairs["expected_label"].value_counts().to_dict()
    filtering_rules = {
        "include_positive": config.include_positive,
        "include_negative": config.include_negative,
        "max_pairs": config.max_pairs,
        "balanced": config.balanced,
        "seed": config.seed,
        "min_name_length": config.min_name_length,
        "exclude_ambiguous": config.exclude_ambiguous,
    }
    filtering_rules.update(config.filtering_rules)
    return {
        "source_name": REPO_DB_SOURCE_NAME,
        "source_file_path_or_url": config.source_path_or_url or str(config.input_path),
        "source_doi": REPO_DB_SOURCE_DOI,
        "date_prepared": datetime.now(timezone.utc).isoformat(),
        "raw_rows": int(len(normalized)),
        "prepared_rows": int(len(pairs)),
        "number_of_positive_pairs": int(counts.get("positive", 0)),
        "number_of_negative_or_failed_pairs": int(counts.get("negative_or_failed", 0)),
        "number_of_todo_review_pairs": int(counts.get("TODO_REVIEW", 0)),
        "filtering_rules": filtering_rules,
        "label_mapping_rules": {
            "positive": list(POSITIVE_STATUS_RULES),
            "negative_or_failed": list(NEGATIVE_STATUS_RULES),
            "ambiguous_unknown_missing": "TODO_REVIEW unless --exclude_ambiguous is set",
        },
    }


def validate_benchmark_files(
    pairs_path: str | Path,
    split_path: str | Path | None = None,
    opentargets_evidence_path: str | Path | None = None,
    opentargets_features_path: str | Path | None = None,
    graph_nodes_path: str | Path | None = None,
    graph_edges_path: str | Path | None = None,
    graph_mappings_path: str | Path | None = None,
    graph_paths_path: str | Path | None = None,
    graph_features_path: str | Path | None = None,
    pubmed_features_path: str | Path | None = None,
    pubmed_evidence_path: str | Path | None = None,
) -> list[str]:
    """Return validation errors for prepared benchmark files."""
    errors: list[str] = []
    pairs_file = Path(pairs_path)
    if not pairs_file.exists():
        return [f"Pairs file does not exist: {pairs_file}"]
    pairs = pd.read_csv(pairs_file)

    errors.extend(_missing_columns(pairs, REQUIRED_PAIR_COLUMNS, "pairs"))
    if errors:
        return errors
    if not pairs["pair_id"].is_unique:
        errors.append("pairs.pair_id must be unique")
    if pairs["drug_name"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("pairs.drug_name contains empty values")
    if pairs["disease_name"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("pairs.disease_name contains empty values")
    invalid_labels = sorted(set(pairs["expected_label"]) - VALID_LABELS)
    if invalid_labels:
        errors.append(f"pairs.expected_label contains invalid values: {invalid_labels}")

    if split_path is not None:
        split_file = Path(split_path)
        if not split_file.exists():
            errors.append(f"Split file does not exist: {split_file}")
            return errors
        split = pd.read_csv(split_file)
        errors.extend(_missing_columns(split, REQUIRED_SPLIT_COLUMNS, "split"))
        if errors:
            return errors
        if not split["pair_id"].is_unique:
            errors.append("split.pair_id must be unique")
        invalid_splits = sorted(set(split["split"]) - VALID_SPLITS)
        if invalid_splits:
            errors.append(f"split.split contains invalid values: {invalid_splits}")
        pair_ids = set(pairs["pair_id"])
        split_ids = set(split["pair_id"])
        if pair_ids != split_ids:
            missing = sorted(pair_ids - split_ids)
            extra = sorted(split_ids - pair_ids)
            if missing:
                errors.append(f"split is missing pair_ids from pairs: {missing[:10]}")
            if extra:
                errors.append(f"split contains pair_ids not present in pairs: {extra[:10]}")
    if opentargets_evidence_path is not None:
        evidence_file = Path(opentargets_evidence_path)
        if not evidence_file.exists():
            errors.append(f"Open Targets evidence file does not exist: {evidence_file}")
        else:
            evidence = pd.read_csv(evidence_file)
            errors.extend(_validate_opentargets_evidence(evidence, set(pairs["pair_id"])))
    else:
        evidence = None

    if opentargets_features_path is not None:
        features_file = Path(opentargets_features_path)
        if not features_file.exists():
            errors.append(f"Open Targets features file does not exist: {features_file}")
        else:
            features = pd.read_csv(features_file)
            evidence_ids = set(evidence["pair_id"]) if evidence is not None and "pair_id" in evidence.columns else None
            errors.extend(_validate_opentargets_features(features, set(pairs["pair_id"]), evidence_ids))
    graph_tables: dict[str, pd.DataFrame] = {}
    graph_inputs = {
        "graph nodes": (graph_nodes_path, GRAPH_NODE_COLUMNS),
        "graph edges": (graph_edges_path, GRAPH_EDGE_COLUMNS),
        "graph mappings": (graph_mappings_path, GRAPH_MAPPING_COLUMNS),
        "graph paths": (graph_paths_path, GRAPH_PATH_COLUMNS),
        "graph features": (graph_features_path, GRAPH_FEATURE_COLUMNS),
    }
    for label, (path_value, columns) in graph_inputs.items():
        if path_value is None:
            continue
        table_path = Path(path_value)
        if not table_path.exists():
            errors.append(f"{label} file does not exist: {table_path}")
            continue
        table = pd.read_csv(table_path)
        graph_tables[label] = table
        errors.extend(_missing_columns(table, columns, label))
    if "graph nodes" in graph_tables:
        errors.extend(_validate_graph_nodes(graph_tables["graph nodes"]))
    if "graph edges" in graph_tables:
        errors.extend(_validate_graph_edges(graph_tables["graph edges"]))
    if "graph mappings" in graph_tables:
        errors.extend(_validate_graph_mappings(graph_tables["graph mappings"], set(pairs["pair_id"])))
    if "graph paths" in graph_tables:
        errors.extend(_validate_graph_paths(graph_tables["graph paths"], set(pairs["pair_id"])))
    if "graph features" in graph_tables:
        mapping_ids = set(graph_tables["graph mappings"]["pair_id"]) if "graph mappings" in graph_tables and "pair_id" in graph_tables["graph mappings"].columns else None
        path_ids = set(graph_tables["graph paths"]["pair_id"]) if "graph paths" in graph_tables and "pair_id" in graph_tables["graph paths"].columns else None
        errors.extend(_validate_graph_features(graph_tables["graph features"], set(pairs["pair_id"]), mapping_ids, path_ids))
    pubmed_evidence_ids = None
    if pubmed_evidence_path is not None:
        evidence_file = Path(pubmed_evidence_path)
        if not evidence_file.exists():
            errors.append(f"PubMed evidence file does not exist: {evidence_file}")
        else:
            pubmed_evidence = pd.read_csv(evidence_file)
            pubmed_evidence_ids = set(pubmed_evidence["pair_id"]) if "pair_id" in pubmed_evidence.columns else None
            errors.extend(_validate_pubmed_evidence(pubmed_evidence, set(pairs["pair_id"])))
    if pubmed_features_path is not None:
        features_file = Path(pubmed_features_path)
        if not features_file.exists():
            errors.append(f"PubMed features file does not exist: {features_file}")
        else:
            pubmed_features = pd.read_csv(features_file)
            errors.extend(_validate_pubmed_features(pubmed_features, set(pairs["pair_id"]), pubmed_evidence_ids))
    return errors


def _validate_opentargets_evidence(evidence: pd.DataFrame, valid_pair_ids: set[str]) -> list[str]:
    errors = _missing_columns(evidence, OPENTARGETS_EVIDENCE_COLUMNS, "Open Targets evidence")
    if errors:
        return errors
    invalid_pair_ids = sorted(set(evidence["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"Open Targets evidence contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(evidence["status"]) - VALID_OPEN_TARGETS_STATUSES)
    if invalid_statuses:
        errors.append(f"Open Targets evidence status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_boolean_columns(evidence, ("drug_target_support", "disease_target_support"), "Open Targets evidence"))
    scores = evidence["association_score"].fillna("").astype(str).str.strip()
    non_empty_scores = scores[scores != ""]
    if not non_empty_scores.empty and pd.to_numeric(non_empty_scores, errors="coerce").isna().any():
        errors.append("Open Targets evidence association_score contains non-numeric values")
    failed = evidence[evidence["status"] == "failed"]
    if not failed.empty and failed["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("Open Targets failed evidence rows must retain error_message")
    return errors


def _validate_opentargets_features(
    features: pd.DataFrame,
    valid_pair_ids: set[str],
    evidence_pair_ids: set[str] | None,
) -> list[str]:
    errors = _missing_columns(features, OPENTARGETS_FEATURE_COLUMNS, "Open Targets features")
    if errors:
        return errors
    if not features["pair_id"].is_unique:
        errors.append("Open Targets features pair_id must be unique")
    invalid_pair_ids = sorted(set(features["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"Open Targets features contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(features["status"]) - VALID_OPEN_TARGETS_STATUSES)
    if invalid_statuses:
        errors.append(f"Open Targets features status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_boolean_columns(features, OPENTARGETS_BOOLEAN_COLUMNS, "Open Targets features"))
    for column in OPENTARGETS_NUMERIC_COLUMNS:
        if pd.to_numeric(features[column], errors="coerce").isna().any():
            errors.append(f"Open Targets features {column} contains non-numeric values")
    failed = features[features["status"] == "failed"]
    if not failed.empty and failed["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("Open Targets failed feature rows must retain error_message")
    unresolved = features[(features["drug_resolved"].map(_coerce_bool) == False) | (features["disease_resolved"].map(_coerce_bool) == False)]
    if not unresolved.empty and unresolved["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("Open Targets unresolved feature rows must retain error_message")
    if evidence_pair_ids is not None and set(features["pair_id"]) != evidence_pair_ids:
        errors.append("Open Targets evidence and feature pair_id sets must match; possible silent row drop")
    return errors


def _validate_boolean_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> list[str]:
    errors = []
    for column in columns:
        invalid = [value for value in df[column].dropna().unique() if _coerce_bool(value) is None]
        if invalid:
            errors.append(f"{label} {column} contains invalid boolean values: {invalid[:10]}")
    return errors


def _coerce_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().casefold()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _validate_graph_nodes(nodes: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    if any(column not in nodes.columns for column in GRAPH_NODE_COLUMNS):
        return errors
    if not nodes["node_id"].is_unique:
        errors.append("graph nodes node_id must be unique")
    invalid_statuses = sorted(set(nodes["status"]) - VALID_GRAPH_STATUSES)
    if invalid_statuses:
        errors.append(f"graph nodes status contains invalid values: {invalid_statuses}")
    return errors


def _validate_graph_edges(edges: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    if any(column not in edges.columns for column in GRAPH_EDGE_COLUMNS):
        return errors
    invalid_statuses = sorted(set(edges["status"]) - VALID_GRAPH_STATUSES)
    if invalid_statuses:
        errors.append(f"graph edges status contains invalid values: {invalid_statuses}")
    return errors


def _validate_graph_mappings(mappings: pd.DataFrame, valid_pair_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if any(column not in mappings.columns for column in GRAPH_MAPPING_COLUMNS):
        return errors
    if not mappings["pair_id"].is_unique:
        errors.append("graph mappings pair_id must be unique")
    invalid_pair_ids = sorted(set(mappings["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"graph mappings contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(mappings["status"]) - VALID_GRAPH_STATUSES)
    if invalid_statuses:
        errors.append(f"graph mappings status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_boolean_columns(mappings, GRAPH_MAPPING_BOOLEAN_COLUMNS, "graph mappings"))
    errors.extend(_validate_numeric_columns(mappings, GRAPH_MAPPING_NUMERIC_COLUMNS, "graph mappings"))
    unmapped = mappings[(mappings["drug_mapped"].map(_coerce_bool) == False) | (mappings["disease_mapped"].map(_coerce_bool) == False)]
    if not unmapped.empty and unmapped["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("graph unmapped mapping rows must retain error_message")
    return errors


def _validate_graph_paths(paths: pd.DataFrame, valid_pair_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if any(column not in paths.columns for column in GRAPH_PATH_COLUMNS):
        return errors
    if not paths.empty and not paths["path_id"].is_unique:
        errors.append("graph paths path_id must be unique")
    invalid_pair_ids = sorted(set(paths["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"graph paths contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(paths["status"]) - VALID_GRAPH_STATUSES)
    if invalid_statuses:
        errors.append(f"graph paths status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_numeric_columns(paths, GRAPH_PATH_NUMERIC_COLUMNS, "graph paths"))
    return errors


def _validate_graph_features(
    features: pd.DataFrame,
    valid_pair_ids: set[str],
    mapping_pair_ids: set[str] | None,
    path_pair_ids: set[str] | None,
) -> list[str]:
    errors: list[str] = []
    if any(column not in features.columns for column in GRAPH_FEATURE_COLUMNS):
        return errors
    if not features["pair_id"].is_unique:
        errors.append("graph features pair_id must be unique")
    invalid_pair_ids = sorted(set(features["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"graph features contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(features["status"]) - VALID_GRAPH_STATUSES)
    if invalid_statuses:
        errors.append(f"graph features status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_boolean_columns(features, GRAPH_FEATURE_BOOLEAN_COLUMNS, "graph features"))
    errors.extend(_validate_numeric_columns(features, GRAPH_FEATURE_NUMERIC_COLUMNS, "graph features"))
    unmapped = features[(features["drug_mapped"].map(_coerce_bool) == False) | (features["disease_mapped"].map(_coerce_bool) == False)]
    if not unmapped.empty and unmapped["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("graph unmapped feature rows must retain error_message")
    if mapping_pair_ids is not None and set(features["pair_id"]) != mapping_pair_ids:
        errors.append("graph mappings and features pair_id sets must match; possible silent row drop")
    if path_pair_ids is not None and not path_pair_ids.issubset(set(features["pair_id"])):
        errors.append("graph paths contain pair_ids absent from graph features")
    return errors


def _validate_numeric_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> list[str]:
    errors = []
    for column in columns:
        if column in df.columns and pd.to_numeric(df[column], errors="coerce").isna().any():
            errors.append(f"{label} {column} contains non-numeric values")
    return errors


def _validate_pubmed_evidence(evidence: pd.DataFrame, valid_pair_ids: set[str]) -> list[str]:
    errors = _missing_columns(evidence, PUBMED_EVIDENCE_COLUMNS, "PubMed evidence")
    if errors:
        return errors
    invalid_pair_ids = sorted(set(evidence["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"PubMed evidence contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(evidence["status"]) - VALID_PUBMED_STATUSES)
    if invalid_statuses:
        errors.append(f"PubMed evidence status contains invalid values: {invalid_statuses}")
    successful = evidence[evidence["status"].isin(["success", "partial_success"])]
    successful_with_titles = successful[successful["title"].fillna("").astype(str).str.strip() != ""]
    if not successful_with_titles.empty and successful_with_titles["pmid"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("PubMed successful evidence rows with article metadata must include PMID")
    failed = evidence[evidence["status"] == "failed"]
    if not failed.empty and failed["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("PubMed failed evidence rows must retain error_message")
    return errors


def _validate_pubmed_features(
    features: pd.DataFrame,
    valid_pair_ids: set[str],
    evidence_pair_ids: set[str] | None,
) -> list[str]:
    errors = _missing_columns(features, PUBMED_FEATURE_COLUMNS, "PubMed features")
    if errors:
        return errors
    if not features["pair_id"].is_unique:
        errors.append("PubMed features pair_id must be unique")
    invalid_pair_ids = sorted(set(features["pair_id"]) - valid_pair_ids)
    if invalid_pair_ids:
        errors.append(f"PubMed features contains pair_ids not present in pairs: {invalid_pair_ids[:10]}")
    invalid_statuses = sorted(set(features["status"]) - VALID_PUBMED_STATUSES)
    if invalid_statuses:
        errors.append(f"PubMed features status contains invalid values: {invalid_statuses}")
    errors.extend(_validate_boolean_columns(features, PUBMED_BOOLEAN_COLUMNS, "PubMed features"))
    for column in PUBMED_NUMERIC_COLUMNS:
        values = features[column].fillna("").astype(str).str.strip()
        non_empty = values[values != ""]
        if not non_empty.empty and pd.to_numeric(non_empty, errors="coerce").isna().any():
            errors.append(f"PubMed features {column} contains non-numeric values")
    failed = features[features["status"] == "failed"]
    if not failed.empty and failed["error_message"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("PubMed failed feature rows must retain error_message")
    if evidence_pair_ids is not None and set(features["pair_id"]) != evidence_pair_ids:
        errors.append("PubMed evidence and feature pair_id sets must match; possible silent row drop")
    return errors


def _missing_columns(df: pd.DataFrame, required: Iterable[str], label: str) -> list[str]:
    missing = [column for column in required if column not in df.columns]
    if missing:
        return [f"{label} file is missing required columns: {missing}"]
    return []


def download_repodb_to_temp(timeout: int = 30) -> tuple[Path, str]:
    """Best-effort download of a repoDB CSV through Figshare metadata."""
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
            name = normalize_key(file_info.get("name", ""))
            download_url = file_info.get("download_url")
            if download_url and "csv" in name and ("repodb" in title or "final database" in title):
                data_resp = requests.get(download_url, timeout=timeout)
                data_resp.raise_for_status()
                handle = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                handle.write(data_resp.content)
                handle.close()
                return Path(handle.name), download_url
    raise RuntimeError(
        "Could not find a repoDB CSV download URL in Figshare metadata. "
        "Use --input data/external/repodb.csv after downloading repoDB manually."
    )
