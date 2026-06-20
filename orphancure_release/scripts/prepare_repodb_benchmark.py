"""Prepare normalized repoDB benchmark pairs and splits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.repodb_benchmark import (  # noqa: E402
    PrepareRepoDBConfig,
    download_repodb_to_temp,
    prepare_repodb_benchmark,
)


DEFAULT_INPUT = PROJECT_ROOT / "data" / "external" / "repodb.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_SPLIT = PROJECT_ROOT / "data" / "benchmark" / "repodb_split.csv"
DEFAULT_METADATA = PROJECT_ROOT / "data" / "benchmark" / "repodb_metadata.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize repoDB into OrphanCure benchmark files.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--include_positive", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include_negative", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max_pairs", type=int)
    parser.add_argument("--balanced", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min_name_length", type=int, default=2)
    parser.add_argument("--exclude_ambiguous", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--download", action="store_true", help="Try Figshare download before local fallback.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = args.input
    source = str(input_path)

    if args.download:
        try:
            input_path, source = download_repodb_to_temp()
            print(f"Downloaded repoDB CSV from {source}")
        except Exception as exc:
            print(f"Automatic download failed: {exc}")
            print(f"Falling back to local input: {args.input}")
            input_path = args.input
            source = str(args.input)

    config = PrepareRepoDBConfig(
        input_path=input_path,
        output_path=args.output,
        split_path=args.split,
        metadata_path=args.metadata,
        include_positive=args.include_positive,
        include_negative=args.include_negative,
        max_pairs=args.max_pairs,
        balanced=args.balanced,
        seed=args.seed,
        min_name_length=args.min_name_length,
        exclude_ambiguous=args.exclude_ambiguous,
        source_path_or_url=source,
    )
    pairs, split, metadata = prepare_repodb_benchmark(config)
    print(f"Wrote pairs: {args.output} ({len(pairs)} rows)")
    print(f"Wrote split: {args.split} ({len(split)} rows)")
    print(f"Wrote metadata: {args.metadata}")
    print(
        "Labels: "
        f"positive={metadata['number_of_positive_pairs']}, "
        f"negative_or_failed={metadata['number_of_negative_or_failed_pairs']}, "
        f"TODO_REVIEW={metadata['number_of_todo_review_pairs']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

