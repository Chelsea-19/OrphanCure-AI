"""Export compact manual-review packets for selected OrphanCure cases."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export selected case-study evidence packets.")
    parser.add_argument("--selected_cases", type=Path, default=PROJECT_ROOT / "docs" / "case_studies" / "selected_cases.csv")
    parser.add_argument("--pubmed_evidence", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "pubmed_evidence.csv")
    parser.add_argument("--opentargets_evidence", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "opentargets_evidence.csv")
    parser.add_argument("--graph_paths", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "graph" / "graph_pair_paths.csv")
    parser.add_argument("--reports_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "reports" / "full")
    parser.add_argument("--output_dir", type=Path, default=PROJECT_ROOT / "case_review_packet")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    selected = pd.read_csv(args.selected_cases, dtype={"pair_id": str})
    pubmed = read_optional_csv(args.pubmed_evidence, dtype={"pair_id": str, "pmid": str})
    opentargets = read_optional_csv(args.opentargets_evidence, dtype={"pair_id": str})
    graph_paths = read_optional_csv(args.graph_paths, dtype={"pair_id": str})

    selected.to_csv(args.output_dir / "selected_cases.csv", index=False)
    (args.output_dir / "README.md").write_text(
        "# OrphanCure Case Review Packet\n\n"
        "This packet contains compact evidence slices for manual biomedical review. "
        "It does not include API keys, raw caches, raw repoDB, or the full PrimeKG graph.\n\n"
        "All cases remain research-support artifacts and are not medical advice.\n",
        encoding="utf-8",
    )

    for idx, row in selected.reset_index(drop=True).iterrows():
        pair_id = str(row["pair_id"])
        case_dir = args.output_dir / f"case_{idx + 1:02d}"
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "summary.md").write_text(render_summary(row), encoding="utf-8")
        write_slice(pubmed, pair_id, case_dir / "pubmed_evidence.csv")
        write_slice(opentargets, pair_id, case_dir / "opentargets_evidence.csv")
        write_slice(graph_paths, pair_id, case_dir / "graph_paths.csv")
        report = args.reports_dir / f"{pair_id}.md"
        if report.exists():
            shutil.copyfile(report, case_dir / "full_report.md")
    return 0


def read_optional_csv(path: Path, dtype: dict[str, str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=dtype)


def write_slice(df: pd.DataFrame, pair_id: str, output: Path) -> None:
    if df.empty or "pair_id" not in df.columns:
        pd.DataFrame().to_csv(output, index=False)
        return
    df[df["pair_id"].astype(str) == pair_id].to_csv(output, index=False)


def render_summary(row: pd.Series) -> str:
    return (
        f"# {row.get('drug_name')} - {row.get('disease_name')}\n\n"
        f"- pair_id: `{row.get('pair_id')}`\n"
        f"- repoDB label: `{row.get('expected_label')}`\n"
        f"- full prediction: `{row.get('full_predicted_label')}`\n"
        f"- full status: `{row.get('full_status')}`\n"
        f"- case type: `{row.get('case_type')}`\n"
        f"- manual review status: `{row.get('manual_review_status')}`\n\n"
        "This packet is for manual research review only. It is not medical advice "
        "and must not be used for clinical decision-making.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
