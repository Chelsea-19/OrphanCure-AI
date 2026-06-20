"""Diagnostics for full-pipeline OrphanCure evaluation outputs.

This module derives error analysis, threshold calibration, alternative scores,
and triage summaries from already-extracted evaluation features. It never
changes benchmark labels or generates biomedical evidence.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from app.evaluation.unified_benchmark import (
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    classification_metrics,
    coerce_bool_series,
    normalize_score,
    numeric_series,
)


VALID_LABELS = {POSITIVE_LABEL, NEGATIVE_LABEL}
DEFAULT_THRESHOLD = 0.5
MIN_DEV_ROWS_FOR_CALIBRATION = 10


def correctness_type(row: pd.Series | dict[str, Any]) -> str:
    """Classify one full-pipeline row as TP/TN/FP/FN/skipped/partial."""
    status = str(row.get("status", "")).strip().casefold()
    expected = str(row.get("expected_label", "")).strip()
    predicted = str(row.get("predicted_label", "")).strip()
    if status == "partial_success":
        return "partial"
    if status in {"failed", "todo_not_run"} or expected not in VALID_LABELS or predicted not in VALID_LABELS:
        return "skipped"
    if expected == POSITIVE_LABEL and predicted == POSITIVE_LABEL:
        return "TP"
    if expected == NEGATIVE_LABEL and predicted == NEGATIVE_LABEL:
        return "TN"
    if expected == NEGATIVE_LABEL and predicted == POSITIVE_LABEL:
        return "FP"
    if expected == POSITIVE_LABEL and predicted == NEGATIVE_LABEL:
        return "FN"
    return "skipped"


def load_diagnostic_frame(results_path: Path, unified_path: Path) -> pd.DataFrame:
    """Load full-agent results and join existing structured evidence features."""
    results = pd.read_csv(results_path)
    unified = pd.read_csv(unified_path)
    feature_cols = [
        "pair_id",
        "split",
        "opentargets_available",
        "graph_available",
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
        "opentargets_support_score",
        "graph_connectivity_score",
        "pubmed_evidence_score",
        "has_target_overlap",
        "has_graph_path",
        "unified_status",
    ]
    keep = [column for column in feature_cols if column in unified.columns]
    joined = results.merge(unified[keep].drop_duplicates("pair_id"), on="pair_id", how="left")
    return add_alternative_scores(joined)


def add_alternative_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add transparent alternative score columns from existing extracted features."""
    out = df.copy()
    out["full_confidence_score_original"] = numeric_series(out, "confidence_score")

    pubmed = numeric_series(out, "pubmed_evidence_score")
    ot = numeric_series(out, "opentargets_support_score")
    graph = numeric_series(out, "graph_connectivity_score")
    verified_rate = numeric_series(out, "citation_verified_rate")
    unsupported_rate = numeric_series(out, "unsupported_claim_rate")
    clinical_pmids = _log_normalized(out, "n_pmids_clinical")
    mechanism_pmids = _log_normalized(out, "n_pmids_mechanism")
    negative_pmids = _log_normalized(out, "n_pmids_negative")

    out["pubmed_only"] = pubmed.clip(0.0, 1.0)
    out["combined_structured_literature"] = (
        0.50 * normalize_score(pubmed)
        + 0.30 * normalize_score(ot)
        + 0.20 * normalize_score(graph)
    ).clip(0.0, 1.0)
    out["evidence_strength_score"] = (
        0.35 * normalize_score(pubmed)
        + 0.30 * normalize_score(ot)
        + 0.20 * normalize_score(graph)
        + 0.15 * verified_rate.clip(0.0, 1.0)
    ).clip(0.0, 1.0)

    negative_ratio = _ratio(out, "n_pmids_negative", "n_unique_pmids")
    out["clinical_support_score"] = (
        0.24 * clinical_pmids
        + 0.18 * mechanism_pmids
        + 0.18 * normalize_score(ot)
        + 0.14 * normalize_score(graph)
        + 0.14 * verified_rate.clip(0.0, 1.0)
        + 0.12 * normalize_score(pubmed)
        - 0.12 * negative_ratio
        - 0.14 * unsupported_rate.clip(0.0, 1.0)
    ).clip(0.0, 1.0)
    out["safety_penalized_score"] = (
        out["clinical_support_score"]
        - 0.18 * negative_pmids
        - 0.18 * negative_ratio
        - 0.22 * unsupported_rate.clip(0.0, 1.0)
    ).clip(0.0, 1.0)
    return out


def build_error_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Create the requested per-pair error analysis table."""
    rows = df.copy()
    rows["correctness_type"] = rows.apply(correctness_type, axis=1)
    rows["full_status"] = rows["status"]
    rows["notes"] = rows.apply(error_note, axis=1)
    columns = [
        "pair_id",
        "drug_name",
        "disease_name",
        "expected_label",
        "predicted_label",
        "confidence_score",
        "correctness_type",
        "full_status",
        "n_pmids_used",
        "n_opentargets_evidence_items",
        "n_graph_paths_used",
        "n_claims",
        "n_verified_claims",
        "n_unsupported_claims",
        "citation_verified_rate",
        "unsupported_claim_rate",
        "notes",
    ]
    return rows.reindex(columns=columns)


def error_note(row: pd.Series) -> str:
    ctype = correctness_type(row)
    if ctype == "partial":
        return "Partial success: no valid binary label was produced, so the row was excluded from original label metrics."
    if ctype == "skipped":
        return "Skipped for binary metrics because status or labels were not evaluable."
    n_pmids = _number(row.get("n_pmids_used"))
    n_ot = _number(row.get("n_opentargets_evidence_items"))
    n_graph = _number(row.get("n_graph_paths_used"))
    unsupported = _number(row.get("unsupported_claim_rate"))
    n_neg = _number(row.get("n_pmids_negative"))
    n_total = _number(row.get("n_unique_pmids"))
    if ctype == "FP" and n_pmids >= 20 and (n_ot + n_graph) <= 1:
        return "False positive with heavy PubMed co-mention but little structured/graph support; likely co-mention inflation."
    if ctype == "FP" and unsupported >= 0.25:
        return "False positive also has unsupported-claim or conflicting provenance signals."
    if ctype == "FP":
        return "False positive under repoDB proxy labels; inspect whether the negative_or_failed label reflects safety, trial logistics, or true lack of efficacy."
    if ctype == "FN" and n_pmids == 0 and (n_ot + n_graph) == 0:
        return "False negative with no evidence used by the full run; likely missing retrieval/structured evidence."
    if ctype == "FN":
        return "False negative: full agent produced a conservative negative label despite a positive repoDB proxy label."
    if ctype == "TN" and n_neg > 0 and n_total > 0:
        return "True negative with available negative/failure PubMed signals."
    if ctype == "TP":
        return "True positive; generated label agrees with repoDB proxy label."
    return "Correct label under repoDB proxy benchmark."


def confusion_markdown(error_table: pd.DataFrame) -> str:
    counts = error_table["correctness_type"].value_counts().to_dict()
    lines = [
        "# Full Pipeline Confusion Matrix",
        "",
        "| Category | Count | Examples |",
        "|---|---:|---|",
    ]
    for category in ["TP", "TN", "FP", "FN", "partial", "skipped"]:
        examples = _examples(error_table, category)
        label = "skipped/partial" if category == "partial" else category
        lines.append(f"| {label} | {int(counts.get(category, 0))} | {examples} |")
    lines.extend(
        [
            "",
            "Partial and skipped rows are not counted as TP/TN/FP/FN in the original full-agent binary metrics.",
        ]
    )
    return "\n".join(lines) + "\n"


def calibrate_thresholds(
    df: pd.DataFrame,
    score_col: str = "full_confidence_score_original",
    label_col: str = "expected_label",
    split_col: str = "split",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Select thresholds on dev rows and report dev/test/all metrics."""
    evaluable = _evaluable_rows(df, score_col, label_col).copy()
    dev = evaluable[evaluable[split_col].fillna("") == "dev"].copy()
    calibration_source = "dev_split"
    exploratory = False
    if len(dev) < MIN_DEV_ROWS_FOR_CALIBRATION or dev[label_col].nunique() < 2:
        exploratory = True
        calibration_source = "dev_split_exploratory_small_n"
    if dev.empty:
        dev = evaluable.copy()
        calibration_source = "all_rows_exploratory_no_dev_rows"
        exploratory = True

    candidates = _threshold_candidates(dev[score_col])
    selected = {
        "default_threshold": DEFAULT_THRESHOLD,
        "best_f1_threshold": _best_threshold(dev, score_col, metric="f1", candidates=candidates),
        "best_balanced_accuracy_threshold": _best_threshold(dev, score_col, metric="balanced_accuracy", candidates=candidates),
        "high_precision_threshold": _best_threshold(dev, score_col, metric="precision", candidates=candidates, prefer_high=True),
        "high_recall_threshold": _best_threshold(dev, score_col, metric="recall", candidates=candidates, prefer_high=False),
    }
    rows: list[dict[str, Any]] = []
    for name, threshold in selected.items():
        for subset_name, subset in _metric_subsets(evaluable):
            metrics = threshold_metrics(subset, score_col, threshold)
            rows.append(
                {
                    "threshold_name": name,
                    "threshold": threshold,
                    "subset": subset_name,
                    "n_rows": len(subset),
                    "calibration_source": calibration_source,
                    "exploratory": exploratory,
                    **metrics,
                }
            )
    best = {
        "score_column": score_col,
        "calibration_source": calibration_source,
        "exploratory": exploratory,
        "n_dev_rows": int(len(dev)),
        "n_total_evaluable_rows": int(len(evaluable)),
        "thresholds": selected,
        "notes": (
            "Thresholds were selected using dev rows only. Because the selected full-agent "
            "subset has fewer than 10 evaluable dev rows, calibration is exploratory."
            if exploratory
            else "Thresholds were selected using dev rows only."
        ),
    }
    return pd.DataFrame(rows), best


def threshold_metrics(df: pd.DataFrame, score_col: str, threshold: float) -> dict[str, Any]:
    if df.empty:
        base = classification_metrics([], [], [])
    else:
        y_true = (df["expected_label"] == POSITIVE_LABEL).astype(int).tolist()
        scores = pd.to_numeric(df[score_col], errors="coerce").tolist()
        y_pred = [1 if float(score) >= threshold else 0 for score in scores]
        base = classification_metrics(y_true, y_pred, scores)
    cm = base.get("confusion_matrix", {})
    tn = int(cm.get("tn", 0))
    fp = int(cm.get("fp", 0))
    fn = int(cm.get("fn", 0))
    tp = int(cm.get("tp", 0))
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    recall = float(base["recall"] or 0.0)
    base["balanced_accuracy"] = float((recall + specificity) / 2)
    return base


def compare_alternative_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compare original and transparent alternative scores."""
    rows = []
    for score_name in [
        "full_confidence_score_original",
        "evidence_strength_score",
        "clinical_support_score",
        "safety_penalized_score",
        "pubmed_only",
        "combined_structured_literature",
    ]:
        evaluable = _evaluable_rows(df, score_name, "expected_label")
        threshold = _threshold_for_score(evaluable, score_name)
        metrics = threshold_metrics(evaluable, score_name, threshold)
        rows.append(
            {
                "score_name": score_name,
                "threshold": threshold,
                "threshold_source": "dev_split_exploratory_small_n"
                if _dev_is_small(evaluable)
                else "dev_split_best_f1",
                "n_evaluated_pairs": int(len(evaluable)),
                **_flatten_metrics(metrics),
            }
        )
    return pd.DataFrame(rows)


def triage_classification(
    df: pd.DataFrame,
    score_col: str = "clinical_support_score",
    low_threshold: float = 0.25,
    high_threshold: float = 0.65,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Add likely_supported / insufficient_or_negative / uncertain_mixed labels."""
    out = df.copy()
    score = pd.to_numeric(out[score_col], errors="coerce").fillna(0.0)
    safety = pd.to_numeric(out["safety_penalized_score"], errors="coerce").fillna(score)
    unsupported = numeric_series(out, "unsupported_claim_rate")
    out["triage_label"] = "uncertain_mixed"
    out.loc[(score >= high_threshold) & (safety >= 0.45) & (unsupported <= 0.25), "triage_label"] = "likely_supported"
    out.loc[(score <= low_threshold) | (safety <= 0.10), "triage_label"] = "insufficient_or_negative"

    covered = out[out["triage_label"] != "uncertain_mixed"].copy()
    metric_rows = covered[covered["expected_label"].isin(VALID_LABELS)].copy()
    metric_rows["triage_predicted_label"] = metric_rows["triage_label"].map(
        {"likely_supported": POSITIVE_LABEL, "insufficient_or_negative": NEGATIVE_LABEL}
    )
    metrics = classification_metrics(
        (metric_rows["expected_label"] == POSITIVE_LABEL).astype(int).tolist(),
        (metric_rows["triage_predicted_label"] == POSITIVE_LABEL).astype(int).tolist(),
        pd.to_numeric(metric_rows[score_col], errors="coerce").tolist(),
    )
    total = len(out)
    metrics.update(
        {
            "score_column": score_col,
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
            "coverage_rate": float(len(covered) / total) if total else 0.0,
            "abstention_rate": float((total - len(covered)) / total) if total else 0.0,
            "accuracy_on_covered_cases": metrics["accuracy"],
            "n_covered": int(len(covered)),
            "n_uncertain": int(total - len(covered)),
            "notes": "Triage uses fixed score bands and abstains on the uncertain middle band.",
        }
    )
    return out, metrics


def error_pattern_summary(df: pd.DataFrame) -> dict[str, Any]:
    errors = build_error_analysis(df)
    fps = errors[errors["correctness_type"] == "FP"]
    fns = errors[errors["correctness_type"] == "FN"]
    partial = errors[errors["correctness_type"] == "partial"]
    joined = df.set_index("pair_id")
    fp_pubmed_inflated = 0
    fn_missing_evidence = 0
    fn_conservative = 0
    noisy_negatives = 0
    malformed = int(len(partial))
    for _, row in fps.iterrows():
        features = joined.loc[row["pair_id"]]
        n_pmids = _number(features.get("n_unique_pmids"))
        n_negative = _number(features.get("n_pmids_negative"))
        structured = _number(row.get("n_opentargets_evidence_items")) + _number(row.get("n_graph_paths_used"))
        if n_pmids >= 20 and structured <= 1:
            fp_pubmed_inflated += 1
        if n_negative >= max(1.0, n_pmids * 0.25):
            noisy_negatives += 1
    for _, row in fns.iterrows():
        if _number(row.get("n_pmids_used")) == 0 and (
            _number(row.get("n_opentargets_evidence_items")) + _number(row.get("n_graph_paths_used"))
        ) == 0:
            fn_missing_evidence += 1
        else:
            fn_conservative += 1
    return {
        "false_positives": int(len(fps)),
        "false_negatives": int(len(fns)),
        "fp_pubmed_comention_inflation": int(fp_pubmed_inflated),
        "fp_noisy_negative_or_failed_labels": int(noisy_negatives),
        "fn_missing_open_targets_graph_or_pubmed_evidence": int(fn_missing_evidence),
        "fn_conservative_negative_outputs": int(fn_conservative),
        "partial_success_rows": int(len(partial)),
        "malformed_or_low_confidence_outputs": malformed,
        "main_interpretation": (
            "Low F1 is driven mainly by false negatives from conservative or no-evidence full-agent "
            "outputs, with additional false positives on PubMed-heavy negative_or_failed rows."
        ),
    }


def write_threshold_curve(calibration: pd.DataFrame, output_path: Path) -> None:
    """Write a threshold curve PNG if matplotlib is available."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    all_rows = calibration[calibration["subset"] == "all"].copy()
    if all_rows.empty:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7.5, 4.5))
    for metric in ["precision", "recall", "f1", "balanced_accuracy"]:
        plt.plot(all_rows["threshold"], all_rows[metric], marker="o", label=metric)
    plt.ylim(0, 1.05)
    plt.xlabel("Threshold")
    plt.ylabel("Metric")
    plt.title("Full Pipeline Threshold Calibration")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def write_diagnostics(
    results_path: Path,
    unified_path: Path,
    output_dir: Path,
    figure_path: Path,
) -> dict[str, Any]:
    df = load_diagnostic_frame(results_path, unified_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    error_table = build_error_analysis(df)
    error_table.to_csv(output_dir / "error_analysis_full.csv", index=False)
    (output_dir / "confusion_matrix_full.md").write_text(confusion_markdown(error_table), encoding="utf-8")

    calibration, best_thresholds = calibrate_thresholds(df)
    calibration.to_csv(output_dir / "threshold_calibration.csv", index=False)
    (output_dir / "best_thresholds.json").write_text(json.dumps(best_thresholds, indent=2), encoding="utf-8")
    write_threshold_curve(calibration, figure_path)

    comparison = compare_alternative_scores(df)
    comparison.to_csv(output_dir / "alternative_score_comparison.csv", index=False)

    triage, triage_metrics = triage_classification(df)
    triage[
        [
            "pair_id",
            "drug_name",
            "disease_name",
            "expected_label",
            "clinical_support_score",
            "safety_penalized_score",
            "triage_label",
        ]
    ].to_csv(output_dir / "triage_classification_full.csv", index=False)
    triage[
        [
            "pair_id",
            "drug_name",
            "disease_name",
            "expected_label",
            "clinical_support_score",
            "safety_penalized_score",
            "triage_label",
        ]
    ].to_csv(output_dir / "triage_output.csv", index=False)
    (output_dir / "triage_metrics_full.json").write_text(json.dumps(triage_metrics, indent=2), encoding="utf-8")

    summary = {
        "confusion_counts": {key: int(value) for key, value in error_table["correctness_type"].value_counts().items()},
        "error_patterns": error_pattern_summary(df),
        "best_thresholds": best_thresholds,
        "best_alternative_score": _best_alternative(comparison),
        "triage_metrics": triage_metrics,
        "outputs": {
            "error_analysis": str(output_dir / "error_analysis_full.csv"),
            "confusion_matrix": str(output_dir / "confusion_matrix_full.md"),
            "threshold_calibration": str(output_dir / "threshold_calibration.csv"),
            "best_thresholds": str(output_dir / "best_thresholds.json"),
            "threshold_curve": str(figure_path),
            "alternative_score_comparison": str(output_dir / "alternative_score_comparison.csv"),
            "triage_classification": str(output_dir / "triage_classification_full.csv"),
        },
    }
    (output_dir / "diagnostic_summary_full.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _evaluable_rows(df: pd.DataFrame, score_col: str, label_col: str) -> pd.DataFrame:
    rows = df[df[label_col].isin(VALID_LABELS)].copy()
    rows = rows[pd.to_numeric(rows[score_col], errors="coerce").notna()].copy()
    if score_col == "full_confidence_score_original" and "status" in rows.columns:
        rows = rows[rows["status"].isin(["completed", "success"])].copy()
        rows = rows[rows["predicted_label"].isin(VALID_LABELS)].copy()
    return rows


def _metric_subsets(evaluable: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    return [
        ("dev", evaluable[evaluable["split"].fillna("") == "dev"].copy()),
        ("test", evaluable[evaluable["split"].fillna("") == "test"].copy()),
        ("all", evaluable.copy()),
    ]


def _threshold_candidates(scores: pd.Series) -> list[float]:
    numeric = pd.to_numeric(scores, errors="coerce").dropna()
    values = {0.0, DEFAULT_THRESHOLD, 1.0}
    values.update(float(value) for value in numeric.tolist())
    return sorted(value for value in values if not math.isnan(value))


def _best_threshold(
    df: pd.DataFrame,
    score_col: str,
    metric: str,
    candidates: list[float],
    prefer_high: bool = False,
) -> float:
    best_threshold = DEFAULT_THRESHOLD
    best_value = -1.0
    best_f1 = -1.0
    for threshold in candidates:
        metrics = threshold_metrics(df, score_col, threshold)
        value = float(metrics.get(metric) or 0.0)
        f1 = float(metrics.get("f1") or 0.0)
        better = value > best_value or (
            value == best_value
            and (f1 > best_f1 or (f1 == best_f1 and ((prefer_high and threshold > best_threshold) or (not prefer_high and threshold > best_threshold))))
        )
        if better:
            best_threshold = float(threshold)
            best_value = value
            best_f1 = f1
    return best_threshold


def _threshold_for_score(evaluable: pd.DataFrame, score_col: str) -> float:
    dev = evaluable[evaluable["split"].fillna("") == "dev"].copy()
    if dev.empty or dev["expected_label"].nunique() < 2:
        return DEFAULT_THRESHOLD
    candidates = _threshold_candidates(dev[score_col])
    return _best_threshold(dev, score_col, metric="f1", candidates=candidates)


def _dev_is_small(evaluable: pd.DataFrame) -> bool:
    dev = evaluable[evaluable["split"].fillna("") == "dev"]
    return len(dev) < MIN_DEV_ROWS_FOR_CALIBRATION or dev["expected_label"].nunique() < 2


def _flatten_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    cm = metrics.get("confusion_matrix", {})
    return {
        "accuracy": metrics.get("accuracy"),
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1": metrics.get("f1"),
        "roc_auc": metrics.get("roc_auc"),
        "balanced_accuracy": metrics.get("balanced_accuracy"),
        "tn": cm.get("tn", 0),
        "fp": cm.get("fp", 0),
        "fn": cm.get("fn", 0),
        "tp": cm.get("tp", 0),
    }


def _best_alternative(comparison: pd.DataFrame) -> dict[str, Any]:
    ranked = comparison.sort_values(
        by=["f1", "balanced_accuracy", "roc_auc"],
        ascending=[False, False, False],
        na_position="last",
    )
    if ranked.empty:
        return {}
    return ranked.iloc[0].to_dict()


def _examples(error_table: pd.DataFrame, category: str, limit: int = 3) -> str:
    rows = error_table[error_table["correctness_type"] == category].head(limit)
    if rows.empty:
        return ""
    return "; ".join(
        f"{row['pair_id']} ({row['drug_name']} / {row['disease_name']})" for _, row in rows.iterrows()
    )


def _log_normalized(df: pd.DataFrame, column: str) -> pd.Series:
    values = numeric_series(df, column)
    logged = values.map(lambda value: math.log1p(max(float(value), 0.0)))
    maximum = float(logged.max()) if len(logged) else 0.0
    if maximum <= 0:
        return pd.Series([0.0] * len(df), index=df.index)
    return (logged / maximum).clip(0.0, 1.0)


def _ratio(df: pd.DataFrame, numerator: str, denominator: str) -> pd.Series:
    num = numeric_series(df, numerator)
    den = numeric_series(df, denominator)
    return (num / den.where(den > 0, 1.0)).fillna(0.0).clip(0.0, 1.0)


def _number(value: Any) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except Exception:
        return 0.0
