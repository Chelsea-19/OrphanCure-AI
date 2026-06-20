"""Download the real repoDB source CSV and write provenance metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.repodb_source import (  # noqa: E402
    RepoDBDownloadError,
    download_repodb_source,
    manual_download_instructions,
)


DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "external" / "repodb_raw"
DEFAULT_NORMALIZED = PROJECT_ROOT / "data" / "external" / "repodb.csv"
DEFAULT_METADATA = PROJECT_ROOT / "data" / "external" / "repodb_source_metadata.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download and validate the real repoDB source CSV.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_NORMALIZED)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--timeout", type=int, default=30)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        prepared = download_repodb_source(
            raw_dir=args.raw_dir,
            normalized_csv_path=args.output,
            metadata_path=args.metadata,
            timeout=args.timeout,
        )
    except RepoDBDownloadError as exc:
        print(str(exc))
        print()
        print(manual_download_instructions())
        return 1

    print("repoDB source downloaded and validated.")
    print(json.dumps(prepared.metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

