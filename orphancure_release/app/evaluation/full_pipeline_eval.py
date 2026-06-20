"""Utilities for evaluating the full OrphanCure agent pipeline.

The functions in this module intentionally separate the evaluation harness from
the live biomedical agent run. When LLM configuration is missing, callers get
explicit TODO_NOT_RUN rows instead of fabricated reports or metrics.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from app.config.settings import load_settings
from app.evaluation.unified_benchmark import (
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    classification_metrics,
)
from app.models.entities import Entity
from app.models.evidence import VerificationStatus
from app.models.state import UnifiedRunState


FULL_PIPELINE_MODES = (
    "full",
    "no_verifier",
    "no_target_expansion",
    "no_graph_features",
    "pubmed_only_report",
    "structured_only_report",
)

FULL_PIPELINE_COLUMNS = (
    "pair_id",
    "drug_name",
    "disease_name",
    "expected_label",
    "mode",
    "predicted_label",
    "confidence_score",
    "final_assessment",
    "n_claims",
    "n_verified_claims",
    "n_unsupported_claims",
    "citation_verified_rate",
    "unsupported_claim_rate",
    "n_pmids_used",
    "n_opentargets_evidence_items",
    "n_graph_paths_used",
    "report_path",
    "raw_output_path",
    "runtime_seconds",
    "status",
    "error_message",
    "notes",
)

TODO_STATUS = "TODO_NOT_RUN"
COMPLETED_STATUSES = {"completed", "success", "partial_success"}
LLM_REQUIRED_MODES = {
    "full",
    "no_verifier",
    "no_target_expansion",
    "no_graph_features",
    "pubmed_only_report",
    "structured_only_report",
}


def load_benchmark_pairs(path: str | Path, max_pairs: int | None = None) -> pd.DataFrame:
    """Load repoDB benchmark pairs while preserving row order."""
    pairs = pd.read_csv(path)
    required = {"pair_id", "drug_name", "disease_name", "expected_label"}
    missing = required - set(pairs.columns)
    if missing:
        raise ValueError(f"benchmark pairs are missing required columns: {sorted(missing)}")
    if max_pairs:
        return pairs.head(max_pairs).copy()
    return pairs.copy()


def select_evaluation_subset(
    pairs: pd.DataFrame,
    unified_features: pd.DataFrame | None,
    max_pairs: int = 20,
) -> pd.DataFrame:
    """Select pairs with the most available evidence first.

    The sort prefers rows with PubMed, Open Targets, and graph features, then
    rows with any two layers, while retaining all original pair fields.
    """
    subset = pairs.copy()
    subset["_original_order"] = range(len(subset))
    if unified_features is not None and not unified_features.empty:
        feature_cols = [
            "pair_id",
            "pubmed_available",
            "opentargets_available",
            "graph_available",
            "n_unique_pmids",
            "n_overlapping_targets",
            "n_paths_len_2",
            "n_paths_len_3",
            "n_paths_len_4",
        ]
        available_cols = [col for col in feature_cols if col in unified_features.columns]
        subset = subset.merge(
            unified_features[available_cols].drop_duplicates("pair_id"),
            on="pair_id",
            how="left",
        )

    for column in ("pubmed_available", "opentargets_available", "graph_available"):
        if column not in subset.columns:
            subset[column] = False
        subset[column] = _as_bool(subset[column])
    subset["_evidence_layers"] = (
        subset["pubmed_available"].astype(int)
        + subset["opentargets_available"].astype(int)
        + subset["graph_available"].astype(int)
    )
    subset["_all_three"] = subset["_evidence_layers"] == 3
    subset["_pmid_count"] = _numeric_column(subset, "n_unique_pmids")
    subset["_target_count"] = _numeric_column(subset, "n_overlapping_targets")
    path_counts = [
        _numeric_column(subset, column)
        for column in ("n_paths_len_2", "n_paths_len_3", "n_paths_len_4")
    ]
    subset["_path_count"] = sum(path_counts)

    subset = subset.sort_values(
        by=[
            "_all_three",
            "_evidence_layers",
            "pubmed_available",
            "opentargets_available",
            "graph_available",
            "_pmid_count",
            "_target_count",
            "_path_count",
            "_original_order",
        ],
        ascending=[False, False, False, False, False, False, False, False, True],
    )
    return subset.head(max_pairs).drop(columns=[c for c in subset.columns if c.startswith("_")])


def llm_config_available() -> bool:
    """Return True when Gemini is configured for the current process."""
    return bool(os.getenv("GEMINI_API_KEY") or load_settings().gemini_api_key)


def missing_llm_reason() -> str:
    return "GEMINI_API_KEY is not configured; full OrphanCure synthesis/report generation was not run."


def run_full_pipeline_for_pair(
    pair: pd.Series | dict[str, Any],
    mode: str,
    output_dir: str | Path,
    *,
    use_cached: bool = False,
    skip_llm_if_missing: bool = True,
    demo_mode: bool = False,
    runner: Callable[[dict[str, Any], str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run one full-pipeline mode and return a normalized result row."""
    pair_dict = dict(pair)
    out_dir = Path(output_dir)
    raw_dir = out_dir / "raw_outputs" / mode
    report_dir = out_dir / "reports" / mode
    raw_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    pair_id = str(pair_dict["pair_id"])
    raw_path = raw_dir / f"{pair_id}.json"
    report_path = report_dir / f"{pair_id}.md"

    if mode not in FULL_PIPELINE_MODES:
        raise ValueError(f"Unsupported full-pipeline mode: {mode}")

    if runner is not None:
        raw_output = runner(pair_dict, mode)
        row = normalize_full_pipeline_output(pair_dict, mode, raw_output, raw_path, report_path)
        row["runtime_seconds"] = float(time.perf_counter() - start)
        _write_raw(raw_path, raw_output)
        _write_report(report_path, row, raw_output)
        return row

    if mode in LLM_REQUIRED_MODES and not llm_config_available():
        if not skip_llm_if_missing:
            raise RuntimeError(missing_llm_reason())
        raw_output = {
            "status": TODO_STATUS,
            "mode": mode,
            "pair_id": pair_id,
            "error_message": missing_llm_reason(),
            "notes": (
                "No biomedical report, claim, PMID selection, or metric was generated. "
                "Configure GEMINI_API_KEY and rerun scripts/run_full_pipeline_eval.py."
            ),
            "use_cached": bool(use_cached),
            "demo_mode": bool(demo_mode),
        }
        row = todo_result_row(pair_dict, mode, raw_path, report_path, raw_output["error_message"])
        row["runtime_seconds"] = float(time.perf_counter() - start)
        _write_raw(raw_path, raw_output)
        _write_todo_report(report_path, row)
        return row

    raw_output = _run_current_orphancure_pipeline(pair_dict, mode, use_cached=use_cached)
    row = normalize_full_pipeline_output(pair_dict, mode, raw_output, raw_path, report_path)
    row["runtime_seconds"] = float(time.perf_counter() - start)
    _write_raw(raw_path, raw_output)
    _write_report(report_path, row, raw_output)
    return row


def _run_current_orphancure_pipeline(pair: dict[str, Any], mode: str, *, use_cached: bool = False) -> dict[str, Any]:
    """Thin wrapper over the current app pipeline.

    The current application pipeline was designed for interactive Streamlit use.
    This wrapper keeps Phase 6C evaluation close to that surface without
    rewriting the agents.
    """
    from app.orchestrator.pipeline import Pipeline
    from app.reporting.report_builder import ReportBuilder
    from app.services.llm_provider import GeminiProvider

    settings = load_settings()
    llm = GeminiProvider(settings)
    state = UnifiedRunState(
        input_mode="drug_and_disease",
        drug_input=str(pair["drug_name"]),
        disease_input=str(pair["disease_name"]),
    )

    if mode == "no_target_expansion":
        settings = settings.__class__(**{**settings.__dict__, "pubmed_target_expansion": False})

    if mode == "no_graph_features":
        state.common_targets = []
        state.mechanism_evidence = []

    pipeline = Pipeline(state, llm, settings)
    if mode == "no_verifier":
        from app.agents.literature import LiteratureAgent
        from app.agents.mechanism import MechanismAgent
        from app.agents.synthesis_critic import SynthesisCriticAgent

        pipeline.run_wave1()
        if state.stage == "analysis":
            if not state.common_targets and not state.drug_data:
                MechanismAgent(state, llm, settings).execute()
            LiteratureAgent(state, llm, settings).execute()
            SynthesisCriticAgent(state, llm, settings).execute()
            state.stage = "results"
    elif mode == "no_graph_features":
        pipeline.run_wave1()
        state.common_targets = []
        state.mechanism_evidence = []
        if state.stage == "analysis":
            pipeline.run_wave2()
    elif mode == "pubmed_only_report":
        pipeline.run_wave1()
        state.common_targets = []
        state.mechanism_evidence = []
        if state.stage == "analysis":
            pipeline.run_wave2()
    elif mode == "structured_only_report":
        pipeline.run_wave1()
        state.papers = []
        state.retrieval_queries = []
        if state.stage == "analysis":
            pipeline.run_wave2()
    else:
        pipeline.run_full()

    final_report = _safe_report_dict(state.final_report)
    structured_report = ReportBuilder(state).build() if final_report and "error" not in final_report else {}
    raw_status = "completed" if state.stage == "results" and final_report and "error" not in final_report else "partial_success"
    if not final_report:
        error_message = "Pipeline completed without a final report object."
    elif "error" in final_report:
        error_message = str(final_report.get("error") or "Pipeline final report contains an error.")
    else:
        error_message = ""
    return {
        "status": raw_status if state.stage == "results" else "partial_success",
        "mode": mode,
        "state": json.loads(state.export_json()),
        "structured_report": structured_report,
        "final_assessment": final_report.get("conclusion", "") if final_report else "",
        "confidence_score": _confidence_from_state(state),
        "predicted_label": _label_from_report(final_report),
        "error_message": error_message,
        "notes": "Generated by current OrphanCure Pipeline.run_full wrapper.",
        "use_cached": bool(use_cached),
    }


def normalize_full_pipeline_output(
    pair: pd.Series | dict[str, Any],
    mode: str,
    raw_output: dict[str, Any],
    raw_path: str | Path = "",
    report_path: str | Path = "",
) -> dict[str, Any]:
    """Normalize a raw full-pipeline output into the evaluation CSV schema."""
    pair_dict = dict(pair)
    state = raw_output.get("state", {}) if isinstance(raw_output, dict) else {}
    claims = _claims_from_raw(raw_output)
    n_claims, n_verified, n_unsupported = claim_verification_counts(claims)
    citation_rate = n_verified / n_claims if n_claims else None
    unsupported_rate = n_unsupported / n_claims if n_claims else None
    status = str(raw_output.get("status", "completed"))
    return _complete_row(
        pair_dict,
        mode,
        predicted_label=raw_output.get("predicted_label", ""),
        confidence_score=raw_output.get("confidence_score"),
        final_assessment=raw_output.get("final_assessment", raw_output.get("conclusion", "")),
        n_claims=n_claims,
        n_verified_claims=n_verified,
        n_unsupported_claims=n_unsupported,
        citation_verified_rate=citation_rate,
        unsupported_claim_rate=unsupported_rate,
        n_pmids_used=len(_pmids_from_raw(raw_output)),
        n_opentargets_evidence_items=_count_state_list(state, "common_targets"),
        n_graph_paths_used=int(raw_output.get("n_graph_paths_used") or _count_state_list(state, "mechanism_evidence")),
        report_path=str(report_path),
        raw_output_path=str(raw_path),
        runtime_seconds=float(raw_output.get("runtime_seconds", 0.0) or 0.0),
        status=status,
        error_message=str(raw_output.get("error_message", "")),
        notes=str(raw_output.get("notes", "")),
    )


def todo_result_row(
    pair: pd.Series | dict[str, Any],
    mode: str,
    raw_path: str | Path,
    report_path: str | Path,
    reason: str,
) -> dict[str, Any]:
    """Return a schema-complete TODO_NOT_RUN row."""
    return _complete_row(
        dict(pair),
        mode,
        predicted_label=TODO_STATUS,
        confidence_score=None,
        final_assessment=TODO_STATUS,
        n_claims=None,
        n_verified_claims=None,
        n_unsupported_claims=None,
        citation_verified_rate=None,
        unsupported_claim_rate=None,
        n_pmids_used=None,
        n_opentargets_evidence_items=None,
        n_graph_paths_used=None,
        report_path=str(report_path),
        raw_output_path=str(raw_path),
        runtime_seconds=0.0,
        status=TODO_STATUS,
        error_message=reason,
        notes="Full-pipeline result not generated; no claims or metrics were fabricated.",
    )


def claim_verification_counts(claims: list[dict[str, Any]]) -> tuple[int, int, int]:
    """Count claim verification statuses from normalized or Pydantic-like dicts."""
    n_claims = len(claims)
    verified = 0
    unsupported = 0
    for claim in claims:
        status = str(claim.get("verification_status", "")).upper()
        if status == VerificationStatus.VERIFIED.value:
            verified += 1
        if status in {"UNVERIFIED", "UNSUPPORTED", "CONTRADICTED"}:
            unsupported += 1
    return n_claims, verified, unsupported


def summarize_full_pipeline_results(results: pd.DataFrame, mode: str) -> dict[str, Any]:
    """Compute label, report faithfulness, evidence usage, and runtime metrics."""
    completed = results[results["status"].isin(COMPLETED_STATUSES)].copy()
    label_rows = completed[
        completed["expected_label"].isin([POSITIVE_LABEL, NEGATIVE_LABEL])
        & completed["predicted_label"].isin([POSITIVE_LABEL, NEGATIVE_LABEL])
    ].copy()
    metrics = classification_metrics(
        (label_rows["expected_label"] == POSITIVE_LABEL).astype(int).tolist(),
        (label_rows["predicted_label"] == POSITIVE_LABEL).astype(int).tolist(),
        pd.to_numeric(label_rows["confidence_score"], errors="coerce").tolist(),
    )
    total = len(results)
    status_counts = {str(k): int(v) for k, v in results["status"].value_counts(dropna=False).items()}
    metrics.update(
        {
            "benchmark": "full_pipeline",
            "mode": mode,
            "status": "completed" if len(completed) else TODO_STATUS,
            "n_evaluated_pairs": int(len(label_rows)),
            "n_skipped_pairs": int(total - len(label_rows)),
            "mean_n_claims": _mean_or_none(completed, "n_claims"),
            "mean_n_verified_claims": _mean_or_none(completed, "n_verified_claims"),
            "mean_n_unsupported_claims": _mean_or_none(completed, "n_unsupported_claims"),
            "citation_verified_rate": _mean_or_none(completed, "citation_verified_rate"),
            "unsupported_claim_rate": _mean_or_none(completed, "unsupported_claim_rate"),
            "mean_n_pmids_used": _mean_or_none(completed, "n_pmids_used"),
            "mean_n_opentargets_evidence_items": _mean_or_none(completed, "n_opentargets_evidence_items"),
            "mean_n_graph_paths_used": _mean_or_none(completed, "n_graph_paths_used"),
            "mean_runtime_seconds": _mean_or_none(results, "runtime_seconds"),
            "success_rate": _rate_for_status(results, "completed"),
            "partial_success_rate": _rate_for_status(results, "partial_success"),
            "failure_rate": _rate_for_status(results, "failed"),
            "status_counts": status_counts,
            "notes": (
                "Full-pipeline metrics are report/evaluation metrics over generated outputs. "
                "They are not clinical validation."
            ),
        }
    )
    if not len(completed):
        metrics["notes"] = "Full-pipeline run is TODO_NOT_RUN; no reports or label metrics were fabricated."
    return metrics


def write_full_pipeline_outputs(
    results: pd.DataFrame,
    mode: str,
    output_dir: str | Path,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = results.reindex(columns=FULL_PIPELINE_COLUMNS)
    results.to_csv(out / f"per_pair_results_{mode}.csv", index=False)
    metrics = summarize_full_pipeline_results(results, mode)
    (out / f"summary_metrics_{mode}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out / f"summary_table_{mode}.md").write_text(full_pipeline_summary_table(metrics), encoding="utf-8")
    write_claim_verification_summary(out, results)
    return metrics


def write_claim_verification_summary(output_dir: str | Path, results: pd.DataFrame) -> None:
    out = Path(output_dir)
    rows = []
    for _, row in results.iterrows():
        rows.append(
            {
                "pair_id": row.get("pair_id"),
                "mode": row.get("mode"),
                "n_claims": row.get("n_claims"),
                "n_verified_claims": row.get("n_verified_claims"),
                "n_unsupported_claims": row.get("n_unsupported_claims"),
                "citation_verified_rate": row.get("citation_verified_rate"),
                "unsupported_claim_rate": row.get("unsupported_claim_rate"),
                "status": row.get("status"),
                "notes": row.get("notes"),
            }
        )
    pd.DataFrame(rows).to_csv(out / "claim_verification_summary.csv", index=False)


def full_pipeline_summary_table(metrics: dict[str, Any]) -> str:
    lines = ["# Full Pipeline Evaluation Summary", "", "| Metric | Value |", "|---|---:|"]
    for key, value in metrics.items():
        if isinstance(value, dict) or key in {"notes"}:
            continue
        lines.append(f"| {key} | {value} |")
    lines.extend(["", metrics.get("notes", "")])
    return "\n".join(lines) + "\n"


def _complete_row(pair: dict[str, Any], mode: str, **values: Any) -> dict[str, Any]:
    row = {
        "pair_id": pair.get("pair_id", ""),
        "drug_name": pair.get("drug_name", ""),
        "disease_name": pair.get("disease_name", ""),
        "expected_label": pair.get("expected_label", ""),
        "mode": mode,
    }
    row.update(values)
    return {column: row.get(column) for column in FULL_PIPELINE_COLUMNS}


def _as_bool(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.casefold()
        .map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
        .fillna(False)
    )


def _numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series([0] * len(df), index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def _write_raw(path: Path, raw_output: dict[str, Any]) -> None:
    path.write_text(json.dumps(raw_output, indent=2), encoding="utf-8")


def _write_todo_report(path: Path, row: dict[str, Any]) -> None:
    lines = [
        f"# Full Pipeline Report Placeholder: {row['pair_id']}",
        "",
        f"- Drug: {row['drug_name']}",
        f"- Disease: {row['disease_name']}",
        f"- Mode: {row['mode']}",
        f"- Status: {TODO_STATUS}",
        "",
        "No biomedical report was generated because the LLM-backed full pipeline was not configured.",
        "",
        f"Reason: {row['error_message']}",
        "",
        "This file is a TODO marker only. It contains no generated biomedical claims.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report(path: Path, row: dict[str, Any], raw_output: dict[str, Any]) -> None:
    report = raw_output.get("structured_report") or raw_output.get("final_report") or {}
    lines = [
        f"# OrphanCure Full Pipeline Report: {row['pair_id']}",
        "",
        f"- Drug: {row['drug_name']}",
        f"- Disease: {row['disease_name']}",
        f"- Mode: {row['mode']}",
        f"- Status: {row['status']}",
        f"- Final assessment: {row['final_assessment']}",
        "",
        "This generated report is for research support only and is not medical advice.",
        "",
        "## Structured Output",
        "",
        "```json",
        json.dumps(report, indent=2),
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _claims_from_raw(raw_output: dict[str, Any]) -> list[dict[str, Any]]:
    if raw_output.get("claims"):
        return list(raw_output["claims"])
    state = raw_output.get("state", {})
    claims = state.get("verified_claims") or state.get("draft_claims") or []
    return list(claims)


def _pmids_from_raw(raw_output: dict[str, Any]) -> set[str]:
    pmids = set(str(pmid) for pmid in raw_output.get("pmids_used", []) if str(pmid))
    state = raw_output.get("state", {})
    for paper in state.get("papers", []) or []:
        pmid = str(paper.get("pmid", ""))
        if pmid:
            pmids.add(pmid)
    for claim in _claims_from_raw(raw_output):
        provenance = claim.get("provenance", {}) or {}
        for evidence in provenance.get("paper_evidence", []) or []:
            pmid = str(evidence.get("pmid", ""))
            if pmid:
                pmids.add(pmid)
    return pmids


def _count_state_list(state: dict[str, Any], key: str) -> int:
    value = state.get(key, [])
    return len(value) if isinstance(value, list) else 0


def _confidence_from_state(state: UnifiedRunState) -> float | None:
    report = _safe_report_dict(state.final_report)
    confidence = str(report.get("overall_confidence", "")).lower()
    if confidence == "high":
        return 0.8
    if confidence == "medium":
        return 0.55
    if confidence == "low":
        return 0.3
    if state.scorecard:
        return float(state.scorecard.overall_score)
    return None


def _label_from_report(report: dict[str, Any]) -> str:
    report = _safe_report_dict(report)
    conclusion = str(report.get("conclusion", "")).lower()
    if conclusion in {"valid", "potential"}:
        return POSITIVE_LABEL
    if conclusion == "unlikely":
        return NEGATIVE_LABEL
    return ""


def _safe_report_dict(report: Any) -> dict[str, Any]:
    return report if isinstance(report, dict) else {}


def _mean_or_none(df: pd.DataFrame, column: str) -> float | None:
    if df.empty or column not in df.columns:
        return None
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    return float(values.mean()) if len(values) else None


def _rate_for_status(df: pd.DataFrame, status: str) -> float:
    if df.empty or "status" not in df.columns:
        return 0.0
    return float((df["status"] == status).mean())
