"""Deterministic selection utilities for scaled full-agent evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.evaluation.unified_benchmark import NEGATIVE_LABEL, POSITIVE_LABEL, coerce_bool_series, numeric_series


LABELS = (POSITIVE_LABEL, NEGATIVE_LABEL)
SPLITS = ("dev", "test")


def evidence_availability_score(df: pd.DataFrame) -> pd.Series:
    """Score rows by available evidence layers and extracted support features."""
    pubmed = coerce_bool_series(df["pubmed_available"]) if "pubmed_available" in df.columns else pd.Series(False, index=df.index)
    ot = coerce_bool_series(df["opentargets_available"]) if "opentargets_available" in df.columns else pd.Series(False, index=df.index)
    graph = coerce_bool_series(df["graph_available"]) if "graph_available" in df.columns else pd.Series(False, index=df.index)
    pubmed_score = numeric_series(df, "pubmed_evidence_score")
    ot_score = numeric_series(df, "opentargets_support_score")
    graph_score = numeric_series(df, "graph_connectivity_score")
    return (
        4.0 * pubmed.astype(float)
        + 3.0 * ot.astype(float)
        + 2.0 * graph.astype(float)
        + pubmed_score.clip(0, 1)
        + 0.5 * ot_score.clip(0, 1)
        + 0.5 * graph_score.clip(0, 1)
    )


def build_selection_frame(repodb_pairs: pd.DataFrame, split: pd.DataFrame, unified: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Join benchmark metadata and rank rows for scaled full-agent runs."""
    base = repodb_pairs[["pair_id", "drug_name", "disease_name", "expected_label"]].copy()
    if "split" not in base.columns and {"pair_id", "split"}.issubset(split.columns):
        base = base.merge(split[["pair_id", "split"]].drop_duplicates("pair_id"), on="pair_id", how="left")
    elif "split" not in base.columns:
        base["split"] = "unspecified"

    feature_cols = [
        "pair_id",
        "pubmed_available",
        "opentargets_available",
        "graph_available",
        "pubmed_evidence_score",
        "opentargets_support_score",
        "graph_connectivity_score",
        "unified_status",
    ]
    keep = [column for column in feature_cols if column in unified.columns]
    out = base.merge(unified[keep].drop_duplicates("pair_id"), on="pair_id", how="left")
    for column in ("pubmed_available", "opentargets_available", "graph_available"):
        if column not in out.columns:
            out[column] = False
        out[column] = coerce_bool_series(out[column])
    out["evidence_availability_score"] = evidence_availability_score(out)
    out["_tie_breaker"] = out["pair_id"].map(lambda value: _stable_random(str(value), seed))
    out["selection_reason"] = out.apply(selection_reason, axis=1)
    return out


def select_scaled_pairs(frame: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Select N pairs while preserving label balance and dev/test coverage."""
    if n <= 0:
        return frame.head(0).copy()
    ranked = frame.copy()
    if "_tie_breaker" not in ranked.columns:
        ranked["_tie_breaker"] = ranked["pair_id"].map(lambda value: _stable_random(str(value), seed))
    ranked = ranked.sort_values(
        ["evidence_availability_score", "pubmed_available", "opentargets_available", "graph_available", "_tie_breaker"],
        ascending=[False, False, False, False, True],
    )

    label_targets = _targets(list(LABELS), n)
    dev_total = min(int((ranked["split"] == "dev").sum()), max(10 if n >= 50 else 1, round(n * 0.2)))
    split_targets = {"dev": dev_total, "test": n - dev_total}
    selected_ids: list[str] = []

    for label in LABELS:
        label_n = label_targets[label]
        label_dev = min(int(((ranked["expected_label"] == label) & (ranked["split"] == "dev")).sum()), round(label_n * split_targets["dev"] / n))
        label_split_targets = {"dev": label_dev, "test": label_n - label_dev}
        for split, target in label_split_targets.items():
            candidates = ranked[
                (ranked["expected_label"] == label)
                & (ranked["split"] == split)
                & (~ranked["pair_id"].isin(selected_ids))
            ]
            selected_ids.extend(candidates.head(target)["pair_id"].astype(str).tolist())

    for label in LABELS:
        target = label_targets[label]
        current = sum(1 for pair_id in selected_ids if str(ranked.set_index("pair_id").loc[pair_id, "expected_label"]) == label)
        if current >= target:
            continue
        candidates = ranked[(ranked["expected_label"] == label) & (~ranked["pair_id"].isin(selected_ids))]
        selected_ids.extend(candidates.head(target - current)["pair_id"].astype(str).tolist())

    if len(selected_ids) < n:
        candidates = ranked[~ranked["pair_id"].isin(selected_ids)]
        selected_ids.extend(candidates.head(n - len(selected_ids))["pair_id"].astype(str).tolist())

    selected = ranked[ranked["pair_id"].isin(selected_ids[:n])].copy()
    selected["_selection_order"] = selected["pair_id"].map({pair_id: idx for idx, pair_id in enumerate(selected_ids[:n])})
    return selected.sort_values("_selection_order").drop(columns=["_selection_order"])


def make_scaled_selection_outputs(
    repodb_pairs: pd.DataFrame,
    split: pd.DataFrame,
    unified: pd.DataFrame,
    sizes: tuple[int, ...] = (50, 100),
    seed: int = 42,
) -> dict[int, pd.DataFrame]:
    """Return selected dataframes with selected_for_50/100 metadata."""
    frame = build_selection_frame(repodb_pairs, split, unified, seed=seed)
    selections = {size: select_scaled_pairs(frame, size, seed=seed) for size in sizes}
    membership = {size: set(selection["pair_id"].astype(str)) for size, selection in selections.items()}
    outputs = {}
    for size, selection in selections.items():
        out = selection.copy()
        out["selected_for_50"] = out["pair_id"].astype(str).isin(membership.get(50, set()))
        out["selected_for_100"] = out["pair_id"].astype(str).isin(membership.get(100, set()))
        outputs[size] = out[selection_columns()]
    return outputs


def selection_columns() -> list[str]:
    return [
        "pair_id",
        "drug_name",
        "disease_name",
        "expected_label",
        "split",
        "pubmed_available",
        "opentargets_available",
        "graph_available",
        "evidence_availability_score",
        "selected_for_50",
        "selected_for_100",
        "selection_reason",
    ]


def write_scaled_selection_outputs(
    repodb_pairs_path: Path,
    split_path: Path,
    unified_path: Path,
    output_dir: Path,
    seed: int = 42,
) -> dict[int, Path]:
    repodb_pairs = pd.read_csv(repodb_pairs_path)
    split = pd.read_csv(split_path)
    unified = pd.read_csv(unified_path)
    outputs = make_scaled_selection_outputs(repodb_pairs, split, unified, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for size, selection in outputs.items():
        path = output_dir / f"scaled_selected_pairs_{size}.csv"
        selection.to_csv(path, index=False)
        paths[size] = path
    metadata = {
        "seed": seed,
        "sizes": sorted(outputs),
        "selection_rules": [
            "balanced expected_label where possible",
            "roughly 20 percent dev rows for calibration",
            "ranked by PubMed, Open Targets, graph availability and support scores",
            "not conditioned on previous full-agent correctness",
        ],
    }
    (output_dir / "scaled_selection_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return paths


def selection_reason(row: pd.Series) -> str:
    layers = []
    if bool(row.get("pubmed_available", False)):
        layers.append("PubMed")
    if bool(row.get("opentargets_available", False)):
        layers.append("Open Targets")
    if bool(row.get("graph_available", False)):
        layers.append("graph")
    layer_text = ", ".join(layers) if layers else "limited prepared evidence"
    return (
        f"Selected by deterministic evidence-ranked, label-balanced, split-aware sampling; "
        f"available layers: {layer_text}; not selected based on previous full-agent correctness."
    )


def _targets(keys: list[str], total: int) -> dict[str, int]:
    base = total // len(keys)
    remainder = total % len(keys)
    return {key: base + (1 if idx < remainder else 0) for idx, key in enumerate(keys)}


def _stable_random(value: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12)
