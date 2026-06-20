"""Prepare Open Targets enrichment tables for repoDB benchmark pairs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.opentargets_benchmark import (  # noqa: E402
    OpenTargetsClient,
    OpenTargetsConfig,
    enrich_pairs,
    summarize_feature_status,
    write_opentargets_outputs,
)


DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_EVIDENCE = PROJECT_ROOT / "data" / "benchmark" / "opentargets_evidence.csv"
DEFAULT_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "opentargets_pair_features.csv"
DEFAULT_CACHE = PROJECT_ROOT / "data" / "external" / "opentargets_cache"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich repoDB benchmark pairs with Open Targets evidence.")
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--output", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--features_output", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--cache_dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--max_pairs", type=int, default=5)
    parser.add_argument("--use_cached", action="store_true")
    parser.add_argument("--skip_api_if_missing", action="store_true")
    parser.add_argument("--api_url", default="https://api.platform.opentargets.org/api/v4/graphql")
    parser.add_argument("--timeout", type=int, default=30)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    pairs = pd.read_csv(args.pairs)
    config = OpenTargetsConfig(
        api_url=args.api_url,
        cache_dir=args.cache_dir,
        use_cached=args.use_cached,
        skip_api_if_missing=args.skip_api_if_missing,
        timeout=args.timeout,
    )
    client = OpenTargetsClient(config)
    evidence, features = enrich_pairs(pairs, client, max_pairs=args.max_pairs)
    write_opentargets_outputs(evidence, features, args.output, args.features_output)

    status_counts = summarize_feature_status(features)
    print(f"Wrote Open Targets evidence: {args.output} ({len(evidence)} rows)")
    print(f"Wrote Open Targets pair features: {args.features_output} ({len(features)} rows)")
    print(f"Status counts: {status_counts}")
    print(f"Cache directory: {args.cache_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

