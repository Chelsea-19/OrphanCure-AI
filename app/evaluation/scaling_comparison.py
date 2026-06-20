"""Build public-safe scaling comparison tables and figures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


SCALING_COLUMNS = [
    "run_name",
    "n_selected",
    "n_completed",
    "n_partial_success",
    "n_failed",
    "original_accuracy",
    "original_precision",
    "original_recall",
    "original_F1",
    "original_ROC_AUC",
    "best_score_name",
    "best_score_accuracy",
    "best_score_precision",
    "best_score_recall",
    "best_score_F1",
    "best_score_ROC_AUC",
    "triage_coverage",
    "triage_abstention",
    "triage_accuracy_on_covered",
    "citation_verified_rate",
    "unsupported_claim_rate",
    "no_verifier_unsupported_claim_rate",
    "mean_runtime_seconds",
    "notes",
]


def build_scaling_summary(
    run_specs: list[dict[str, Any]],
    output_dir: Path,
    figures_dir: Path,
) -> pd.DataFrame:
    rows = [scaling_row(**spec) for spec in run_specs]
    summary = pd.DataFrame(rows).reindex(columns=SCALING_COLUMNS)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / "scaling_summary.csv", index=False)
    (output_dir / "scaling_summary.md").write_text(scaling_summary_markdown(summary), encoding="utf-8")
    write_scaling_figures(summary, figures_dir)
    return summary


def scaling_row(
    run_name: str,
    run_dir: Path,
    selected_path: Path | None = None,
    diagnostics_dir: Path | None = None,
) -> dict[str, Any]:
    diagnostics_dir = diagnostics_dir or run_dir
    result_path = run_dir / "per_pair_results_full.csv"
    summary_path = run_dir / "summary_metrics_full.json"
    selected = _read_csv(selected_path) if selected_path else pd.DataFrame()
    results = _read_csv(result_path)
    n_selected = int(len(selected)) if not selected.empty else int(len(results)) if not results.empty else 0

    if not result_path.exists() or results.empty:
        return {
            "run_name": run_name,
            "n_selected": n_selected,
            "n_completed": 0,
            "n_partial_success": 0,
            "n_failed": 0,
            "notes": "TODO_NOT_RUN: scaled full-agent result file is not available; no metrics were fabricated.",
        }

    metrics = _read_json(summary_path)
    status_counts = results["status"].value_counts(dropna=False).to_dict() if "status" in results.columns else {}
    if metrics.get("status") == "TODO_NOT_RUN" or int(status_counts.get("completed", 0)) == 0:
        return {
            "run_name": run_name,
            "n_selected": n_selected,
            "n_completed": int(status_counts.get("completed", 0)),
            "n_partial_success": int(status_counts.get("partial_success", 0)),
            "n_failed": int(status_counts.get("failed", 0)),
            "notes": "TODO_NOT_RUN: no completed full-agent rows; no scaled full-agent metrics were fabricated.",
        }
    best = _best_alternative(diagnostics_dir / "alternative_score_comparison.csv")
    triage = _read_json(diagnostics_dir / "triage_metrics_full.json")
    no_verifier = _read_json(run_dir / "summary_metrics_no_verifier.json")
    return {
        "run_name": run_name,
        "n_selected": n_selected,
        "n_completed": int(status_counts.get("completed", 0)),
        "n_partial_success": int(status_counts.get("partial_success", 0)),
        "n_failed": int(status_counts.get("failed", 0)),
        "original_accuracy": metrics.get("accuracy"),
        "original_precision": metrics.get("precision"),
        "original_recall": metrics.get("recall"),
        "original_F1": metrics.get("f1"),
        "original_ROC_AUC": metrics.get("roc_auc"),
        "best_score_name": best.get("score_name"),
        "best_score_accuracy": best.get("accuracy"),
        "best_score_precision": best.get("precision"),
        "best_score_recall": best.get("recall"),
        "best_score_F1": best.get("f1"),
        "best_score_ROC_AUC": best.get("roc_auc"),
        "triage_coverage": triage.get("coverage_rate"),
        "triage_abstention": triage.get("abstention_rate"),
        "triage_accuracy_on_covered": triage.get("accuracy_on_covered_cases"),
        "citation_verified_rate": metrics.get("citation_verified_rate"),
        "unsupported_claim_rate": metrics.get("unsupported_claim_rate"),
        "no_verifier_unsupported_claim_rate": no_verifier.get("unsupported_claim_rate"),
        "mean_runtime_seconds": metrics.get("mean_runtime_seconds"),
        "notes": metrics.get("notes", "Completed full-agent run; metrics remain research-support only."),
    }


def scaling_summary_markdown(summary: pd.DataFrame) -> str:
    lines = [
        "# Full-Agent Scaling Summary",
        "",
        "| Run | Selected | Completed | Partial | Failed | Original F1 | Best Score | Best F1 | Triage Coverage | Verifier Unsupported | no_verifier Unsupported | Notes |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            "| {run_name} | {n_selected} | {n_completed} | {n_partial_success} | {n_failed} | {original_F1} | {best_score_name} | {best_score_F1} | {triage_coverage} | {unsupported_claim_rate} | {no_verifier_unsupported_claim_rate} | {notes} |".format(
                **{column: _fmt(row.get(column)) for column in SCALING_COLUMNS}
            )
        )
    lines.extend(
        [
            "",
            "Missing scaled runs are shown as `TODO_NOT_RUN`; no scaled predictions or metrics are inferred.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_scaling_figures(summary: pd.DataFrame, figures_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    figures_dir.mkdir(parents=True, exist_ok=True)
    runs = summary["run_name"].astype(str).tolist()

    def numeric(column: str) -> pd.Series:
        return pd.to_numeric(summary[column], errors="coerce")

    plt.figure(figsize=(7, 4))
    plt.plot(runs, numeric("original_F1"), marker="o", label="Original confidence F1")
    plt.plot(runs, numeric("best_score_F1"), marker="o", label="Best alternative F1")
    plt.ylim(0, 1)
    plt.ylabel("F1")
    plt.title("Scaling F1 Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "scaling_f1_comparison.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(runs, numeric("original_ROC_AUC"), marker="o", label="Original confidence ROC-AUC")
    plt.plot(runs, numeric("best_score_ROC_AUC"), marker="o", label="Best alternative ROC-AUC")
    plt.ylim(0, 1)
    plt.ylabel("ROC-AUC")
    plt.title("Scaling ROC-AUC Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "scaling_roc_auc_comparison.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(runs, numeric("triage_coverage"), marker="o", label="Coverage")
    plt.plot(runs, numeric("triage_accuracy_on_covered"), marker="o", label="Accuracy on covered")
    plt.ylim(0, 1)
    plt.ylabel("Rate")
    plt.title("Scaling Triage Coverage vs Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "scaling_triage_coverage_accuracy.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(runs, numeric("unsupported_claim_rate"), marker="o", label="Full unsupported claim rate")
    plt.plot(runs, numeric("no_verifier_unsupported_claim_rate"), marker="o", label="no_verifier unsupported claim rate")
    plt.ylim(0, 1.05)
    plt.ylabel("Unsupported claim rate")
    plt.title("Scaling Verifier Effect")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "scaling_verifier_effect.png", dpi=160)
    plt.close()


def _read_csv(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _best_alternative(path: Path) -> dict[str, Any]:
    df = _read_csv(path)
    if df.empty:
        return {}
    ranked = df.sort_values(["f1", "roc_auc"], ascending=[False, False], na_position="last")
    return ranked.iloc[0].to_dict()


def _fmt(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)
