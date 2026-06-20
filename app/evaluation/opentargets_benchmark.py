"""Open Targets enrichment for prepared repoDB benchmark pairs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests


OPEN_TARGETS_API_URL = "https://api.platform.opentargets.org/api/v4/graphql"
OPEN_TARGETS_SOURCE = "Open Targets Platform GraphQL API"

EVIDENCE_COLUMNS = (
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

FEATURE_COLUMNS = (
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

VALID_OPEN_TARGETS_STATUSES = {"success", "partial_success", "failed", "skipped"}


SEARCH_QUERY = """
query Search($q: String!, $entities: [String!]) {
  search(queryString: $q, entityNames: $entities, page: {index: 0, size: 5}) {
    hits { id, name, score, entity }
  }
}
"""

DISEASE_TARGETS_QUERY = """
query DiseaseTargets($id: String!) {
  disease(efoId: $id) {
    id
    name
    associatedTargets(page: {index: 0, size: 100}) {
      rows {
        score
        target { id approvedSymbol approvedName }
      }
    }
  }
}
"""

DRUG_TARGETS_QUERY = """
query DrugTargets($id: String!) {
  drug(chemblId: $id) {
    id
    name
    mechanismsOfAction {
      rows {
        actionType
        mechanismOfAction
        targets { id approvedSymbol approvedName }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class OpenTargetsConfig:
    """Runtime controls for Open Targets enrichment."""

    api_url: str = OPEN_TARGETS_API_URL
    cache_dir: Path = Path("data/external/opentargets_cache")
    use_cached: bool = False
    skip_api_if_missing: bool = False
    timeout: int = 30


@dataclass(frozen=True)
class ResolvedEntity:
    """A best-effort Open Targets entity resolution result."""

    query_name: str
    entity_type: str
    resolved: bool
    opentargets_id: str = ""
    opentargets_name: str = ""
    score: float = 0.0
    error_message: str = ""


class OpenTargetsClient:
    """Small GraphQL client with deterministic JSON caching."""

    def __init__(self, config: OpenTargetsConfig):
        self.config = config

    def query(self, operation: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        cache_key = make_cache_key(operation, variables)
        if self.config.use_cached:
            cached = load_cached_json(self.config.cache_dir, cache_key)
            if cached is not None:
                return cached
            if self.config.skip_api_if_missing:
                raise FileNotFoundError(f"Missing cached Open Targets response: {cache_key}.json")

        response = requests.post(
            self.config.api_url,
            json={"query": query, "variables": variables},
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError(f"Open Targets GraphQL errors: {payload['errors']}")
        write_cached_json(self.config.cache_dir, cache_key, payload)
        return payload


def make_cache_key(operation: str, variables: dict[str, Any]) -> str:
    raw = json.dumps({"operation": operation, "variables": variables}, sort_keys=True)
    return f"{operation}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def load_cached_json(cache_dir: str | Path, cache_key: str) -> dict[str, Any] | None:
    path = Path(cache_dir) / f"{cache_key}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_cached_json(cache_dir: str | Path, cache_key: str, payload: dict[str, Any]) -> Path:
    path = Path(cache_dir) / f"{cache_key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def normalize_name(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return " ".join(str(value).strip().casefold().split())


def resolve_entity(client: OpenTargetsClient, name: str, entity_type: str) -> ResolvedEntity:
    if not name:
        return ResolvedEntity(name, entity_type, False, error_message="empty entity name")
    try:
        payload = client.query(
            f"search_{entity_type}",
            SEARCH_QUERY,
            {"q": name, "entities": [entity_type]},
        )
        hits = payload.get("data", {}).get("search", {}).get("hits", []) or []
        if not hits:
            return ResolvedEntity(name, entity_type, False, error_message=f"no {entity_type} search hits")
        best = sorted(hits, key=lambda hit: float(hit.get("score") or 0.0), reverse=True)[0]
        return ResolvedEntity(
            query_name=name,
            entity_type=entity_type,
            resolved=True,
            opentargets_id=str(best.get("id") or ""),
            opentargets_name=str(best.get("name") or ""),
            score=float(best.get("score") or 0.0),
        )
    except Exception as exc:
        return ResolvedEntity(name, entity_type, False, error_message=str(exc))


def extract_disease_targets(client: OpenTargetsClient, disease_id: str) -> tuple[list[dict[str, Any]], str]:
    if not disease_id:
        return [], "missing disease id"
    try:
        payload = client.query("disease_targets", DISEASE_TARGETS_QUERY, {"id": disease_id})
        disease = payload.get("data", {}).get("disease") or {}
        rows = disease.get("associatedTargets", {}).get("rows", []) or []
        targets = []
        for row in rows:
            target = row.get("target") or {}
            target_id = str(target.get("id") or "")
            symbol = str(target.get("approvedSymbol") or "")
            if not target_id and not symbol:
                continue
            targets.append(
                {
                    "target_id": target_id,
                    "target_symbol": symbol,
                    "target_name": str(target.get("approvedName") or ""),
                    "association_score": float(row.get("score") or 0.0),
                }
            )
        return targets, ""
    except Exception as exc:
        return [], str(exc)


def extract_drug_targets(client: OpenTargetsClient, drug_id: str) -> tuple[list[dict[str, Any]], str]:
    if not drug_id:
        return [], "missing drug id"
    try:
        payload = client.query("drug_targets", DRUG_TARGETS_QUERY, {"id": drug_id})
        drug = payload.get("data", {}).get("drug") or {}
        rows = drug.get("mechanismsOfAction", {}).get("rows", []) or []
        targets = []
        for row in rows:
            for target in row.get("targets") or []:
                target_id = str(target.get("id") or "")
                symbol = str(target.get("approvedSymbol") or "")
                if not target_id and not symbol:
                    continue
                targets.append(
                    {
                        "target_id": target_id,
                        "target_symbol": symbol,
                        "target_name": str(target.get("approvedName") or ""),
                        "action_type": str(row.get("actionType") or ""),
                        "mechanism_of_action": str(row.get("mechanismOfAction") or ""),
                    }
                )
        return dedupe_targets(targets), ""
    except Exception as exc:
        return [], str(exc)


def extract_known_drugs(client: OpenTargetsClient, disease_id: str) -> tuple[list[dict[str, Any]], str]:
    """Return known-drug rows when supported by the current API schema.

    The current public GraphQL schema no longer exposes `knownDrugs` on `Disease`.
    Keeping this as an explicit no-op avoids fabricating known-drug evidence while
    preserving a stable feature column.
    """
    return [], ""


def dedupe_targets(targets: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for target in targets:
        key = target_key(target)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(target)
    return deduped


def target_key(target: dict[str, Any]) -> str:
    return normalize_name(target.get("target_id") or target.get("target_symbol") or "")


def calculate_target_overlap(
    drug_targets: list[dict[str, Any]],
    disease_targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    disease_by_key = {target_key(target): target for target in disease_targets if target_key(target)}
    overlaps = []
    for drug_target in drug_targets:
        key = target_key(drug_target)
        if key and key in disease_by_key:
            disease_target = disease_by_key[key]
            overlaps.append(
                {
                    "target_id": disease_target.get("target_id") or drug_target.get("target_id") or "",
                    "target_symbol": disease_target.get("target_symbol") or drug_target.get("target_symbol") or "",
                    "association_score": float(disease_target.get("association_score") or 0.0),
                    "drug_target": drug_target,
                    "disease_target": disease_target,
                }
            )
    return overlaps


def known_drug_matches(known_drugs: list[dict[str, Any]], drug: ResolvedEntity, drug_name: str) -> list[dict[str, Any]]:
    query_key = normalize_name(drug_name)
    id_key = normalize_name(drug.opentargets_id)
    matches = []
    for row in known_drugs:
        if id_key and normalize_name(row.get("drug_id")) == id_key:
            matches.append(row)
        elif query_key and normalize_name(row.get("drug_name")) == query_key:
            matches.append(row)
    return matches


def calculate_support_features(
    drug_resolved: bool,
    disease_resolved: bool,
    disease_targets: list[dict[str, Any]],
    drug_targets: list[dict[str, Any]],
    overlaps: list[dict[str, Any]],
    known_matches: list[dict[str, Any]],
    error_messages: list[str] | None = None,
) -> dict[str, Any]:
    scores = [float(row.get("association_score") or 0.0) for row in overlaps]
    max_score = max(scores) if scores else 0.0
    mean_score = sum(scores) / len(scores) if scores else 0.0
    has_known = bool(known_matches)
    has_overlap = bool(overlaps)
    support_score = min(1.0, (0.6 * max_score) + (0.3 if has_known else 0.0) + (0.1 if has_overlap else 0.0))
    errors = [message for message in (error_messages or []) if message]
    if drug_resolved and disease_resolved and not errors:
        status = "success"
    elif drug_resolved or disease_resolved or disease_targets or drug_targets or known_matches or overlaps:
        status = "partial_success"
    else:
        status = "failed"
    return {
        "drug_resolved": bool(drug_resolved),
        "disease_resolved": bool(disease_resolved),
        "n_disease_targets": len(disease_targets),
        "n_drug_targets": len(drug_targets),
        "n_overlapping_targets": len(overlaps),
        "max_target_disease_score": max_score,
        "mean_target_disease_score": mean_score,
        "has_known_drug_evidence": has_known,
        "has_target_overlap": has_overlap,
        "opentargets_support_score": support_score,
        "status": status,
        "error_message": " | ".join(errors),
    }


def enrich_pair(pair: dict[str, Any], client: OpenTargetsClient) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pair_id = str(pair.get("pair_id", ""))
    drug_name = str(pair.get("drug_name", ""))
    disease_name = str(pair.get("disease_name", ""))
    notes = "Open Targets is external support evidence, not a clinical gold label."

    errors: list[str] = []
    drug = resolve_entity(client, drug_name, "drug")
    disease = resolve_entity(client, disease_name, "disease")
    if drug.error_message:
        errors.append(f"drug_resolution: {drug.error_message}")
    if disease.error_message:
        errors.append(f"disease_resolution: {disease.error_message}")

    disease_targets: list[dict[str, Any]] = []
    drug_targets: list[dict[str, Any]] = []
    known_drugs: list[dict[str, Any]] = []
    if disease.resolved:
        disease_targets, err = extract_disease_targets(client, disease.opentargets_id)
        if err:
            errors.append(f"disease_targets: {err}")
        known_drugs, err = extract_known_drugs(client, disease.opentargets_id)
        if err:
            errors.append(f"known_drugs: {err}")
    if drug.resolved:
        drug_targets, err = extract_drug_targets(client, drug.opentargets_id)
        if err:
            errors.append(f"drug_targets: {err}")

    overlaps = calculate_target_overlap(drug_targets, disease_targets)
    known_matches = known_drug_matches(known_drugs, drug, drug_name)
    features = calculate_support_features(
        drug.resolved,
        disease.resolved,
        disease_targets,
        drug_targets,
        overlaps,
        known_matches,
        errors,
    )
    feature_row = {
        "pair_id": pair_id,
        "drug_name": drug_name,
        "disease_name": disease_name,
        **features,
        "notes": notes,
    }

    evidence_rows = make_evidence_rows(pair_id, drug_name, disease_name, drug, disease, overlaps, known_matches, feature_row)
    if not evidence_rows:
        evidence_rows.append(status_evidence_row(pair_id, drug_name, disease_name, drug, disease, feature_row, notes))
    return evidence_rows, feature_row


def make_evidence_rows(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    drug: ResolvedEntity,
    disease: ResolvedEntity,
    overlaps: list[dict[str, Any]],
    known_matches: list[dict[str, Any]],
    feature_row: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for overlap in overlaps:
        rows.append(
            base_evidence_row(pair_id, drug_name, disease_name, drug, disease, feature_row)
            | {
                "target_symbol": overlap.get("target_symbol", ""),
                "target_id": overlap.get("target_id", ""),
                "evidence_type": "target_overlap",
                "association_score": overlap.get("association_score", 0.0),
                "drug_target_support": True,
                "disease_target_support": True,
                "source_url_or_id": disease.opentargets_id,
            }
        )
    for known in known_matches:
        rows.append(
            base_evidence_row(pair_id, drug_name, disease_name, drug, disease, feature_row)
            | {
                "target_symbol": known.get("target_symbol", ""),
                "target_id": known.get("target_id", ""),
                "evidence_type": "known_drug",
                "association_score": "",
                "drug_target_support": bool(known.get("target_id") or known.get("target_symbol")),
                "disease_target_support": True,
                "source_url_or_id": disease.opentargets_id,
            }
        )
    return rows


def base_evidence_row(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    drug: ResolvedEntity,
    disease: ResolvedEntity,
    feature_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "pair_id": pair_id,
        "drug_name": drug_name,
        "disease_name": disease_name,
        "opentargets_drug_id": drug.opentargets_id,
        "opentargets_disease_id": disease.opentargets_id,
        "target_symbol": "",
        "target_id": "",
        "evidence_type": "",
        "association_score": "",
        "drug_target_support": False,
        "disease_target_support": False,
        "source": OPEN_TARGETS_SOURCE,
        "source_url_or_id": "",
        "status": feature_row["status"],
        "error_message": feature_row["error_message"],
        "notes": feature_row["notes"],
    }


def status_evidence_row(
    pair_id: str,
    drug_name: str,
    disease_name: str,
    drug: ResolvedEntity,
    disease: ResolvedEntity,
    feature_row: dict[str, Any],
    notes: str,
) -> dict[str, Any]:
    row = base_evidence_row(pair_id, drug_name, disease_name, drug, disease, feature_row)
    row["evidence_type"] = "status"
    row["notes"] = notes
    return row


def enrich_pairs(
    pairs: pd.DataFrame,
    client: OpenTargetsClient,
    max_pairs: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    evidence: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    selected = pairs.head(max_pairs).copy() if max_pairs else pairs.copy()
    for _, pair in selected.iterrows():
        try:
            rows, feature = enrich_pair(pair.to_dict(), client)
        except Exception as exc:
            pair_id = str(pair.get("pair_id", ""))
            drug_name = str(pair.get("drug_name", ""))
            disease_name = str(pair.get("disease_name", ""))
            feature = {
                "pair_id": pair_id,
                "drug_name": drug_name,
                "disease_name": disease_name,
                "drug_resolved": False,
                "disease_resolved": False,
                "n_disease_targets": 0,
                "n_drug_targets": 0,
                "n_overlapping_targets": 0,
                "max_target_disease_score": 0.0,
                "mean_target_disease_score": 0.0,
                "has_known_drug_evidence": False,
                "has_target_overlap": False,
                "opentargets_support_score": 0.0,
                "status": "failed",
                "error_message": str(exc),
                "notes": "Pair-level Open Targets enrichment failed; row retained for audit.",
            }
            rows = [status_evidence_row(pair_id, drug_name, disease_name, ResolvedEntity(drug_name, "drug", False), ResolvedEntity(disease_name, "disease", False), feature, feature["notes"])]
        evidence.extend(rows)
        features.append(feature)
    return pd.DataFrame(evidence, columns=EVIDENCE_COLUMNS), pd.DataFrame(features, columns=FEATURE_COLUMNS)


def write_opentargets_outputs(
    evidence: pd.DataFrame,
    features: pd.DataFrame,
    evidence_path: str | Path,
    features_path: str | Path,
) -> None:
    evidence_output = Path(evidence_path)
    features_output = Path(features_path)
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    features_output.parent.mkdir(parents=True, exist_ok=True)
    evidence.to_csv(evidence_output, index=False)
    features.to_csv(features_output, index=False)


def summarize_feature_status(features: pd.DataFrame) -> dict[str, int]:
    return {status: int(count) for status, count in features["status"].value_counts().items()}
