"""Prepare graph mechanism/path benchmark outputs for repoDB pairs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.graph_benchmark import (  # noqa: E402
    MissingGraphFilesError,
    load_graph_files,
    manual_graph_download_instructions,
    prepare_graph_outputs,
    write_graph_outputs,
)


DEFAULT_PAIRS = PROJECT_ROOT / "data" / "benchmark" / "repodb_pairs.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "benchmark" / "graph"
DEFAULT_GRAPH_DIR = PROJECT_ROOT / "data" / "external" / "primekg"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare PrimeKG/PharmKG graph benchmark outputs.")
    parser.add_argument("--graph_source", choices=["primekg", "pharmkg"], default="primekg")
    parser.add_argument("--graph_dir", type=Path, default=DEFAULT_GRAPH_DIR)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max_pairs", type=int, default=50)
    parser.add_argument("--max_path_length", type=int, default=4)
    parser.add_argument("--top_k_paths", type=int, default=10)
    parser.add_argument("--use_cached", action="store_true", help="Accepted for CLI symmetry; graph files are local.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        graph = load_graph_files(args.graph_source, args.graph_dir)
    except MissingGraphFilesError as exc:
        print(str(exc))
        print()
        print(manual_graph_download_instructions(args.graph_source, args.graph_dir))
        return 1

    pairs = pd.read_csv(args.pairs)
    nodes, edges, mappings, paths, features = prepare_graph_outputs(
        pairs,
        graph,
        max_pairs=args.max_pairs,
        max_path_length=args.max_path_length,
        top_k_paths=args.top_k_paths,
    )
    write_graph_outputs(args.output_dir, nodes, edges, mappings, paths, features)
    print(f"Wrote graph nodes: {args.output_dir / 'graph_nodes_normalized.csv'} ({len(nodes)} rows)")
    print(f"Wrote graph edges: {args.output_dir / 'graph_edges_normalized.csv'} ({len(edges)} rows)")
    print(f"Wrote graph mappings: {args.output_dir / 'graph_pair_mappings.csv'} ({len(mappings)} rows)")
    print(f"Wrote graph paths: {args.output_dir / 'graph_pair_paths.csv'} ({len(paths)} rows)")
    print(f"Wrote graph features: {args.output_dir / 'graph_pair_features.csv'} ({len(features)} rows)")
    print(f"Feature status counts: {features['status'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

