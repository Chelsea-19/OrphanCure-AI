"""Build manually reviewable case-study docs from completed evaluation outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DISCLAIMER = (
    "This case study is for research and educational purposes only. It is not "
    "medical advice and must not be used for clinical decision-making."
)

INVENTORY_COLUMNS = [
    "pair_id",
    "drug_name",
    "disease_name",
    "expected_label",
    "full_status",
    "full_predicted_label",
    "full_confidence_score",
    "full_correct",
    "n_claims",
    "n_verified_claims",
    "n_unsupported_claims",
    "citation_verified_rate",
    "unsupported_claim_rate",
    "n_pmids_used",
    "n_unique_pmids_available",
    "n_opentargets_evidence_items",
    "n_graph_paths_used",
    "has_full_report",
    "has_pubmed_evidence",
    "has_opentargets_evidence",
    "has_graph_evidence",
    "recommended_case_type",
    "recommended_for_manual_review",
    "notes",
]

CASE_FILENAMES = {
    "correct_positive": "case_01_correct_positive.md",
    "correct_negative_or_failed": "case_02_correct_negative_or_failed.md",
    "verifier_effect": "case_03_verifier_effect.md",
    "incorrect_but_informative": "case_04_incorrect_but_informative.md",
    "partial_success_error_analysis": "case_05_partial_success_optional.md",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build OrphanCure case-study docs.")
    parser.add_argument("--output_dir", type=Path, default=PROJECT_ROOT / "docs" / "case_studies")
    parser.add_argument("--full_results", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "per_pair_results_full.csv")
    parser.add_argument("--no_verifier_results", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "per_pair_results_no_verifier.csv")
    parser.add_argument("--unified", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "unified_benchmark_features.csv")
    parser.add_argument("--pubmed_evidence", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "pubmed_evidence.csv")
    parser.add_argument("--opentargets_features", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "opentargets_pair_features.csv")
    parser.add_argument("--opentargets_evidence", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "opentargets_evidence.csv")
    parser.add_argument("--graph_features", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "graph" / "graph_pair_features.csv")
    parser.add_argument("--graph_paths", type=Path, default=PROJECT_ROOT / "data" / "benchmark" / "graph" / "graph_pair_paths.csv")
    parser.add_argument("--raw_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "raw_outputs" / "full")
    parser.add_argument("--report_dir", type=Path, default=PROJECT_ROOT / "eval_results" / "full_pipeline" / "reports" / "full")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = load_inputs(args)
    inventory = build_inventory(data, args)
    inventory.to_csv(args.output_dir / "case_inventory.csv", index=False)
    selected = select_cases(inventory, data)
    selected.to_csv(args.output_dir / "selected_cases.csv", index=False)
    for _, row in selected.iterrows():
        case_type = str(row["case_type"])
        filename = CASE_FILENAMES[case_type]
        (args.output_dir / filename).write_text(render_case_markdown(row, data, args), encoding="utf-8")
    (args.output_dir / "case_studies_en.md").write_text(render_english_summary(selected), encoding="utf-8")
    (args.output_dir / "case_studies_zh.md").write_text(render_chinese_summary(selected), encoding="utf-8")
    return 0


def load_inputs(args: argparse.Namespace) -> dict[str, pd.DataFrame]:
    return {
        "full": pd.read_csv(args.full_results),
        "no_verifier": pd.read_csv(args.no_verifier_results) if args.no_verifier_results.exists() else pd.DataFrame(),
        "unified": pd.read_csv(args.unified),
        "pubmed_evidence": pd.read_csv(args.pubmed_evidence, dtype={"pmid": str}),
        "opentargets_features": pd.read_csv(args.opentargets_features),
        "opentargets_evidence": pd.read_csv(args.opentargets_evidence),
        "graph_features": pd.read_csv(args.graph_features),
        "graph_paths": pd.read_csv(args.graph_paths),
    }


def build_inventory(data: dict[str, pd.DataFrame], args: argparse.Namespace) -> pd.DataFrame:
    full = data["full"].copy()
    unified = data["unified"]
    no_verifier = data["no_verifier"]
    rows = []
    for _, row in full.iterrows():
        pair_id = str(row["pair_id"])
        u = first_row(unified, pair_id)
        nv = first_row(no_verifier, pair_id)
        full_correct = bool(row.get("expected_label") == row.get("predicted_label")) if row.get("predicted_label") in {"positive", "negative_or_failed"} else False
        has_report = (args.report_dir / f"{pair_id}.md").exists() and (args.report_dir / f"{pair_id}.md").stat().st_size > 500
        n_unique_pmids = to_float(u.get("n_unique_pmids"))
        case_type = recommend_case_type(row, nv, full_correct)
        notes = []
        if row.get("status") == "partial_success":
            notes.append("Partial success row retained for error analysis.")
        if row.get("expected_label") == "negative_or_failed" and full_correct and to_float(row.get("n_verified_claims")) == 0:
            notes.append("Closest correct negative case has no fully verified claims.")
        if not has_report:
            notes.append("Full report missing or placeholder-sized.")
        rows.append(
            {
                "pair_id": pair_id,
                "drug_name": row.get("drug_name"),
                "disease_name": row.get("disease_name"),
                "expected_label": row.get("expected_label"),
                "full_status": row.get("status"),
                "full_predicted_label": row.get("predicted_label"),
                "full_confidence_score": row.get("confidence_score"),
                "full_correct": full_correct,
                "n_claims": row.get("n_claims"),
                "n_verified_claims": row.get("n_verified_claims"),
                "n_unsupported_claims": row.get("n_unsupported_claims"),
                "citation_verified_rate": row.get("citation_verified_rate"),
                "unsupported_claim_rate": row.get("unsupported_claim_rate"),
                "n_pmids_used": row.get("n_pmids_used"),
                "n_unique_pmids_available": n_unique_pmids,
                "n_opentargets_evidence_items": row.get("n_opentargets_evidence_items"),
                "n_graph_paths_used": row.get("n_graph_paths_used"),
                "has_full_report": has_report,
                "has_pubmed_evidence": n_unique_pmids > 0,
                "has_opentargets_evidence": bool(u.get("opentargets_available")) if u else False,
                "has_graph_evidence": bool(u.get("graph_available")) if u else False,
                "recommended_case_type": case_type,
                "recommended_for_manual_review": case_type in {
                    "correct_positive",
                    "correct_negative_or_failed",
                    "verifier_effect",
                    "incorrect_but_informative",
                    "partial_success_error_analysis",
                },
                "notes": " ".join(notes),
            }
        )
    return pd.DataFrame(rows).reindex(columns=INVENTORY_COLUMNS)


def recommend_case_type(row: pd.Series, no_verifier: dict[str, Any], full_correct: bool) -> str:
    if row.get("status") == "partial_success":
        return "partial_success_error_analysis"
    if to_float(no_verifier.get("unsupported_claim_rate")) > to_float(row.get("unsupported_claim_rate")):
        return "verifier_effect"
    if row.get("expected_label") == "positive" and full_correct:
        return "correct_positive"
    if row.get("expected_label") == "negative_or_failed" and full_correct:
        return "correct_negative_or_failed"
    if row.get("status") == "completed" and not full_correct:
        return "incorrect_but_informative"
    return "partial_success_error_analysis"


def select_cases(inventory: pd.DataFrame, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    records = []
    seen = set()
    selectors = [
        lambda exclude: select_first(
            inventory,
            "correct_positive",
            'expected_label == "positive" and full_status == "completed" and full_correct == True and n_verified_claims > 0 and has_full_report == True',
            exclude,
        ),
        lambda exclude: select_first(
            inventory,
            "correct_negative_or_failed",
            'expected_label == "negative_or_failed" and full_status == "completed" and full_correct == True and has_full_report == True',
            exclude,
        ),
        lambda exclude: select_verifier_effect(inventory, data["no_verifier"], exclude),
        lambda exclude: select_first(
            inventory,
            "incorrect_but_informative",
            'full_status == "completed" and full_correct == False and has_full_report == True',
            exclude,
        ),
        lambda exclude: select_first(inventory, "partial_success_error_analysis", 'full_status == "partial_success"', exclude),
    ]
    for selector in selectors:
        case_type, row, reason = selector(seen)
        if not row or row["pair_id"] in seen:
            continue
        seen.add(row["pair_id"])
        record = dict(row)
        record["case_type"] = case_type
        record["case_file"] = CASE_FILENAMES[case_type]
        record["selection_reason"] = reason
        record["manual_review_status"] = "TODO_MANUAL_REVIEW"
        records.append(record)
    return pd.DataFrame(records)


def select_first(inventory: pd.DataFrame, case_type: str, query: str, exclude: set[str] | None = None) -> tuple[str, dict[str, Any], str]:
    exclude = exclude or set()
    candidates = inventory.query(query).copy()
    candidates = candidates[~candidates["pair_id"].astype(str).isin(exclude)]
    if candidates.empty and case_type == "correct_negative_or_failed":
        candidates = inventory.query('expected_label == "negative_or_failed" and full_status == "completed" and full_correct == True').copy()
        candidates = candidates[~candidates["pair_id"].astype(str).isin(exclude)]
        reason = "Closest available correct negative_or_failed case; ideal fully verified negative case was not available."
    elif candidates.empty and case_type == "partial_success_error_analysis":
        reason = "Selected partial_success case for pipeline limitation analysis."
    elif candidates.empty:
        candidates = inventory.query('full_status == "completed" and has_full_report == True').copy()
        candidates = candidates[~candidates["pair_id"].astype(str).isin(exclude)]
        reason = f"Closest available case for {case_type}; ideal criteria were not fully met."
    else:
        reason = f"Meets selection criteria for {case_type}."
    if candidates.empty:
        return case_type, {}, reason
    candidates["_score"] = (
        pd.to_numeric(candidates["n_verified_claims"], errors="coerce").fillna(0) * 10
        + pd.to_numeric(candidates["n_pmids_used"], errors="coerce").fillna(0)
        + pd.to_numeric(candidates["n_opentargets_evidence_items"], errors="coerce").fillna(0)
    )
    return case_type, candidates.sort_values("_score", ascending=False).iloc[0].drop(labels=["_score"]).to_dict(), reason


def select_verifier_effect(inventory: pd.DataFrame, no_verifier: pd.DataFrame, exclude: set[str] | None = None) -> tuple[str, dict[str, Any], str]:
    exclude = exclude or set()
    merged = inventory.merge(
        no_verifier[["pair_id", "unsupported_claim_rate", "n_unsupported_claims"]].rename(
            columns={"unsupported_claim_rate": "no_verifier_unsupported_claim_rate", "n_unsupported_claims": "no_verifier_unsupported_claims"}
        ),
        on="pair_id",
        how="left",
    )
    merged["effect"] = pd.to_numeric(merged["no_verifier_unsupported_claim_rate"], errors="coerce").fillna(0) - pd.to_numeric(merged["unsupported_claim_rate"], errors="coerce").fillna(0)
    candidates = merged.query('full_status == "completed" and effect > 0 and has_full_report == True').copy()
    candidates = candidates[~candidates["pair_id"].astype(str).isin(exclude)]
    if candidates.empty:
        return select_first(inventory, "verifier_effect", 'full_status == "completed" and has_full_report == True', exclude)
    candidates["_score"] = candidates["effect"] * 100 + pd.to_numeric(candidates["n_verified_claims"], errors="coerce").fillna(0)
    return "verifier_effect", candidates.sort_values("_score", ascending=False).iloc[0].drop(labels=["_score"]).to_dict(), "Shows lower unsupported-claim rate in full mode than no_verifier."


def render_case_markdown(row: pd.Series, data: dict[str, pd.DataFrame], args: argparse.Namespace) -> str:
    pair_id = str(row["pair_id"])
    raw = load_raw(args.raw_dir / f"{pair_id}.json")
    state = raw.get("state", {})
    claims = state.get("verified_claims") or state.get("draft_claims") or []
    papers = state.get("papers") or []
    unified = first_row(data["unified"], pair_id)
    ot = first_row(data["opentargets_features"], pair_id)
    graph = first_row(data["graph_features"], pair_id)
    graph_paths = data["graph_paths"][data["graph_paths"]["pair_id"].astype(str) == pair_id] if "pair_id" in data["graph_paths"].columns else pd.DataFrame()
    pubmed = data["pubmed_evidence"][data["pubmed_evidence"]["pair_id"].astype(str) == pair_id] if "pair_id" in data["pubmed_evidence"].columns else pd.DataFrame()
    top_pubmed = pubmed.drop_duplicates("pmid").head(5)
    report_summary = report_excerpt(raw)
    claim_lines = claim_summary_lines(claims)
    path_lines = graph_path_lines(graph_paths)
    checklist = [
        "- [ ] repoDB row checked",
        "- [ ] PubMed PMIDs checked",
        "- [ ] Abstracts checked",
        "- [ ] Open Targets mappings checked",
        "- [ ] PrimeKG paths checked",
        "- [ ] Generated claims checked",
        "- [ ] Citations checked",
        "- [ ] Biomedical expert review completed",
    ]
    return f"""# {row['drug_name']} - {row['disease_name']}

## 1. Case Metadata

- pair_id: `{pair_id}`
- drug: {row['drug_name']}
- disease: {row['disease_name']}
- repoDB label: `{row['expected_label']}`
- full pipeline prediction: `{row['full_predicted_label']}`
- full confidence score: {fmt(row['full_confidence_score'])}
- full status: `{row['full_status']}`
- case type: `{row['case_type']}`
- manual review status: `{row['manual_review_status']}`

## 2. Why This Case Was Selected

{row['selection_reason']} The case is included for manual review, not as a definitive biomedical conclusion.

## 3. Evidence Summary

### 3.1 PubMed Evidence

- PMIDs available in PubMed baseline: {fmt(row['n_unique_pmids_available'])}
- PMIDs used by full pipeline: {fmt(row['n_pmids_used'])}
- Abstract availability rate from baseline: {fmt(unified.get('abstract_available_rate'))}

Top available PMID/title rows:

{pubmed_lines(top_pubmed)}

The literature signal should be interpreted as co-mention and retrieved-document support. It does not establish efficacy.

### 3.2 Open Targets Evidence

- drug resolved: {fmt_bool(ot.get('drug_resolved'))}
- disease resolved: {fmt_bool(ot.get('disease_resolved'))}
- disease targets: {fmt(ot.get('n_disease_targets'))}
- drug targets: {fmt(ot.get('n_drug_targets'))}
- overlapping targets: {fmt(ot.get('n_overlapping_targets'))}
- support score: {fmt(ot.get('opentargets_support_score'))}

Open Targets support is target-evidence context, not clinical truth.

### 3.3 PrimeKG Graph Evidence

- drug mapped: {fmt_bool(graph.get('drug_mapped'))}
- disease mapped: {fmt_bool(graph.get('disease_mapped'))}
- graph path exists: {fmt_bool(graph.get('has_path'))}
- shortest path length: {fmt(graph.get('shortest_path_length'))}
- graph connectivity score: {fmt(graph.get('graph_connectivity_score'))}

Graph paths:

{path_lines}

PrimeKG connectivity is mechanism support only and does not prove efficacy.

### 3.4 Full-Agent Generated Report

{report_summary}

### 3.5 Claim Verification

- claims: {fmt(row['n_claims'])}
- verified claims: {fmt(row['n_verified_claims'])}
- unsupported claims: {fmt(row['n_unsupported_claims'])}
- citation verified rate: {fmt(row['citation_verified_rate'])}
- unsupported claim rate: {fmt(row['unsupported_claim_rate'])}

Claim examples:

{claim_lines}

## 4. Manual Interpretation

The available evidence suggests a research-support assessment only. The retrieved literature and structured evidence may be consistent with the full-agent assessment, but this case does not establish efficacy, safety, or clinical utility. Any apparent alignment or mismatch with the repoDB proxy label requires expert review of the original repoDB row, PubMed abstracts, Open Targets mappings, and graph paths.

## 5. Error Analysis Or Reliability Analysis

This case is useful for `{row['case_type']}`. It shows how OrphanCure preserves provenance, exposes missing evidence, and separates report faithfulness from repoDB label prediction. If the prediction is incorrect or partial, the case should be used to study failure modes rather than to claim biomedical validity.

## 6. Interview Talking Points

- 30-second explanation: This case shows how OrphanCure turns a drug-disease pair into a traceable evidence report with PubMed, Open Targets, graph, and verifier outputs.
- 2-minute explanation: Discuss the repoDB proxy label, what evidence layers were available, whether the generated claims were verified, and why this does or does not align with the label.
- Technical takeaway: The case keeps `pair_id`, evidence availability, claims, and verification status tied together.
- Limitation: Evidence grounding is not the same as clinical validation.

## 7. Safety Note

{DISCLAIMER}

## 8. Manual Review Checklist

{chr(10).join(checklist)}
"""


def render_english_summary(selected: pd.DataFrame) -> str:
    rows = "\n".join(
        f"| `{r.pair_id}` | {r.drug_name} | {r.disease_name} | `{r.case_type}` | `{r.full_status}` | `{r.manual_review_status}` |"
        for r in selected.itertuples()
    )
    return f"""# OrphanCure Case Studies

These case studies were selected from the completed 20-pair full-agent run.
They are manually reviewable research artifacts, not clinical recommendations.

## Selected Cases

| pair_id | Drug | Disease | Case Type | Status | Manual Review |
|---|---|---|---|---|---|
{rows}

## What These Cases Demonstrate

- Evidence provenance can be inspected across PubMed, Open Targets, PrimeKG, and generated claims.
- The verifier reduces unsupported claims compared with `no_verifier`.
- Incorrect and partial-success cases are useful for understanding limitations.

## What These Cases Do Not Demonstrate

- They do not prove drug efficacy.
- They do not validate clinical use.
- They do not replace biomedical expert review.

## Safety Disclaimer

{DISCLAIMER}
"""


def render_chinese_summary(selected: pd.DataFrame) -> str:
    bullet_rows = "\n".join(
        f"- `{r.pair_id}`：{r.drug_name} / {r.disease_name}，类型 `{r.case_type}`，状态 `{r.full_status}`。"
        for r in selected.itertuples()
    )
    return f"""# OrphanCure Case Studies 中文面试说明

## 为什么选择这些案例

这些案例来自 20-pair full-agent run，覆盖 correct positive、correct negative_or_failed、
verifier effect、incorrect but informative，以及 partial_success error analysis。它们的目的
不是证明药物有效，而是展示系统如何保留证据、claims、PMID、Open Targets/PrimeKG 特征和
verification status。

## 选中案例

{bullet_rows}

## 面试中怎么讲 verifier effect

可以说：`no_verifier` 的 unsupported claim rate 明显更高，而 full mode 会把 claim 和
retrieved PubMed abstracts 做 citation verification。这个模块不一定提高 repoDB label
accuracy，但可以提高 report faithfulness，降低 unsupported claims。

## 为什么 full pipeline accuracy 不高

repoDB label 是 approved/failed proxy label，不等于机制证据真假。失败试验也可能有机制证据，
approved indication 也可能缺少 Open Targets overlap 或图路径。因此 full pipeline 当前更像
evidence-grounded report generator，而不是 validated clinical predictor。

## 这个项目是不是 LLM wrapper?

不是。LLM 只是 synthesis/report 组件。项目核心是 benchmark、真实数据集成、PubMed/OT/PrimeKG
多证据层、ablation、verifier、failure accounting 和 manual review workflow。

## 医学安全边界

{DISCLAIMER}

所有 case 的 biomedical expert review 默认仍是未完成状态。
"""


def first_row(df: pd.DataFrame, pair_id: str) -> dict[str, Any]:
    if df.empty or "pair_id" not in df.columns:
        return {}
    rows = df[df["pair_id"].astype(str) == str(pair_id)]
    return rows.iloc[0].to_dict() if not rows.empty else {}


def load_raw(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def report_excerpt(raw: dict[str, Any]) -> str:
    report = raw.get("structured_report") or {}
    sections = report.get("sections") or {}
    exec_summary = (sections.get("1_executive_summary") or {}).get("summary")
    conclusion = raw.get("final_assessment") or (sections.get("1_executive_summary") or {}).get("conclusion")
    if not exec_summary and not conclusion:
        return "No complete full-agent report was generated for this case."
    return f"Conclusion field: `{conclusion}`. Short summary: {shorten(str(exec_summary or 'No executive summary available.'), 600)}"


def claim_summary_lines(claims: list[dict[str, Any]]) -> str:
    if not claims:
        return "- No generated claims available."
    lines = []
    for claim in claims[:5]:
        statement = shorten(str(claim.get("statement", "")), 240)
        status = claim.get("verification_status", "")
        pmids = []
        for ev in (claim.get("provenance") or {}).get("paper_evidence", []) or []:
            if isinstance(ev, dict) and ev.get("pmid"):
                pmids.append(str(ev["pmid"]))
        lines.append(f"- `{status}` claim: {statement} PMIDs: {', '.join(pmids[:5]) if pmids else 'none listed'}")
    return "\n".join(lines)


def pubmed_lines(df: pd.DataFrame) -> str:
    if df.empty:
        return "- No PubMed evidence rows available in local outputs."
    lines = []
    for _, row in df.iterrows():
        lines.append(f"- PMID `{fmt(row.get('pmid'))}` ({fmt(row.get('publication_year'))}): {shorten(str(row.get('title', '')), 160)}")
    return "\n".join(lines)


def graph_path_lines(df: pd.DataFrame) -> str:
    if df.empty:
        return "- No graph path rows available for this pair."
    columns = [c for c in ["path_length", "path_node_names", "path_relations"] if c in df.columns]
    lines = []
    for _, row in df.head(5).iterrows():
        details = "; ".join(f"{col}: {row.get(col)}" for col in columns)
        lines.append(f"- {shorten(details, 220)}")
    return "\n".join(lines)


def to_float(value: Any) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fmt(value: Any) -> str:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return "not available"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def fmt_bool(value: Any) -> str:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return "not available"
    return "yes" if str(value).strip().lower() in {"true", "1", "yes"} else "no"


def shorten(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."


if __name__ == "__main__":
    raise SystemExit(main())
