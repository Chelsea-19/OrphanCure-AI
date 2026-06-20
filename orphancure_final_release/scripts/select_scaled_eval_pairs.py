"""Select deterministic 50/100-pair full-agent evaluation subsets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.scaled_selection import write_scaled_selection_outputs  # noqa: E402


DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_SPLIT = PROJECT_ROOT / "data" / "benchmark" / "repodb_split.csv"
DEFAULT_UNIFIED = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "eval_results" / "full_pipeline"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Select scaled full-agent evaluation pairs.")
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--unified_features", type=Path, default=DEFAULT_UNIFIED)
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output_50", type=Path, help="Optional explicit path for the 50-pair selection CSV.")
    parser.add_argument("--output_100", type=Path, help="Optional explicit path for the 100-pair selection CSV.")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    paths = write_scaled_selection_outputs(args.pairs, args.split, args.unified_features, args.output_dir, args.seed)
    explicit_paths = {50: args.output_50, 100: args.output_100}
    for size, explicit_path in explicit_paths.items():
        if explicit_path is None or explicit_path == paths[size]:
            continue
        explicit_path.parent.mkdir(parents=True, exist_ok=True)
        pd.read_csv(paths[size]).to_csv(explicit_path, index=False)
        paths[size] = explicit_path
    summary = {}
    for size, path in paths.items():
        rows = pd.read_csv(path)
        summary[size] = {
            "path": str(path),
            "n_selected": int(len(rows)),
            "label_counts": {str(k): int(v) for k, v in rows["expected_label"].value_counts().items()},
            "split_counts": {str(k): int(v) for k, v in rows["split"].value_counts().items()},
        }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
