"""Structured scientific report builder — 11-section output."""

from __future__ import annotations

from typing import Dict, List

from app.models.claims import Claim
from app.models.evidence import EvidencePolarity, VerificationStatus
from app.models.state import UnifiedRunState


class ReportBuilder:
    """
    Builds the final structured scientific report from the unified run state.

    Required sections:
    1.  Executive Summary
    2.  Normalized Hypothesis
    3.  Mechanistic Rationale
    4.  Target Overlap Summary
    5.  Literature Evidence Summary
    6.  Contradictory / Negative Evidence
    7.  Confidence Assessment
    8.  Risk Flags / Limitations
    9.  Recommended Next Steps
    10. Claim-by-Claim Evidence Table
    11. Provenance Appendix
    """

    def __init__(self, state: UnifiedRunState):
        self.state = state

    def build(self) -> Dict:
        """Build the complete structured report."""
        claims = self.state.verified_claims or self.state.draft_claims
        report = self.state.final_report or {}

        return {
            "sections": {
                "1_executive_summary": self._executive_summary(report),
                "2_normalized_hypothesis": self._normalized_hypothesis(),
                "3_mechanistic_rationale": self._mechanistic_rationale(),
                "4_target_overlap_summary": self._target_overlap_summary(),
                "5_literature_evidence_summary": self._literature_evidence_summary(),
                "6_contradictory_evidence": self._contradictory_evidence(claims),
                "7_confidence_assessment": self._confidence_assessment(report),
                "8_risk_flags_limitations": self._risk_flags(report, claims),
                "9_recommended_next_steps": self._next_steps(report),
                "10_claim_evidence_table": self._claim_table(claims),
                "11_provenance_appendix": self._provenance_appendix(claims),
            },
            "metadata": {
                "run_id": self.state.run_id,
                "created_at": self.state.created_at,
                "drug": self.state.drug_entity.name if self.state.drug_entity else "",
                "disease": self.state.disease_entity.name if self.state.disease_entity else "",
                "total_claims": len(claims),
                "quality_score": self.state.scorecard.overall_score,
                "reruns": len(self.state.rerun_history),
            },
        }

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _executive_summary(self, report: Dict) -> Dict:
        conclusion = report.get("conclusion", "N/A")
        confidence = report.get("overall_confidence", "N/A")
        exec_sum = report.get("executive_summary", "")

        matrix = self.state.evidence_matrix
        return {
            "conclusion": conclusion,
            "confidence": confidence,
            "summary": exec_sum,
            "evidence_counts": {
                "total_papers": matrix.total_retrieved,
                "supporting": matrix.supports,
                "contradicting": matrix.contradicts,
                "inconclusive": matrix.inconclusive,
            },
            "common_targets_count": len(self.state.common_targets),
        }

    def _normalized_hypothesis(self) -> Dict:
        drug = self.state.drug_entity
        disease = self.state.disease_entity
        return {
            "statement": f"Repurpose {drug.name if drug else '?'} for {disease.name if disease else '?'}",
            "drug": {
                "id": drug.id if drug else "",
                "name": drug.name if drug else "",
                "aliases": drug.aliases.aliases if drug and drug.aliases else [],
                "resolution_method": drug.source_method if drug else "",
            },
            "disease": {
                "id": disease.id if disease else "",
                "name": disease.name if disease else "",
                "aliases": disease.aliases.aliases if disease and disease.aliases else [],
                "resolution_method": disease.source_method if disease else "",
            },
        }

    def _mechanistic_rationale(self) -> Dict:
        mech_evidence = self.state.mechanism_evidence
        entries = []
        for me in mech_evidence:
            entries.append({
                "target": me.target_symbol,
                "drug_action": me.drug_action,
                "disease_score": round(me.disease_assoc_score, 3),
                "pathway": me.pathway_summary or "Not available",
            })
        return {
            "total_mechanisms": len(entries),
            "mechanisms": entries,
        }

    def _target_overlap_summary(self) -> Dict:
        targets = self.state.common_targets
        return {
            "total_overlapping": len(targets),
            "top_targets": [
                {
                    "symbol": t.symbol,
                    "name": t.name,
                    "drug_action": t.drug_action,
                    "disease_association_score": round(t.disease_assoc_score, 3),
                }
                for t in targets[:15]
            ],
        }

    def _literature_evidence_summary(self) -> Dict:
        matrix = self.state.evidence_matrix
        papers = self.state.papers
        return {
            "total_retrieved": matrix.total_retrieved,
            "polarity": {
                "supports": matrix.supports,
                "contradicts": matrix.contradicts,
                "inconclusive": matrix.inconclusive,
            },
            "support_ratio": f"{matrix.supports} of {matrix.total_retrieved} retrieved papers support the hypothesis"
            if matrix.total_retrieved > 0 else "No papers retrieved",
            "queries_used": len(self.state.retrieval_queries),
            "top_papers": [
                {
                    "pmid": p.pmid,
                    "title": p.title,
                    "year": p.year,
                    "relevance_score": round(p.relevance_score, 2),
                    "polarity": p.polarity.value,
                    "match_reasons": p.match_reasons,
                }
                for p in papers[:10]
            ],
        }

    def _contradictory_evidence(self, claims: List[Claim]) -> Dict:
        contra_claims = [
            c for c in claims if c.polarity == EvidencePolarity.CONTRADICTS
        ]
        return {
            "count": len(contra_claims),
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "statement": c.statement,
                    "evidence_count": len(c.provenance.paper_evidence),
                }
                for c in contra_claims
            ],
        }

    def _confidence_assessment(self, report: Dict) -> Dict:
        assessment = report.get("confidence_assessment", {})
        return {
            "overall": report.get("overall_confidence", "N/A"),
            "dimensions": assessment,
            "quality_scorecard": self.state.scorecard.to_summary_dict(),
        }

    def _risk_flags(self, report: Dict, claims: List[Claim]) -> Dict:
        flags = list(report.get("risk_flags", []))
        limitations = list(report.get("limitations", []))

        # Add claim-level risks
        for c in claims:
            flags.extend(c.risk_flags)

        return {
            "risk_flags": list(set(flags)),
            "limitations": limitations,
            "missing_data": report.get("missing_data", []),
        }

    def _next_steps(self, report: Dict) -> Dict:
        return {
            "clinical_next_steps": report.get("clinical_next_steps", []),
        }

    def _claim_table(self, claims: List[Claim]) -> Dict:
        rows = []
        for c in claims:
            rows.append({
                "claim_id": c.claim_id,
                "statement": c.statement,
                "confidence_numeric": round(c.confidence_numeric, 2),
                "confidence_label": c.confidence_label,
                "polarity": c.polarity.value,
                "verification_status": c.verification_status.value,
                "targets": c.supported_targets,
                "citation_count": len(c.provenance.paper_evidence),
                "risk_flags": c.risk_flags,
            })
        return {
            "total_claims": len(rows),
            "claims": rows,
        }

    def _provenance_appendix(self, claims: List[Claim]) -> Dict:
        entries = []
        for c in claims:
            prov = c.provenance
            entries.append({
                "claim_id": c.claim_id,
                "source_agent": prov.source_agent,
                "source_run": prov.source_run,
                "timestamp": prov.timestamp,
                "paper_evidence": [
                    {
                        "pmid": pe.pmid,
                        "snippet": pe.evidence_snippet[:200],
                        "polarity": pe.polarity.value,
                        "verification": pe.verification_status.value,
                        "error": pe.verification_error,
                    }
                    for pe in prov.paper_evidence
                ],
                "mechanism_evidence": [
                    {"target": me.target_symbol, "action": me.drug_action}
                    for me in prov.mechanism_evidence
                ],
                "queries_used_count": len(prov.retrieval_queries_used),
            })
        return {
            "total_entries": len(entries),
            "entries": entries,
        }
