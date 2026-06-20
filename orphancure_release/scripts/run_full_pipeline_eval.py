"""Run full OrphanCure pipeline evaluation or explicit TODO placeholders."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.full_pipeline_eval import (  # noqa: E402
    FULL_PIPELINE_COLUMNS,
    FULL_PIPELINE_MODES,
    load_benchmark_pairs,
    llm_config_available,
    missing_llm_reason,
    run_full_pipeline_for_pair,
    select_evaluation_subset,
    write_full_pipeline_outputs,
)


DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_UNIFIED = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"
DEFAULT_OUT = PROJECT_ROOT / "eval_results" / "full_pipeline"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate full OrphanCure pipeline modes.")
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--unified_features", type=Path, default=DEFAULT_UNIFIED)
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max_pairs", type=int, default=20)
    parser.add_argument("--mode", choices=FULL_PIPELINE_MODES, default="full")
    parser.add_argument("--use_cached", action="store_true")
    parser.add_argument("--skip_llm_if_missing", action="store_true")
    parser.add_argument("--demo_mode", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    pairs = load_benchmark_pairs(args.pairs)
    unified = pd.read_csv(args.unified_features) if args.unified_features.exists() else pd.DataFrame()
    subset = select_evaluation_subset(pairs, unified, max_pairs=args.max_pairs)

    if not llm_config_available():
        message = {
            "status": "TODO_NOT_RUN",
            "reason": missing_llm_reason(),
            "mode": args.mode,
            "selected_pairs": int(len(subset)),
        }
        if not args.skip_llm_if_missing:
            print(json.dumps(message, indent=2))
            return 2

    rows = []
    for _, row in subset.iterrows():
        try:
            result = run_full_pipeline_for_pair(
                row,
                args.mode,
                args.output_dir,
                use_cached=args.use_cached,
                skip_llm_if_missing=args.skip_llm_if_missing,
                demo_mode=args.demo_mode,
            )
        except Exception as exc:  # pragma: no cover - defensive per-pair isolation
            raw_dir = args.output_dir / "raw_outputs" / args.mode
            report_dir = args.output_dir / "reports" / args.mode
            raw_dir.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)
            pair_id = str(row.get("pair_id"))
            raw_path = raw_dir / f"{pair_id}.json"
            report_path = report_dir / f"{pair_id}.md"
            failure_payload = {
                "status": "failed",
                "mode": args.mode,
                "pair_id": pair_id,
                "drug_name": row.get("drug_name"),
                "disease_name": row.get("disease_name"),
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
                "notes": "Pair-level full-pipeline run failed; execution continued. No outputs were fabricated.",
            }
            raw_path.write_text(json.dumps(failure_payload, indent=2), encoding="utf-8")
            report_path.write_text(
                "\n".join(
                    [
                        f"# Full Pipeline Failure: {pair_id}",
                        "",
                        f"- Drug: {row.get('drug_name')}",
                        f"- Disease: {row.get('disease_name')}",
                        f"- Mode: {args.mode}",
                        "- Status: failed",
                        "",
                        "No biomedical report was generated for this pair.",
                        "",
                        f"Error: {exc}",
                        "",
                        "This failure marker is for debugging only and is not medical advice.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            result = {
                "pair_id": row.get("pair_id"),
                "drug_name": row.get("drug_name"),
                "disease_name": row.get("disease_name"),
                "expected_label": row.get("expected_label"),
                "mode": args.mode,
                "predicted_label": "failed",
                "confidence_score": None,
                "final_assessment": "failed",
                "n_claims": None,
                "n_verified_claims": None,
                "n_unsupported_claims": None,
                "citation_verified_rate": None,
                "unsupported_claim_rate": None,
                "n_pmids_used": None,
                "n_opentargets_evidence_items": None,
                "n_graph_paths_used": None,
                "report_path": str(report_path),
                "raw_output_path": str(raw_path),
                "runtime_seconds": 0.0,
                "status": "failed",
                "error_message": str(exc),
                "notes": "Pair-level full-pipeline run failed; execution continued.",
            }
        rows.append(result)

    results = pd.DataFrame(rows).reindex(columns=FULL_PIPELINE_COLUMNS)
    metrics = write_full_pipeline_outputs(results, args.mode, args.output_dir)
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
