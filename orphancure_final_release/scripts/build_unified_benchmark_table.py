"""Build a unified repoDB/Open Targets/graph benchmark feature table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.unified_benchmark import build_unified_benchmark_table, evidence_coverage_metrics  # noqa: E402


DEFAULT_REPODB_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_SPLIT = PROJECT_ROOT / "data" / "benchmark" / "repodb_split.csv"
DEFAULT_OPENTARGETS = PROJECT_ROOT / "data" / "benchmark" / "opentargets_pair_features.csv"
DEFAULT_GRAPH = PROJECT_ROOT / "data" / "benchmark" / "graph" / "graph_pair_features.csv"
DEFAULT_PUBMED = PROJECT_ROOT / "data" / "benchmark" / "pubmed_pair_features.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Left-join repoDB, Open Targets, and graph benchmark features.")
    parser.add_argument("--repodb_pairs", type=Path, default=DEFAULT_REPODB_PAIRS)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--opentargets_features", type=Path, default=DEFAULT_OPENTARGETS)
    parser.add_argument("--graph_features", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--pubmed_features", type=Path, default=DEFAULT_PUBMED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repodb_pairs = pd.read_csv(args.repodb_pairs)
    opentargets_features = pd.read_csv(args.opentargets_features) if args.opentargets_features.exists() else pd.DataFrame()
    graph_features = pd.read_csv(args.graph_features) if args.graph_features.exists() else pd.DataFrame()
    pubmed_features = pd.read_csv(args.pubmed_features) if args.pubmed_features and args.pubmed_features.exists() else pd.DataFrame()
    split = pd.read_csv(args.split) if args.split and args.split.exists() else None

    unified = build_unified_benchmark_table(repodb_pairs, opentargets_features, graph_features, split, pubmed_features=pubmed_features)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    unified.to_csv(args.output, index=False)
    coverage = evidence_coverage_metrics(unified)

    print(f"Wrote unified benchmark features: {args.output} ({len(unified)} rows)")
    print(f"Open Targets availability rate: {coverage['opentargets_availability_rate']}")
    print(f"Graph availability rate: {coverage['graph_availability_rate']}")
    print(f"PubMed availability rate: {coverage.get('pubmed_availability_rate', 0.0)}")
    print(f"Both evidence layers available rate: {coverage['both_evidence_layers_available_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
