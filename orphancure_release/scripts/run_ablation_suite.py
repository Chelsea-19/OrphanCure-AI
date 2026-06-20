"""Run transparent unified benchmark ablations."""

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
    IMPLEMENTED_UNIFIED_MODES,
    OPTIONAL_TODO_MODES,
    baseline_row,
    evaluate_unified_mode,
    evidence_coverage_metrics,
    summary_table,
    write_figures,
    write_unified_outputs,
)
from app.evaluation.full_pipeline_eval import (  # noqa: E402
    FULL_PIPELINE_MODES,
    summarize_full_pipeline_results,
)


DEFAULT_INPUT = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "eval_results" / "unified"
DEFAULT_FULL_PIPELINE_DIR = PROJECT_ROOT / "eval_results" / "full_pipeline"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run unified baseline and ablation comparisons.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--full_pipeline_dir", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    unified = pd.read_csv(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_metrics = []
    has_pubmed = "pubmed_available" in unified.columns and unified["pubmed_available"].astype(str).str.casefold().isin(["true", "1", "yes"]).any()
    modes_to_run = [
        mode
        for mode in IMPLEMENTED_UNIFIED_MODES
        if has_pubmed or mode not in {"pubmed_only", "combined_structured_literature"}
    ]
    full_pipeline_metrics = []
    completed_full_modes = []
    todo_modes = list(OPTIONAL_TODO_MODES)
    if not has_pubmed:
        todo_modes = ["pubmed_only", "combined_structured_literature", *todo_modes]
    for mode in modes_to_run:
        mode_results, mode_metrics = evaluate_unified_mode(unified, mode)
        write_unified_outputs(unified, mode_results, mode_metrics, args.output_dir)
        all_metrics.append(mode_metrics)

    full_pipeline_dir = args.full_pipeline_dir or args.output_dir.parent / "full_pipeline"
    for mode in FULL_PIPELINE_MODES:
        result_path = full_pipeline_dir / f"per_pair_results_{mode}.csv"
        if not result_path.exists():
            if mode not in todo_modes:
                todo_modes.append(mode)
            continue
        todo_modes = [todo_mode for todo_mode in todo_modes if todo_mode != mode]
        results = pd.read_csv(result_path)
        metrics = summarize_full_pipeline_results(results, mode)
        full_pipeline_metrics.append(metrics)
        completed_full_modes.append(mode)

    summary_path = args.output_dir / "summary_metrics.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {"benchmark": "unified", "modes": {}}
    for mode in todo_modes:
        summary.setdefault("modes", {})[mode] = {
            "mode": mode,
            "status": "TODO_NOT_RUN",
            "n_evaluated_pairs": 0,
            "n_skipped_pairs": int(len(unified)),
            "notes": "Full-pipeline ablation output is not available; no results are fabricated.",
        }
    for metrics in full_pipeline_metrics:
        summary.setdefault("modes", {})[metrics["mode"]] = metrics

    comparison_path = args.output_dir / "baseline_comparison.csv"
    comparison = pd.read_csv(comparison_path) if comparison_path.exists() else pd.DataFrame()
    todo_rows = [baseline_row(summary["modes"][mode]) for mode in todo_modes]
    if not comparison.empty and "mode" in comparison.columns:
        comparison = comparison[
            comparison["mode"].isin(
                (*IMPLEMENTED_UNIFIED_MODES, *OPTIONAL_TODO_MODES, *FULL_PIPELINE_MODES, "pubmed_only", "combined_structured_literature")
            )
        ]
        comparison = comparison[~comparison["mode"].isin([*todo_modes, *completed_full_modes])]
    comparison_records = comparison.to_dict("records") if not comparison.empty else []
    full_rows = [baseline_row(metrics) for metrics in full_pipeline_metrics]
    comparison = pd.DataFrame(comparison_records + full_rows + todo_rows)
    comparison.to_csv(comparison_path, index=False)
    comparison.to_csv(args.output_dir / "ablation_results.csv", index=False)

    summary["coverage_metrics"] = evidence_coverage_metrics(unified)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.output_dir / "summary_table.md").write_text(summary_table(summary, comparison), encoding="utf-8")
    write_figures(unified, comparison)

    write_final_project_summary(args.output_dir, summary, comparison)
    print(json.dumps({"implemented_modes": [m["mode"] for m in all_metrics], "full_pipeline_modes": completed_full_modes, "todo_modes": todo_modes}, indent=2))
    return 0


def write_final_project_summary(output_dir: Path, summary: dict, comparison: pd.DataFrame) -> None:
    coverage = summary.get("coverage_metrics", {})
    lines = ["# OrphanCure Final Project Summary", "", "## Evidence Coverage", "", "| Metric | Value |", "|---|---:|"]
    for key, value in coverage.items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Baseline And Ablation Status", "", "| Mode | Status | Accuracy | F1 | ROC-AUC | Evaluated | Skipped |", "|---|---|---:|---:|---:|---:|---:|"])
    for _, row in comparison.iterrows():
        lines.append(
            f"| {row.get('mode', '')} | {row.get('status', '')} | {row.get('accuracy', '')} | {row.get('f1', '')} | {row.get('roc_auc', '')} | {row.get('n_evaluated_pairs', '')} | {row.get('n_skipped_pairs', '')} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- repoDB labels are proxy labels, not clinical truth.",
            "- PubMed co-mentions are not evidence of efficacy.",
            "- Open Targets and graph support are mechanism/evidence features, not clinical validation.",
            "- TODO_NOT_RUN rows are intentionally not fabricated.",
        ]
    )
    (output_dir / "final_project_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
