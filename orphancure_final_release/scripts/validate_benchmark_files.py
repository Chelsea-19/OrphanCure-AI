"""Validate prepared OrphanCure benchmark pair and split files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.repodb_benchmark import validate_benchmark_files  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate prepared benchmark files.")
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--split", type=Path)
    parser.add_argument("--opentargets_evidence", type=Path)
    parser.add_argument("--opentargets_features", type=Path)
    parser.add_argument("--graph_nodes", type=Path)
    parser.add_argument("--graph_edges", type=Path)
    parser.add_argument("--graph_mappings", type=Path)
    parser.add_argument("--graph_paths", type=Path)
    parser.add_argument("--graph_features", type=Path)
    parser.add_argument("--pubmed_features", type=Path)
    parser.add_argument("--pubmed_evidence", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors = validate_benchmark_files(
        args.pairs,
        args.split,
        opentargets_evidence_path=args.opentargets_evidence,
        opentargets_features_path=args.opentargets_features,
        graph_nodes_path=args.graph_nodes,
        graph_edges_path=args.graph_edges,
        graph_mappings_path=args.graph_mappings,
        graph_paths_path=args.graph_paths,
        graph_features_path=args.graph_features,
        pubmed_features_path=args.pubmed_features,
        pubmed_evidence_path=args.pubmed_evidence,
    )
    if errors:
        print("Benchmark validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Benchmark validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
