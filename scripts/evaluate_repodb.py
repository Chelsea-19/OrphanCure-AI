"""CLI for Phase 1 repoDB evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.repodb import (
    EvaluationConfig,
    download_repodb_csv,
    run_repodb_evaluation,
)


DEFAULT_REPODB_PATH = PROJECT_ROOT / "data" / "benchmarks" / "repodb" / "repodb.csv"
DEFAULT_OUT_DIR = PROJECT_ROOT / "eval_results" / "repodb"
SMOKE_REPODB_PATH = PROJECT_ROOT / "tests" / "fixtures" / "repodb_toy.csv"
SMOKE_PREDICTIONS_PATH = PROJECT_ROOT / "tests" / "fixtures" / "repodb_predictions_toy.csv"


def parse_top_k(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("--top-k must contain at least one integer")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate OrphanCure predictions against repoDB.")
    parser.add_argument("--repodb-path", type=Path, default=DEFAULT_REPODB_PATH)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--top-k", type=parse_top_k, default=(1, 5, 10))
    parser.add_argument("--smoke", action="store_true", help="Run against bundled toy fixtures unless paths are provided.")
    parser.add_argument("--smoke-limit", type=int, default=20)
    parser.add_argument("--download", action="store_true", help="Try to download repoDB from Figshare if missing.")
    parser.add_argument("--download-only", action="store_true", help="Download repoDB and exit without evaluating.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    repodb_path = args.repodb_path
    predictions_path = args.predictions
    if args.smoke:
        if repodb_path == DEFAULT_REPODB_PATH:
            repodb_path = SMOKE_REPODB_PATH
        if predictions_path is None:
            predictions_path = SMOKE_PREDICTIONS_PATH

    if args.download and not repodb_path.exists():
        download_repodb_csv(repodb_path)

    if args.download_only:
        if not repodb_path.exists():
            download_repodb_csv(repodb_path)
        print(f"repoDB CSV available at: {repodb_path}")
        return 0

    if predictions_path is None:
        raise SystemExit("Missing --predictions. Use --smoke for bundled toy predictions.")

    config = EvaluationConfig(
        repodb_path=repodb_path,
        predictions_path=predictions_path,
        out_dir=args.out_dir,
        threshold=args.threshold,
        top_k=args.top_k,
        smoke=args.smoke,
        smoke_limit=args.smoke_limit,
    )
    metrics = run_repodb_evaluation(config)
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
