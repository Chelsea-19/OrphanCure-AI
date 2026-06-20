"""Evaluate prepared benchmark feature tables without invoking OrphanCure agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.unified_benchmark import (  # noqa: E402
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    UNIFIED_MODES,
    classification_metrics,
    evaluate_unified_mode,
    select_threshold,
    write_unified_outputs,
)
from app.evaluation.full_pipeline_eval import (  # noqa: E402
    FULL_PIPELINE_MODES,
    full_pipeline_summary_table,
    summarize_full_pipeline_results,
)

DEFAULT_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "opentargets_pair_features.csv"
DEFAULT_GRAPH_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "graph" / "graph_pair_features.csv"
DEFAULT_UNIFIED_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"
DEFAULT_PUBMED_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "pubmed_pair_features.csv"
DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_SPLIT = PROJECT_ROOT / "data" / "benchmark" / "repodb_split.csv"
DEFAULT_OUT_DIR = PROJECT_ROOT / "eval_results" / "opentargets"
DEFAULT_GRAPH_OUT_DIR = PROJECT_ROOT / "eval_results" / "graph"
DEFAULT_UNIFIED_OUT_DIR = PROJECT_ROOT / "eval_results" / "unified"
DEFAULT_PUBMED_OUT_DIR = PROJECT_ROOT / "eval_results" / "pubmed"
DEFAULT_FULL_PIPELINE_OUT_DIR = PROJECT_ROOT / "eval_results" / "full_pipeline"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate benchmark feature tables.")
    parser.add_argument("--benchmark", choices=["opentargets", "graph", "pubmed", "unified", "full_pipeline"], required=True)
    parser.add_argument("--mode", choices=["opentargets_only", "graph_only", "pubmed_only", *UNIFIED_MODES, *FULL_PIPELINE_MODES], required=True)
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--input", type=Path, help="Alias for --pairs.")
    parser.add_argument("--graph_features", type=Path, default=DEFAULT_GRAPH_FEATURES)
    parser.add_argument("--pubmed_features", type=Path, default=DEFAULT_PUBMED_FEATURES)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--graph_paths", type=Path)
    parser.add_argument("--full_pipeline_results", type=Path)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--output_dir", type=Path)
    parser.add_argument("--max_pairs", type=int)
    return parser


def coerce_bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.casefold().map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}).fillna(False)


def evaluate_opentargets_only(features_path: Path, pairs_path: Path | None, out_dir: Path) -> dict[str, object]:
    features = pd.read_csv(features_path)
    enriched = features.copy()
    if pairs_path and pairs_path.exists():
        pairs = pd.read_csv(pairs_path)
        keep = [column for column in ("pair_id", "expected_label") if column in pairs.columns]
        if keep:
            enriched = enriched.merge(pairs[keep].drop_duplicates("pair_id"), on="pair_id", how="left")

    drug_resolved = coerce_bool_series(enriched["drug_resolved"])
    disease_resolved = coerce_bool_series(enriched["disease_resolved"])
    has_overlap = coerce_bool_series(enriched["has_target_overlap"])
    has_known = coerce_bool_series(enriched["has_known_drug_evidence"])
    support = pd.to_numeric(enriched["opentargets_support_score"], errors="coerce").fillna(0.0)

    metrics: dict[str, object] = {
        "benchmark": "opentargets",
        "mode": "opentargets_only",
        "n_pairs": int(len(enriched)),
        "drug_resolution_rate": float(drug_resolved.mean()) if len(enriched) else 0.0,
        "disease_resolution_rate": float(disease_resolved.mean()) if len(enriched) else 0.0,
        "target_overlap_rate": float(has_overlap.mean()) if len(enriched) else 0.0,
        "known_drug_recovery_rate": float(has_known.mean()) if len(enriched) else 0.0,
        "mean_opentargets_support_score": float(support.mean()) if len(enriched) else 0.0,
        "status_counts": {str(status): int(count) for status, count in enriched["status"].value_counts().items()},
        "notes": (
            "Open Targets metrics measure external evidence support only. "
            "They are not clinical truth and may overlap with OrphanCure internal evidence sources."
        ),
    }
    if "expected_label" in enriched.columns:
        grouped = {}
        for label, group in enriched.groupby("expected_label", dropna=True):
            grouped[str(label)] = {
                "n_pairs": int(len(group)),
                "mean_opentargets_support_score": float(pd.to_numeric(group["opentargets_support_score"], errors="coerce").fillna(0.0).mean()),
                "target_overlap_rate": float(coerce_bool_series(group["has_target_overlap"]).mean()),
                "known_drug_recovery_rate": float(coerce_bool_series(group["has_known_drug_evidence"]).mean()),
            }
        metrics["by_expected_label"] = grouped

    out_dir.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_dir / "per_pair_features.csv", index=False)
    (out_dir / "summary_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / "summary_table.md").write_text(summary_table(metrics), encoding="utf-8")
    return metrics


def evaluate_graph_only(
    features_path: Path,
    pairs_path: Path | None,
    out_dir: Path,
    max_pairs: int | None = None,
    paths_path: Path | None = None,
) -> dict[str, object]:
    features = pd.read_csv(features_path)
    if max_pairs:
        features = features.head(max_pairs).copy()
    enriched = features.copy()
    if pairs_path and pairs_path.exists():
        pairs = pd.read_csv(pairs_path)
        keep = [column for column in ("pair_id", "expected_label") if column in pairs.columns]
        if keep:
            enriched = enriched.merge(pairs[keep].drop_duplicates("pair_id"), on="pair_id", how="left")

    drug_mapped = coerce_bool_series(enriched["drug_mapped"])
    disease_mapped = coerce_bool_series(enriched["disease_mapped"])
    both_mapped = drug_mapped & disease_mapped
    has_path = coerce_bool_series(enriched["has_path"])
    shortest = pd.to_numeric(enriched["shortest_path_length"], errors="coerce").fillna(0)
    support = pd.to_numeric(enriched["graph_connectivity_score"], errors="coerce").fillna(0.0)
    nonzero_shortest = shortest[shortest > 0]
    metrics: dict[str, object] = {
        "benchmark": "graph",
        "mode": "graph_only",
        "n_pairs": int(len(enriched)),
        "drug_mapping_rate": float(drug_mapped.mean()) if len(enriched) else 0.0,
        "disease_mapping_rate": float(disease_mapped.mean()) if len(enriched) else 0.0,
        "both_mapped_rate": float(both_mapped.mean()) if len(enriched) else 0.0,
        "path_recovery_rate": float(has_path.mean()) if len(enriched) else 0.0,
        "mean_shortest_path_length": float(nonzero_shortest.mean()) if len(nonzero_shortest) else 0.0,
        "mean_graph_connectivity_score": float(support.mean()) if len(enriched) else 0.0,
        "status_counts": {str(status): int(count) for status, count in enriched["status"].value_counts().items()},
        "notes": "Graph connectivity is mechanism support only and is not proof of drug efficacy.",
    }
    if "expected_label" in enriched.columns:
        grouped = {}
        for label, group in enriched.groupby("expected_label", dropna=True):
            group_support = pd.to_numeric(group["graph_connectivity_score"], errors="coerce").fillna(0.0)
            grouped[str(label)] = {
                "n_pairs": int(len(group)),
                "mean_graph_connectivity_score": float(group_support.mean()),
                "path_recovery_rate": float(coerce_bool_series(group["has_path"]).mean()),
                "both_mapped_rate": float((coerce_bool_series(group["drug_mapped"]) & coerce_bool_series(group["disease_mapped"])).mean()),
            }
        metrics["by_expected_label"] = grouped

    out_dir.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_dir / "per_pair_features.csv", index=False)
    (out_dir / "summary_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / "summary_table.md").write_text(summary_table(metrics), encoding="utf-8")
    write_case_paths(enriched, paths_path or features_path.parent / "graph_pair_paths.csv", out_dir / "case_paths")
    return metrics


def evaluate_pubmed_only(
    features_path: Path,
    pairs_path: Path | None,
    split_path: Path | None,
    out_dir: Path,
    max_pairs: int | None = None,
) -> dict[str, object]:
    features = pd.read_csv(features_path)
    if max_pairs:
        features = features.head(max_pairs).copy()
    enriched = features.copy()
    if pairs_path and pairs_path.exists():
        pairs = pd.read_csv(pairs_path)
        keep = [column for column in ("pair_id", "expected_label") if column in pairs.columns]
        if keep:
            enriched = enriched.drop(columns=[column for column in ("expected_label",) if column in enriched.columns], errors="ignore")
            enriched = enriched.merge(pairs[keep].drop_duplicates("pair_id"), on="pair_id", how="left")
    if split_path and split_path.exists():
        split = pd.read_csv(split_path)
        if {"pair_id", "split"}.issubset(split.columns):
            enriched = enriched.merge(split[["pair_id", "split"]].drop_duplicates("pair_id"), on="pair_id", how="left")
    if "split" not in enriched.columns:
        enriched["split"] = "unspecified"

    scores = pd.to_numeric(enriched["pubmed_evidence_score"], errors="coerce").fillna(0.0)
    available = pd.to_numeric(enriched["n_unique_pmids"], errors="coerce").fillna(0) > 0
    results = enriched[["pair_id", "drug_name", "disease_name", "expected_label", "split"]].copy()
    results["mode"] = "pubmed_only"
    results["confidence_score"] = scores
    results["evaluation_status"] = available.map({True: "evaluated", False: "skipped_no_pubmed_evidence"})
    threshold, threshold_source = select_threshold(results, "pubmed_only")
    evaluated_mask = results["evaluation_status"] == "evaluated"
    results["predicted_label"] = "skipped"
    results.loc[evaluated_mask, "predicted_label"] = results.loc[evaluated_mask, "confidence_score"].map(
        lambda value: POSITIVE_LABEL if float(value) >= threshold else NEGATIVE_LABEL
    )
    results["threshold"] = threshold
    results["threshold_source"] = threshold_source
    results["notes"] = "confidence_score = pubmed_evidence_score; co-mentions are not evidence of efficacy."

    metric_rows = results[evaluated_mask & results["expected_label"].isin([POSITIVE_LABEL, NEGATIVE_LABEL])]
    metrics = classification_metrics(
        (metric_rows["expected_label"] == POSITIVE_LABEL).astype(int).tolist(),
        (metric_rows["predicted_label"] == POSITIVE_LABEL).astype(int).tolist(),
        pd.to_numeric(metric_rows["confidence_score"], errors="coerce").tolist(),
    )
    grouped = {}
    for label, group in enriched.groupby("expected_label", dropna=True):
        grouped[str(label)] = {
            "n_pairs": int(len(group)),
            "mean_n_unique_pmids": float(pd.to_numeric(group["n_unique_pmids"], errors="coerce").fillna(0).mean()),
            "mean_pubmed_evidence_score": float(pd.to_numeric(group["pubmed_evidence_score"], errors="coerce").fillna(0).mean()),
        }
    metrics.update(
        {
            "benchmark": "pubmed",
            "mode": "pubmed_only",
            "status": "completed",
            "threshold": threshold,
            "threshold_source": threshold_source,
            "n_evaluated_pairs": int(len(metric_rows)),
            "n_skipped_pairs": int(len(results) - len(metric_rows)),
            "evidence_availability_rate": float(available.mean()) if len(available) else 0.0,
            "mean_n_unique_pmids_by_expected_label": {
                label: values["mean_n_unique_pmids"] for label, values in grouped.items()
            },
            "mean_pubmed_evidence_score_by_expected_label": {
                label: values["mean_pubmed_evidence_score"] for label, values in grouped.items()
            },
            "by_expected_label": grouped,
            "notes": (
                "PubMed-only is a transparent co-mention retrieval baseline. "
                "It does not classify evidence polarity and is not clinical validation."
            ),
        }
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_dir / "per_pair_results.csv", index=False)
    enriched.to_csv(out_dir / "per_pair_features.csv", index=False)
    (out_dir / "summary_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / "summary_table.md").write_text(summary_table(metrics), encoding="utf-8")
    return metrics


def write_case_paths(features: pd.DataFrame, paths_path: Path, output_dir: Path, max_cases: int = 5) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not paths_path.exists():
        return
    paths = pd.read_csv(paths_path)
    mapped = features[coerce_bool_series(features["has_path"])].head(max_cases)
    for _, row in mapped.iterrows():
        pair_id = str(row["pair_id"])
        case_paths = paths[paths["pair_id"] == pair_id].to_dict("records")
        (output_dir / f"{pair_id}.json").write_text(json.dumps(case_paths, indent=2), encoding="utf-8")


def summary_table(metrics: dict[str, object]) -> str:
    rows = [(key, value) for key, value in metrics.items() if key not in {"benchmark", "mode", "status_counts", "notes", "by_expected_label"} and not isinstance(value, dict)]
    lines = ["| Metric | Value |", "|---|---|"]
    for key, value in rows:
        lines.append(f"| {key} | {value} |")
    for status, count in dict(metrics.get("status_counts", {})).items():
        lines.append(f"| status:{status} | {count} |")
    return "\n".join(lines) + "\n"


def evaluate_full_pipeline_results(results_path: Path, out_dir: Path, mode: str) -> dict[str, object]:
    if not results_path.exists():
        raise FileNotFoundError(f"Full-pipeline results file not found: {results_path}")
    results = pd.read_csv(results_path)
    metrics = summarize_full_pipeline_results(results, mode)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"summary_metrics_{mode}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / f"summary_table_{mode}.md").write_text(full_pipeline_summary_table(metrics), encoding="utf-8")
    return metrics


def main() -> int:
    args = build_parser().parse_args()
    if args.benchmark == "opentargets" and args.mode == "opentargets_only":
        metrics = evaluate_opentargets_only(args.features, args.input or args.pairs, args.output_dir or args.out_dir)
        print(json.dumps(metrics, indent=2))
        return 0
    if args.benchmark == "graph" and args.mode == "graph_only":
        metrics = evaluate_graph_only(
            args.graph_features,
            args.input or args.pairs,
            args.output_dir or DEFAULT_GRAPH_OUT_DIR,
            max_pairs=args.max_pairs,
            paths_path=args.graph_paths,
        )
        print(json.dumps(metrics, indent=2))
        return 0
    if args.benchmark == "pubmed" and args.mode == "pubmed_only":
        metrics = evaluate_pubmed_only(
            args.pubmed_features,
            args.input or args.pairs,
            args.split,
            args.output_dir or DEFAULT_PUBMED_OUT_DIR,
            max_pairs=args.max_pairs,
        )
        print(json.dumps(metrics, indent=2))
        return 0
    if args.benchmark == "unified" and args.mode in UNIFIED_MODES:
        unified = pd.read_csv(args.input or DEFAULT_UNIFIED_FEATURES)
        results, metrics = evaluate_unified_mode(unified, args.mode)
        summary = write_unified_outputs(unified, results, metrics, args.output_dir or DEFAULT_UNIFIED_OUT_DIR)
        print(json.dumps(summary["modes"][args.mode], indent=2))
        return 0
    if args.benchmark == "full_pipeline" and args.mode in FULL_PIPELINE_MODES:
        out_dir = args.output_dir or DEFAULT_FULL_PIPELINE_OUT_DIR
        results_path = args.full_pipeline_results or out_dir / f"per_pair_results_{args.mode}.csv"
        metrics = evaluate_full_pipeline_results(results_path, out_dir, args.mode)
        print(json.dumps(metrics, indent=2))
        return 0
    raise SystemExit("Unsupported benchmark/mode combination.")


if __name__ == "__main__":
    raise SystemExit(main())
