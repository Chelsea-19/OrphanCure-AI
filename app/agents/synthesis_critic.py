"""SynthesisCriticAgent — combined synthesis + critique for structured report generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.base import BaseAgent
from app.models.claims import Claim, ClaimEvidenceBundle
from app.models.entities import TargetInfo
from app.models.evidence import (
    EvidencePolarity,
    MechanismEvidence,
    Paper,
    PaperEvidence,
    VerificationStatus,
)
from app.models.scorecard import QualityScorecard


class SynthesisCriticAgent(BaseAgent):
    """
    Combined synthesis + critic agent (v1).

    Responsibilities:
    - Generate claim-level outputs (not just a narrative)
    - Attach provenance bundles to each claim
    - Run a quality scorecard
    - Request targeted reruns if quality is insufficient
    - Only finalize if threshold is met
    """

    name = "SynthesisCriticAgent"

    def execute(self) -> None:
        self.log("Starting synthesis + critique")

        if not self.state.drug_entity or not self.state.disease_entity:
            self.log("Cannot synthesise — entities not resolved", "ERROR")
            return

        # 1. Generate claims via LLM
        raw_report = self._call_synthesis_llm()

        if not isinstance(raw_report, dict):
            self.state.final_report = {
                "error": "LLM synthesis returned a non-object response",
                "raw_response_type": type(raw_report).__name__,
            }
            self.log("LLM synthesis returned a non-object response", "ERROR")
            return

        if "error" in raw_report:
            self.state.final_report = {"error": raw_report["error"]}
            self.log(f"LLM synthesis error: {raw_report['error']}", "ERROR")
            return

        # 2. Build Claim objects with provenance
        claims = self._build_claims(raw_report)
        self.state.draft_claims = claims

        # 3. Store the raw LLM report
        self.state.final_report = raw_report

        # 4. Quality scorecard
        scorecard = self._score_quality(raw_report, claims)
        self.state.scorecard = scorecard

        self.log(
            f"Synthesis complete — {len(claims)} claims, "
            f"quality={scorecard.overall_score:.2f}, decision={scorecard.decision}"
        )

    # ------------------------------------------------------------------
    # LLM synthesis call (evolved from app6.py synthesize_report_strict)
    # ------------------------------------------------------------------

    def _call_synthesis_llm(self) -> Dict:
        drug = self.state.drug_entity.name
        disease = self.state.disease_entity.name
        targets = self.state.common_targets
        papers = self.state.papers

        t_str = ", ".join(t.symbol for t in targets[:10])

        p_str = ""
        for p in papers[:8]:
            p_str += f"[PaperID: {p.pmid}] Title: {p.title}\n"
            if p.abstract:
                p_str += f"Abstract Snippet: {p.abstract[:800]}...\n\n"

        # Mechanism evidence context
        mech_str = ""
        for me in self.state.mechanism_evidence[:10]:
            mech_str += f"- {me.target_symbol}: {me.drug_action} (disease score: {me.disease_assoc_score:.2f})"
            if me.pathway_summary:
                mech_str += f" — {me.pathway_summary}"
            mech_str += "\n"

        evidence_matrix = self.state.evidence_matrix

        sys_prompt = """You are a Senior Pharmacologist Agent performing rigorous drug repurposing analysis.
Your goal is to validate a hypothesis based strictly on the provided data.

CRITICAL RULES:
1. When citing evidence, extract the EXACT substring from the provided abstract.
2. Do NOT paraphrase quotes significantly.
3. Every claim must reference specific PMIDs.
4. Include contradictory evidence if found.
5. Be conservative — do not overstate certainty."""

        user_prompt = f"""
Hypothesis: Repurpose {drug} for {disease}.

MECHANISM DATA:
Common Targets: {t_str}
Mechanism Details:
{mech_str}

EVIDENCE SUMMARY:
- {evidence_matrix.total_retrieved} papers retrieved
- {evidence_matrix.supports} supporting, {evidence_matrix.contradicts} contradicting, {evidence_matrix.inconclusive} inconclusive

LITERATURE:
{p_str}

OUTPUT JSON (Strict Schema):
{{
  "conclusion": "Valid|Potential|Unlikely",
  "overall_confidence": "High|Medium|Low",
  "executive_summary": "2-3 sentence summary",
  "key_mechanisms": [
    {{
      "claim": "Scientific claim statement",
      "supported_targets": ["TargetSymbol"],
      "supported_papers": [
        {{ "pmid": "PaperID", "evidence_snippet": "Quote from abstract (<200 chars)", "polarity": "SUPPORTS|CONTRADICTS|INCONCLUSIVE" }}
      ],
      "confidence": 0.8
    }}
  ],
  "contradictory_evidence": [
    {{
      "claim": "Contradictory finding",
      "supported_papers": [
        {{ "pmid": "PaperID", "evidence_snippet": "Quote" }}
      ]
    }}
  ],
  "confidence_assessment": {{
    "mechanistic_strength": "High|Medium|Low",
    "literature_strength": "High|Medium|Low",
    "clinical_evidence": "High|Medium|Low"
  }},
  "clinical_next_steps": ["string"],
  "missing_data": ["string"],
  "risk_flags": ["string"],
  "limitations": ["string"]
}}
"""
        return self.llm.generate(sys_prompt, user_prompt, json_mode=True, temperature=0.1)

    # ------------------------------------------------------------------
    # Claim builder with provenance
    # ------------------------------------------------------------------

    def _build_claims(self, report: Dict) -> List[Claim]:
        claims: List[Claim] = []
        ts = datetime.now(timezone.utc).isoformat()

        for i, mech in enumerate(self._dict_items(report.get("key_mechanisms"), "key_mechanisms")):
            claim_id = f"CLM-{uuid.uuid4().hex[:6]}"

            # Build paper evidence
            paper_ev = []
            for ref in self._dict_items(mech.get("supported_papers"), f"key_mechanisms[{i}].supported_papers"):
                polarity_str = ref.get("polarity", "INCONCLUSIVE")
                try:
                    polarity = EvidencePolarity(polarity_str)
                except ValueError:
                    polarity = EvidencePolarity.INCONCLUSIVE

                paper_ev.append(
                    PaperEvidence(
                        pmid=ref.get("pmid", ""),
                        evidence_snippet=ref.get("evidence_snippet", ""),
                        polarity=polarity,
                    )
                )

            # Map supported targets to mechanism evidence
            mech_ev = []
            supported_targets = self._string_items(mech.get("supported_targets"), f"key_mechanisms[{i}].supported_targets")
            for sym in supported_targets:
                for me in self.state.mechanism_evidence:
                    if me.target_symbol == sym:
                        mech_ev.append(me)

            # Retrieval query strings
            query_strings = [q.query_string for q in self.state.retrieval_queries]

            bundle = ClaimEvidenceBundle(
                paper_evidence=paper_ev,
                mechanism_evidence=mech_ev,
                retrieval_queries_used=query_strings,
                source_agent=self.name,
                source_run=self.state.run_id,
                timestamp=ts,
            )

            confidence = self._coerce_confidence(mech.get("confidence", 0.0))
            claim = Claim(
                claim_id=claim_id,
                statement=mech.get("claim", ""),
                confidence_numeric=confidence,
                supported_targets=supported_targets,
                provenance=bundle,
            )
            claim.compute_confidence_label()
            claims.append(claim)

        # Contradictory claims
        for i, contra in enumerate(self._dict_items(report.get("contradictory_evidence"), "contradictory_evidence")):
            claim_id = f"CTR-{uuid.uuid4().hex[:6]}"
            paper_ev = [
                PaperEvidence(
                    pmid=ref.get("pmid", ""),
                    evidence_snippet=ref.get("evidence_snippet", ""),
                    polarity=EvidencePolarity.CONTRADICTS,
                )
                for ref in self._dict_items(contra.get("supported_papers"), f"contradictory_evidence[{i}].supported_papers")
            ]

            bundle = ClaimEvidenceBundle(
                paper_evidence=paper_ev,
                source_agent=self.name,
                source_run=self.state.run_id,
                timestamp=ts,
            )

            claim = Claim(
                claim_id=claim_id,
                statement=contra.get("claim", ""),
                confidence_numeric=0.5,
                polarity=EvidencePolarity.CONTRADICTS,
                provenance=bundle,
            )
            claim.compute_confidence_label()
            claims.append(claim)

        return claims

    def _dict_items(self, value: Any, field_name: str) -> List[Dict]:
        """Return only dict items from a list-like LLM field."""
        if value is None:
            return []
        if isinstance(value, dict):
            return [value]
        if not isinstance(value, list):
            self.log(f"Malformed synthesis field {field_name}: expected list", "WARN")
            return []
        items = []
        skipped = 0
        for item in value:
            if isinstance(item, dict):
                items.append(item)
            else:
                skipped += 1
        if skipped:
            self.log(f"Skipped {skipped} malformed item(s) in {field_name}", "WARN")
        return items

    def _string_items(self, value: Any, field_name: str) -> List[str]:
        """Return stringified non-empty values from an LLM list field."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value else []
        if not isinstance(value, list):
            self.log(f"Malformed synthesis field {field_name}: expected list", "WARN")
            return []
        return [str(item) for item in value if item]

    def _coerce_confidence(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    # ------------------------------------------------------------------
    # Quality scorecard
    # ------------------------------------------------------------------

    def _score_quality(self, report: Dict, claims: List[Claim]) -> QualityScorecard:
        sc = QualityScorecard.create_default()

        # Completeness — does the report have all expected sections?
        expected_keys = ["conclusion", "overall_confidence", "key_mechanisms",
                         "clinical_next_steps", "risk_flags"]
        present = sum(1 for k in expected_keys if report.get(k))
        sc.set_dimension("completeness", present / len(expected_keys),
                         f"{present}/{len(expected_keys)} sections present")

        # Evidence support
        if claims:
            supported = sum(1 for c in claims if c.provenance.paper_evidence)
            sc.set_dimension("evidence_support", supported / len(claims),
                             f"{supported}/{len(claims)} claims have paper evidence")
        else:
            sc.set_dimension("evidence_support", 0.0, "No claims generated")

        # Citation validity (pre-verification — checked later by verifier)
        total_refs = sum(len(c.provenance.paper_evidence) for c in claims)
        sc.set_dimension("citation_validity", min(total_refs / max(len(claims), 1), 1.0),
                         f"{total_refs} total citations")

        # Mechanistic specificity
        mech_claims = [c for c in claims if c.supported_targets]
        sc.set_dimension("mechanistic_specificity",
                         len(mech_claims) / max(len(claims), 1),
                         f"{len(mech_claims)}/{len(claims)} claims reference targets")

        # Contradiction handling
        has_contra = bool(report.get("contradictory_evidence"))
        sc.set_dimension("contradiction_handling",
                         0.8 if has_contra else 0.3,
                         "Contradictory evidence discussed" if has_contra else "No contradiction analysis")

        # Traceability
        traced = sum(1 for c in claims if c.provenance.paper_evidence or c.provenance.mechanism_evidence)
        sc.set_dimension("traceability", traced / max(len(claims), 1),
                         f"{traced}/{len(claims)} claims have provenance")

        # Output structure
        has_exec = bool(report.get("executive_summary"))
        has_conf = bool(report.get("confidence_assessment"))
        struct_score = (0.5 if has_exec else 0.0) + (0.5 if has_conf else 0.0)
        sc.set_dimension("output_structure", struct_score,
                         "Executive summary + confidence assessment")

        # Actionability
        steps = report.get("clinical_next_steps") or []
        missing = report.get("missing_data") or []
        sc.set_dimension("actionability",
                         min((len(steps) + len(missing)) / 4, 1.0),
                         f"{len(steps)} next steps, {len(missing)} data gaps identified")

        sc.make_decision(self.settings.quality_threshold)
        return sc
