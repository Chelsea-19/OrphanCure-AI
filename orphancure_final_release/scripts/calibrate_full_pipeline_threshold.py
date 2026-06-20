"""Generate diagnostics and threshold calibration for full-pipeline outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.full_pipeline_diagnostics import write_diagnostics  # noqa: E402


DEFAULT_RESULTS = PROJECT_ROOT / "eval_results" / "full_pipeline" / "per_pair_results_full.csv"
DEFAULT_UNIFIED = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "eval_results" / "full_pipeline"
DEFAULT_FIGURE = PROJECT_ROOT / "docs" / "figures" / "full_pipeline_threshold_curve.png"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calibrate full-pipeline threshold and write diagnostics.")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--input", dest="input_path", type=Path, help="Alias for --results.")
    parser.add_argument("--split", type=Path, help="Accepted for CLI compatibility; split is read from unified features.")
    parser.add_argument("--unified_features", type=Path, default=DEFAULT_UNIFIED)
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--figure", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results = args.input_path or args.results
    if args.figure is not None:
        figure = args.figure
    elif args.output_dir == DEFAULT_OUTPUT_DIR:
        figure = DEFAULT_FIGURE
    else:
        figure = args.output_dir / "threshold_curve.png"
    summary = write_diagnostics(results, args.unified_features, args.output_dir, figure)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
