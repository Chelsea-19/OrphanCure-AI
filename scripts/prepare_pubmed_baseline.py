"""Prepare PubMed-only baseline features for repoDB benchmark pairs."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.pubmed_baseline import PubMedClient, PubMedConfig, prepare_pubmed_outputs  # noqa: E402


DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_FEATURES = PROJECT_ROOT / "data" / "benchmark" / "pubmed_pair_features.csv"
DEFAULT_EVIDENCE = PROJECT_ROOT / "data" / "benchmark" / "pubmed_evidence.csv"
DEFAULT_CACHE = PROJECT_ROOT / "data" / "external" / "pubmed_cache"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retrieve PubMed co-mention evidence for repoDB pairs.")
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--output", type=Path, default=DEFAULT_FEATURES)
    parser.add_argument("--evidence_output", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--cache_dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--max_pairs", type=int, default=20)
    parser.add_argument("--max_results_per_query", type=int, default=20)
    parser.add_argument("--email", default=os.getenv("PUBMED_EMAIL", ""))
    parser.add_argument("--ncbi_api_key", default=os.getenv("NCBI_API_KEY", ""))
    parser.add_argument("--use_cached", action="store_true")
    parser.add_argument("--skip_api_if_missing", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    pairs = pd.read_csv(args.pairs)
    config = PubMedConfig(
        email=args.email,
        ncbi_api_key=args.ncbi_api_key,
        cache_dir=args.cache_dir,
        max_results_per_query=args.max_results_per_query,
        timeout=args.timeout,
        retries=args.retries,
        use_cached=args.use_cached,
        skip_api_if_missing=args.skip_api_if_missing,
    )
    client = PubMedClient(config)
    evidence, features = prepare_pubmed_outputs(pairs, client, max_pairs=args.max_pairs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False)
    evidence.to_csv(args.evidence_output, index=False)
    print(f"Wrote PubMed pair features: {args.output} ({len(features)} rows)")
    print(f"Wrote PubMed evidence: {args.evidence_output} ({len(evidence)} rows)")
    print(f"Status counts: {features['status'].value_counts().to_dict() if not features.empty else {}}")
    print(f"Unique PMIDs: {features['n_unique_pmids'].sum() if 'n_unique_pmids' in features else 0}")
    if not args.email:
        print("No PubMed email configured. NCBI recommends setting --email or PUBMED_EMAIL for real API runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
