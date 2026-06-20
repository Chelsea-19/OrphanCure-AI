"""Unified repoDB/Open Targets/graph/PubMed benchmark utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


UNIFIED_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "expected_label",
    "split",
    "opentargets_available",
    "drug_resolved_ot",
    "disease_resolved_ot",
    "n_disease_targets",
    "n_drug_targets",
    "n_overlapping_targets",
    "has_target_overlap",
    "opentargets_support_score",
    "graph_available",
    "drug_mapped_graph",
    "disease_mapped_graph",
    "has_graph_path",
    "shortest_path_length",
    "n_paths_len_2",
    "n_paths_len_3",
    "n_paths_len_4",
    "graph_connectivity_score",
    "pubmed_available",
    "n_unique_pmids",
    "n_pmids_direct",
    "n_pmids_title_abstract",
    "n_pmids_clinical",
    "n_pmids_negative",
    "n_pmids_mechanism",
    "has_direct_evidence",
    "has_clinical_evidence",
    "has_negative_signal",
    "has_mechanism_signal",
    "abstract_available_rate",
    "pubmed_evidence_score",
    "unified_status",
    "notes",
)

IMPLEMENTED_UNIFIED_MODES = (
    "opentargets_only",
    "graph_only",
    "pubmed_only",
    "ot_plus_graph",
    "heuristic_combined",
    "combined_structured_literature",
)
UNIFIED_MODES = IMPLEMENTED_UNIFIED_MODES + ("full_placeholder",)
OPTIONAL_TODO_MODES = (
    "no_verifier",
    "no_target_expansion",
    "no_graph_features",
    "full",
)

POSITIVE_LABEL = "positive"
NEGATIVE_LABEL = "negative_or_failed"
FIXED_THRESHOLDS = {
    "opentargets_only": 0.25,
    "graph_only": 0.25,
    "pubmed_only": 0.35,
    "ot_plus_graph": 0.25,
    "heuristic_combined": 0.35,
    "combined_structured_literature": 0.35,
}
MIN_DEV_ROWS_FOR_TUNING = 10


def coerce_bool_series(series: pd.Series) -> pd.Series:
    mapped = (
        series.astype(str)
        .str.strip()
        .str.casefold()
        .map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
    )
    return mapped.map(lambda value: bool(value) if pd.notna(value) else False)


def numeric_series(df: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in df.columns:
        return pd.Series([default] * len(df), index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").fillna(default)


def normalize_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    minimum = float(numeric.min(skipna=True))
    maximum = float(numeric.max(skipna=True))
    if maximum == minimum:
        fill_value = 1.0 if maximum > 0 else 0.0
        return pd.Series([fill_value if pd.notna(value) else 0.0 for value in numeric], index=series.index)
    return ((numeric - minimum) / (maximum - minimum)).fillna(0.0).clip(0.0, 1.0)


def build_unified_benchmark_table(
    repodb_pairs: pd.DataFrame,
    opentargets_features: pd.DataFrame,
    graph_features: pd.DataFrame,
    split: pd.DataFrame | None = None,
    pubmed_features: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Left-join evidence features onto every repoDB pair."""
    required_pairs = {"pair_id", "drug_name", "disease_name", "expected_label"}
    missing_pairs = required_pairs - set(repodb_pairs.columns)
    if missing_pairs:
        raise ValueError(f"repoDB pairs are missing required columns: {sorted(missing_pairs)}")

    base_columns = ["pair_id", "drug_name", "disease_name", "expected_label"]
    base = repodb_pairs[base_columns].copy()
    if split is not None and {"pair_id", "split"}.issubset(split.columns):
        base = base.merge(split[["pair_id", "split"]].drop_duplicates("pair_id"), on="pair_id", how="left")
    elif "split" in repodb_pairs.columns:
        base["split"] = repodb_pairs["split"]
    else:
        base["split"] = "unspecified"

    ot = _prepare_opentargets_for_merge(opentargets_features)
    graph = _prepare_graph_for_merge(graph_features)
    pubmed = _prepare_pubmed_for_merge(pubmed_features if pubmed_features is not None else pd.DataFrame())
    unified = base.merge(ot, on="pair_id", how="left").merge(graph, on="pair_id", how="left").merge(pubmed, on="pair_id", how="left")

    unified["opentargets_available"] = unified["_ot_present"].map(lambda value: bool(value) if pd.notna(value) else False)
    unified["graph_available"] = unified["_graph_present"].map(lambda value: bool(value) if pd.notna(value) else False)
    unified["pubmed_available"] = unified["_pubmed_present"].map(lambda value: bool(value) if pd.notna(value) else False)
    for column in ("drug_resolved_ot", "disease_resolved_ot", "has_target_overlap"):
        unified[column] = coerce_bool_series(unified[column]).where(unified["opentargets_available"], False)
    for column in ("drug_mapped_graph", "disease_mapped_graph", "has_graph_path"):
        unified[column] = coerce_bool_series(unified[column]).where(unified["graph_available"], False)
    for column in ("has_direct_evidence", "has_clinical_evidence", "has_negative_signal", "has_mechanism_signal"):
        unified[column] = coerce_bool_series(unified[column]).where(unified["pubmed_available"], False)

    for column in (
        "n_disease_targets",
        "n_drug_targets",
        "n_overlapping_targets",
        "opentargets_support_score",
        "shortest_path_length",
        "n_paths_len_2",
        "n_paths_len_3",
        "n_paths_len_4",
        "graph_connectivity_score",
        "n_unique_pmids",
        "n_pmids_direct",
        "n_pmids_title_abstract",
        "n_pmids_clinical",
        "n_pmids_negative",
        "n_pmids_mechanism",
        "abstract_available_rate",
        "pubmed_evidence_score",
    ):
        unified[column] = pd.to_numeric(unified[column], errors="coerce")

    unified["unified_status"] = unified.apply(_unified_status, axis=1)
    unified["notes"] = unified.apply(_unified_notes, axis=1)
    return unified[list(UNIFIED_COLUMNS)]


def _prepare_opentargets_for_merge(features: pd.DataFrame) -> pd.DataFrame:
    ot_columns = [
        "pair_id",
        "drug_resolved_ot",
        "disease_resolved_ot",
        "n_disease_targets",
        "n_drug_targets",
        "n_overlapping_targets",
        "has_target_overlap",
        "opentargets_support_score",
        "_ot_present",
    ]
    if features.empty:
        return pd.DataFrame(columns=ot_columns)
    required = {"pair_id"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"Open Targets features are missing required columns: {sorted(missing)}")
    rename = {
        "drug_resolved": "drug_resolved_ot",
        "disease_resolved": "disease_resolved_ot",
    }
    keep = [
        "pair_id",
        "drug_resolved",
        "disease_resolved",
        "n_disease_targets",
        "n_drug_targets",
        "n_overlapping_targets",
        "has_target_overlap",
        "opentargets_support_score",
    ]
    available = [column for column in keep if column in features.columns]
    ot = features[available].drop_duplicates("pair_id").rename(columns=rename)
    for column in ot_columns:
        if column not in ot.columns and column != "_ot_present":
            ot[column] = pd.NA
    ot["_ot_present"] = True
    return ot[ot_columns]


def _prepare_graph_for_merge(features: pd.DataFrame) -> pd.DataFrame:
    graph_columns = [
        "pair_id",
        "drug_mapped_graph",
        "disease_mapped_graph",
        "has_graph_path",
        "shortest_path_length",
        "n_paths_len_2",
        "n_paths_len_3",
        "n_paths_len_4",
        "graph_connectivity_score",
        "_graph_present",
    ]
    if features.empty:
        return pd.DataFrame(columns=graph_columns)
    required = {"pair_id"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"graph features are missing required columns: {sorted(missing)}")
    rename = {
        "drug_mapped": "drug_mapped_graph",
        "disease_mapped": "disease_mapped_graph",
        "has_path": "has_graph_path",
    }
    keep = [
        "pair_id",
        "drug_mapped",
        "disease_mapped",
        "has_path",
        "shortest_path_length",
        "n_paths_len_2",
        "n_paths_len_3",
        "n_paths_len_4",
        "graph_connectivity_score",
    ]
    available = [column for column in keep if column in features.columns]
    graph = features[available].drop_duplicates("pair_id").rename(columns=rename)
    for column in graph_columns:
        if column not in graph.columns and column != "_graph_present":
            graph[column] = pd.NA
    graph["_graph_present"] = True
    return graph[graph_columns]


def _prepare_pubmed_for_merge(features: pd.DataFrame) -> pd.DataFrame:
    pubmed_columns = [
        "pair_id",
        "n_unique_pmids",
        "n_pmids_direct",
        "n_pmids_title_abstract",
        "n_pmids_clinical",
        "n_pmids_negative",
        "n_pmids_mechanism",
        "has_direct_evidence",
        "has_clinical_evidence",
        "has_negative_signal",
        "has_mechanism_signal",
        "abstract_available_rate",
        "pubmed_evidence_score",
        "_pubmed_present",
    ]
    if features.empty:
        return pd.DataFrame(columns=pubmed_columns)
    required = {"pair_id"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"PubMed features are missing required columns: {sorted(missing)}")
    keep = [
        "pair_id",
        "n_unique_pmids",
        "n_pmids_direct",
        "n_pmids_title_abstract",
        "n_pmids_clinical",
        "n_pmids_negative",
        "n_pmids_mechanism",
        "has_direct_evidence",
        "has_clinical_evidence",
        "has_negative_signal",
        "has_mechanism_signal",
        "abstract_available_rate",
        "pubmed_evidence_score",
    ]
    available = [column for column in keep if column in features.columns]
    pubmed = features[available].drop_duplicates("pair_id")
    for column in pubmed_columns:
        if column not in pubmed.columns and column != "_pubmed_present":
            pubmed[column] = pd.NA
    pubmed["_pubmed_present"] = True
    return pubmed[pubmed_columns]


def _unified_status(row: pd.Series) -> str:
    available = [
        bool(row["opentargets_available"]),
        bool(row["graph_available"]),
        bool(row["pubmed_available"]),
    ]
    if all(available):
        return "all_available"
    if bool(row["opentargets_available"]) and bool(row["graph_available"]):
        return "ot_graph_available"
    if bool(row["opentargets_available"]) and bool(row["pubmed_available"]):
        return "ot_pubmed_available"
    if bool(row["graph_available"]) and bool(row["pubmed_available"]):
        return "graph_pubmed_available"
    if bool(row["opentargets_available"]):
        return "opentargets_only"
    if bool(row["graph_available"]):
        return "graph_only"
    if bool(row["pubmed_available"]):
        return "pubmed_only"
    return "missing_evidence"


def _unified_notes(row: pd.Series) -> str:
    notes = [
        "repoDB label is a proxy approved/failed benchmark label.",
        "Open Targets support and graph connectivity are evidence features, not clinical truth.",
    ]
    if not bool(row["opentargets_available"]):
        notes.append("Open Targets features missing for this pair.")
    if not bool(row["graph_available"]):
        notes.append("Graph features missing for this pair.")
    if not bool(row["pubmed_available"]):
        notes.append("PubMed features missing for this pair.")
    if bool(row["graph_available"]) and not bool(row["disease_mapped_graph"]):
        notes.append("Graph disease mapping missing or failed.")
    return " ".join(notes)


def evidence_coverage_metrics(unified: pd.DataFrame) -> dict[str, float | int]:
    n = len(unified)
    ot_available = coerce_bool_series(unified["opentargets_available"])
    graph_available = coerce_bool_series(unified["graph_available"])
    pubmed_available = coerce_bool_series(unified["pubmed_available"]) if "pubmed_available" in unified.columns else pd.Series([False] * len(unified), index=unified.index)
    return {
        "n_pairs": int(n),
        "opentargets_availability_rate": _rate(ot_available),
        "graph_availability_rate": _rate(graph_available),
        "pubmed_availability_rate": _rate(pubmed_available),
        "both_evidence_layers_available_rate": _rate(ot_available & graph_available),
        "all_three_evidence_layers_available_rate": _rate(ot_available & graph_available & pubmed_available),
        "ot_disease_resolution_rate": _rate(coerce_bool_series(unified["disease_resolved_ot"]), ot_available),
        "graph_disease_mapping_rate": _rate(coerce_bool_series(unified["disease_mapped_graph"]), graph_available),
        "target_overlap_rate": _rate(coerce_bool_series(unified["has_target_overlap"]), ot_available),
        "graph_path_recovery_rate": _rate(coerce_bool_series(unified["has_graph_path"]), graph_available),
        "pubmed_direct_evidence_rate": _rate(coerce_bool_series(unified["has_direct_evidence"]), pubmed_available) if "has_direct_evidence" in unified.columns else 0.0,
        "pubmed_clinical_evidence_rate": _rate(coerce_bool_series(unified["has_clinical_evidence"]), pubmed_available) if "has_clinical_evidence" in unified.columns else 0.0,
    }


def _rate(values: pd.Series, mask: pd.Series | None = None) -> float:
    selected = values[mask] if mask is not None else values
    return float(selected.mean()) if len(selected) else 0.0


def score_unified_mode(unified: pd.DataFrame, mode: str) -> tuple[pd.Series, pd.Series, str]:
    """Return confidence scores, evaluable mask, and transparent scoring notes."""
    ot = numeric_series(unified, "opentargets_support_score")
    graph = numeric_series(unified, "graph_connectivity_score")
    pubmed = numeric_series(unified, "pubmed_evidence_score")
    ot_available = coerce_bool_series(unified["opentargets_available"])
    graph_available = coerce_bool_series(unified["graph_available"])
    pubmed_available = coerce_bool_series(unified["pubmed_available"]) if "pubmed_available" in unified.columns else pd.Series([False] * len(unified), index=unified.index)
    if mode == "opentargets_only":
        return ot.clip(0.0, 1.0), ot_available, "confidence_score = opentargets_support_score"
    if mode == "graph_only":
        return graph.clip(0.0, 1.0), graph_available, "confidence_score = graph_connectivity_score"
    if mode == "pubmed_only":
        return pubmed.clip(0.0, 1.0), pubmed_available, "confidence_score = pubmed_evidence_score"
    if mode == "ot_plus_graph":
        score = (0.6 * normalize_score(ot)) + (0.4 * normalize_score(graph))
        return score.clip(0.0, 1.0), ot_available & graph_available, (
            "confidence_score = 0.6 * minmax(opentargets_support_score) + "
            "0.4 * minmax(graph_connectivity_score)"
        )
    if mode == "heuristic_combined":
        score = (
            0.45 * ot.clip(0.0, 1.0)
            + 0.20 * coerce_bool_series(unified["has_target_overlap"]).astype(float)
            + 0.20 * coerce_bool_series(unified["has_graph_path"]).astype(float)
            + 0.15 * graph.clip(0.0, 1.0)
            - 0.10 * (graph_available & ~coerce_bool_series(unified["disease_mapped_graph"])).astype(float)
        ).clip(0.0, 1.0)
        return score, ot_available | graph_available, (
            "confidence_score = 0.45*OT support + 0.20*target overlap + 0.20*graph path + "
            "0.15*graph connectivity - 0.10 if graph disease mapping is missing"
        )
    if mode == "combined_structured_literature":
        score = (0.5 * normalize_score(pubmed)) + (0.3 * normalize_score(ot)) + (0.2 * normalize_score(graph))
        return score.clip(0.0, 1.0), pubmed_available & ot_available & graph_available, (
            "confidence_score = 0.5 * minmax(pubmed_evidence_score) + "
            "0.3 * minmax(opentargets_support_score) + 0.2 * minmax(graph_connectivity_score)"
        )
    raise ValueError(f"Unsupported unified scoring mode: {mode}")


def select_threshold(results: pd.DataFrame, mode: str) -> tuple[float, str]:
    dev = results[(results["split"] == "dev") & (results["evaluation_status"] == "evaluated")].copy()
    dev = dev[dev["expected_label"].isin([POSITIVE_LABEL, NEGATIVE_LABEL])]
    if len(dev) < MIN_DEV_ROWS_FOR_TUNING or dev["expected_label"].nunique() < 2:
        return FIXED_THRESHOLDS.get(mode, 0.5), "fixed_threshold_insufficient_dev"
    labels = (dev["expected_label"] == POSITIVE_LABEL).astype(int)
    scores = pd.to_numeric(dev["confidence_score"], errors="coerce")
    candidates = sorted(set(float(value) for value in scores.dropna()))
    candidates = sorted(set(candidates + [0.0, 0.5, 1.0]))
    best_threshold = FIXED_THRESHOLDS.get(mode, 0.5)
    best_f1 = -1.0
    for threshold in candidates:
        preds = (scores >= threshold).astype(int)
        metrics = classification_metrics(labels.tolist(), preds.tolist(), scores.tolist())
        f1 = float(metrics["f1"])
        if f1 > best_f1 or (f1 == best_f1 and threshold > best_threshold):
            best_f1 = f1
            best_threshold = threshold
    return float(best_threshold), "dev_split_max_f1"


def evaluate_unified_mode(unified: pd.DataFrame, mode: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    if mode == "full_placeholder":
        results = _placeholder_results(unified, mode)
        metrics = {
            "mode": mode,
            "status": "TODO_NOT_RUN",
            "n_evaluated_pairs": 0,
            "n_skipped_pairs": int(len(unified)),
            "notes": "Full OrphanCure pipeline predictions were not run; no full results are fabricated.",
        }
        return results, metrics

    scores, evaluable, scoring_notes = score_unified_mode(unified, mode)
    results = unified[["pair_id", "drug_name", "disease_name", "expected_label", "split"]].copy()
    results["mode"] = mode
    results["confidence_score"] = scores
    results["evaluation_status"] = evaluable.map({True: "evaluated", False: "skipped_missing_features"})
    results["predicted_label"] = "skipped"
    threshold, threshold_source = select_threshold(results, mode)
    evaluated_mask = results["evaluation_status"] == "evaluated"
    results.loc[evaluated_mask, "predicted_label"] = results.loc[evaluated_mask, "confidence_score"].map(
        lambda value: POSITIVE_LABEL if float(value) >= threshold else NEGATIVE_LABEL
    )
    results["threshold"] = threshold
    results["threshold_source"] = threshold_source
    results["notes"] = scoring_notes

    metric_rows = results[evaluated_mask & results["expected_label"].isin([POSITIVE_LABEL, NEGATIVE_LABEL])].copy()
    y_true = (metric_rows["expected_label"] == POSITIVE_LABEL).astype(int).tolist()
    y_pred = (metric_rows["predicted_label"] == POSITIVE_LABEL).astype(int).tolist()
    y_score = pd.to_numeric(metric_rows["confidence_score"], errors="coerce").tolist()
    metrics = classification_metrics(y_true, y_pred, y_score)
    metrics.update(
        {
            "mode": mode,
            "status": "completed",
            "threshold": threshold,
            "threshold_source": threshold_source,
            "n_evaluated_pairs": int(len(metric_rows)),
            "n_skipped_pairs": int(len(results) - len(metric_rows)),
            "scoring_formula": scoring_notes,
            "notes": "Metrics compare transparent baseline scores against repoDB proxy labels only.",
        }
    )
    return results, metrics


def _placeholder_results(unified: pd.DataFrame, mode: str) -> pd.DataFrame:
    results = unified[["pair_id", "drug_name", "disease_name", "expected_label", "split"]].copy()
    results["mode"] = mode
    results["confidence_score"] = pd.NA
    results["predicted_label"] = "TODO_NOT_RUN"
    results["evaluation_status"] = "TODO_NOT_RUN"
    results["threshold"] = pd.NA
    results["threshold_source"] = "not_applicable"
    results["notes"] = "Full pipeline was not run; placeholder prevents fabricated results."
    return results


def classification_metrics(y_true: list[int], y_pred: list[int], y_score: list[float]) -> dict[str, Any]:
    if not y_true:
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "roc_auc": None,
            "confusion_matrix": {"tn": 0, "fp": 0, "fn": 0, "tp": 0},
        }
    tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == 1 and pred == 1)
    tn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == 0 and pred == 0)
    fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == 0 and pred == 1)
    fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == 1 and pred == 0)
    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": roc_auc(y_true, y_score),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def roc_auc(y_true: list[int], y_score: list[float]) -> float | None:
    pairs = [(truth, float(score)) for truth, score in zip(y_true, y_score) if pd.notna(score)]
    positives = [score for truth, score in pairs if truth == 1]
    negatives = [score for truth, score in pairs if truth == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = len(positives) * len(negatives)
    for pos in positives:
        for neg in negatives:
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return float(wins / total)


def write_unified_outputs(
    unified: pd.DataFrame,
    mode_results: pd.DataFrame,
    mode_metrics: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    coverage = evidence_coverage_metrics(unified)

    per_pair_path = out / "unified_per_pair_results.csv"
    previous_results = _read_csv_or_empty(per_pair_path)
    if not previous_results.empty and "mode" in previous_results.columns:
        previous_results = previous_results[previous_results["mode"].isin(UNIFIED_MODES)]
        previous_results = previous_results[previous_results["mode"] != mode_metrics["mode"]]
    all_results = pd.concat([previous_results, mode_results], ignore_index=True)
    all_results.to_csv(per_pair_path, index=False)

    comparison_path = out / "baseline_comparison.csv"
    row = baseline_row(mode_metrics)
    previous_comparison = _read_csv_or_empty(comparison_path)
    if not previous_comparison.empty and "mode" in previous_comparison.columns:
        previous_comparison = previous_comparison[previous_comparison["mode"].isin((*UNIFIED_MODES, *OPTIONAL_TODO_MODES))]
        previous_comparison = previous_comparison[previous_comparison["mode"] != mode_metrics["mode"]]
    comparison_records = previous_comparison.to_dict("records") if not previous_comparison.empty else []
    comparison = pd.DataFrame(comparison_records + [row])
    comparison.to_csv(comparison_path, index=False)

    summary_path = out / "summary_metrics.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        summary = {"benchmark": "unified", "modes": {}}
    summary["coverage_metrics"] = coverage
    summary.setdefault("modes", {})[mode_metrics["mode"]] = mode_metrics
    summary["limitations"] = [
        "repoDB is a proxy approved/failed label benchmark.",
        "Open Targets support is target evidence support, not clinical truth.",
        "PrimeKG graph connectivity is mechanism support, not proof of efficacy.",
        "Rows with missing evidence are retained and counted as skipped for affected baselines.",
    ]
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "summary_table.md").write_text(summary_table(summary, comparison), encoding="utf-8")
    write_figures(unified, comparison)
    return summary


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def baseline_row(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": metrics.get("mode"),
        "status": metrics.get("status"),
        "accuracy": metrics.get("accuracy"),
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1": metrics.get("f1"),
        "roc_auc": metrics.get("roc_auc"),
        "n_evaluated_pairs": metrics.get("n_evaluated_pairs", 0),
        "n_skipped_pairs": metrics.get("n_skipped_pairs", 0),
        "threshold": metrics.get("threshold"),
        "threshold_source": metrics.get("threshold_source"),
        "notes": metrics.get("notes"),
    }


def summary_table(summary: dict[str, Any], comparison: pd.DataFrame) -> str:
    lines = ["# Unified Evaluation Summary", ""]
    lines.append("## Evidence Coverage")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for key, value in summary.get("coverage_metrics", {}).items():
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("## Baseline Comparison")
    lines.append("")
    lines.append("| Mode | Status | Accuracy | Precision | Recall | F1 | ROC-AUC | Evaluated | Skipped |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for _, row in comparison.sort_values("mode").iterrows():
        lines.append(
            "| {mode} | {status} | {accuracy} | {precision} | {recall} | {f1} | {roc_auc} | {n_evaluated_pairs} | {n_skipped_pairs} |".format(
                **{column: _format_value(row.get(column)) for column in comparison.columns}
            )
        )
    lines.append("")
    lines.append("These baselines compare transparent evidence scores against repoDB proxy labels only.")
    return "\n".join(lines) + "\n"


def _format_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_figures(unified: pd.DataFrame, comparison: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    figures = Path("docs") / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    completed = comparison[comparison["status"] == "completed"].copy()
    if not completed.empty:
        plt.figure(figsize=(8, 4.5))
        x = range(len(completed))
        plt.bar([i - 0.18 for i in x], pd.to_numeric(completed["accuracy"], errors="coerce").fillna(0), width=0.36, label="Accuracy")
        plt.bar([i + 0.18 for i in x], pd.to_numeric(completed["f1"], errors="coerce").fillna(0), width=0.36, label="F1")
        plt.xticks(list(x), completed["mode"], rotation=20, ha="right")
        plt.ylim(0, 1)
        plt.ylabel("Metric")
        plt.title("Unified Baseline Comparison")
        plt.legend()
        plt.tight_layout()
        plt.savefig(figures / "unified_baseline_comparison.png", dpi=160)
        plt.savefig(figures / "unified_with_pubmed_comparison.png", dpi=160)
        plt.close()

    coverage = evidence_coverage_metrics(unified)
    coverage_keys = [
        "opentargets_availability_rate",
        "graph_availability_rate",
        "both_evidence_layers_available_rate",
        "ot_disease_resolution_rate",
        "graph_disease_mapping_rate",
        "target_overlap_rate",
        "graph_path_recovery_rate",
    ]
    plt.figure(figsize=(8, 4.8))
    plt.bar(coverage_keys, [float(coverage[key]) for key in coverage_keys], color="#477998")
    plt.xticks(rotation=30, ha="right")
    plt.ylim(0, 1)
    plt.ylabel("Rate")
    plt.title("Evidence Coverage Summary")
    plt.tight_layout()
    plt.savefig(figures / "evidence_coverage_summary.png", dpi=160)
    plt.close()

    scatter = unified[coerce_bool_series(unified["opentargets_available"]) | coerce_bool_series(unified["graph_available"])].copy()
    if not scatter.empty:
        colors = scatter["expected_label"].map({POSITIVE_LABEL: "#2a9d8f", NEGATIVE_LABEL: "#b44d4d"}).fillna("#666666")
        plt.figure(figsize=(6, 5))
        plt.scatter(
            numeric_series(scatter, "opentargets_support_score"),
            numeric_series(scatter, "graph_connectivity_score"),
            c=colors,
            alpha=0.75,
            edgecolors="none",
        )
        plt.xlabel("Open Targets support score")
        plt.ylabel("Graph connectivity score")
        plt.title("Open Targets vs Graph Scores")
        plt.tight_layout()
        plt.savefig(figures / "ot_vs_graph_score_scatter.png", dpi=160)
        plt.close()

    if {"n_unique_pmids", "pubmed_evidence_score", "expected_label"}.issubset(unified.columns):
        pubmed_rows = unified[coerce_bool_series(unified["pubmed_available"])].copy()
        if not pubmed_rows.empty:
            grouped = pubmed_rows.groupby("expected_label", dropna=True).agg(
                mean_n_unique_pmids=("n_unique_pmids", "mean"),
                mean_pubmed_evidence_score=("pubmed_evidence_score", "mean"),
            )
            plt.figure(figsize=(6, 4))
            plt.bar(grouped.index.astype(str), grouped["mean_n_unique_pmids"].fillna(0), color="#477998")
            plt.ylabel("Mean unique PMIDs")
            plt.title("PubMed Evidence Count By repoDB Label")
            plt.tight_layout()
            plt.savefig(figures / "pubmed_evidence_by_label.png", dpi=160)
            plt.close()

            plt.figure(figsize=(6, 4))
            plt.bar(grouped.index.astype(str), grouped["mean_pubmed_evidence_score"].fillna(0), color="#7b8f3a")
            plt.ylim(0, 1)
            plt.ylabel("Mean PubMed evidence score")
            plt.title("PubMed Baseline Score By repoDB Label")
            plt.tight_layout()
            plt.savefig(figures / "pubmed_baseline_comparison.png", dpi=160)
            plt.close()
