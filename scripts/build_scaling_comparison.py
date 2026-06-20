"""Build 20/50/100 full-agent scaling comparison artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.scaling_comparison import build_scaling_summary  # noqa: E402


DEFAULT_OUTPUT = PROJECT_ROOT / "eval_results" / "scaling_comparison"
DEFAULT_FIGURES = PROJECT_ROOT / "docs" / "figures"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build full-agent scaling comparison tables and figures.")
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--figures_dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--run20_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline")
    parser.add_argument("--run20", dest="run20_alias", type=Path, help="Alias for --run20_dir.")
    parser.add_argument("--run50_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline_scaled_50")
    parser.add_argument("--run50", dest="run50_alias", type=Path, help="Alias for --run50_dir.")
    parser.add_argument("--run100_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline_scaled_100")
    parser.add_argument("--run100", dest="run100_alias", type=Path, help="Alias for --run100_dir.")
    parser.add_argument("--selected50", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "scaled_selected_pairs_50.csv")
    parser.add_argument("--selected100", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "scaled_selected_pairs_100.csv")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run20_dir = args.run20_alias or args.run20_dir
    run50_dir = args.run50_alias or args.run50_dir
    run100_dir = args.run100_alias or args.run100_dir
    specs = [
        {"run_name": "20_pair", "run_dir": run20_dir, "diagnostics_dir": run20_dir},
        {
            "run_name": "50_pair",
            "run_dir": run50_dir,
            "selected_path": args.selected50,
            "diagnostics_dir": run50_dir / "diagnostics",
        },
        {
            "run_name": "100_pair",
            "run_dir": run100_dir,
            "selected_path": args.selected100,
            "diagnostics_dir": run100_dir / "diagnostics",
        },
    ]
    summary = build_scaling_summary(specs, args.output_dir, args.figures_dir)
    print(json.dumps({"rows": len(summary), "output_dir": str(args.output_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
