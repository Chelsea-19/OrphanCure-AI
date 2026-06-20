"""RankerAgent — transparent multi-factor candidate ranking."""

from __future__ import annotations

from typing import List

from app.agents.base import BaseAgent
from app.models.entities import CandidateDrug, RankingBreakdown


class RankerAgent(BaseAgent):
    """
    Responsibilities:
    - Receive generated candidate list.
    - Apply publishable multi-factor scoring (mechanism, evidence, safety, readiness).
    - Determine translational contradiction burden.
    - Apply composite expert score.
    - Assign transparent priority tiers.
    """

    name = "RankerAgent"

    def execute(self) -> None:
        self.log(f"Starting explicit multi-factor ranking for {len(self.state.generated_candidates)} candidates.")

        if not self.state.generated_candidates:
            self.log("No candidates available to rank.")
            return

        # Prevent giant loop timeouts if OpenTargets returned 50. Let's rank top 10 heuristically chosen candidates.
        # Or, just batched. For Phase 3, we rank the top 5 candidates.
        batch = self.state.generated_candidates[:5]

        for cand in batch:
            if self.llm.enabled:
                self._rank_with_llm(cand)
            else:
                self._rank_heuristic(cand)
                
        # Move unranked below ranked
        for cand in self.state.generated_candidates[5:]:
            cand.priority_class = "Unranked"

        # Resort ONLY the batch based on computed deep score
        batch.sort(key=lambda c: c.score, reverse=True)
        self.state.generated_candidates = batch + self.state.generated_candidates[5:]
        
        self.state.log("RankerAgent", "Multifactor ranking complete.")

    def _rank_with_llm(self, candidate: CandidateDrug) -> None:
        """Deep specialized LLM reasoning for published-tier transparent matrices."""
        sys_prompt = (
            "You are an expert computational biologist evaluating a drug for rare disease repurposing. "
            "Output JSON utilizing strict floating point metrics (0.0 to 10.0)."
        )
        disease_name = self.state.disease_entity.name if self.state.disease_entity else "Disease"
        
        user_prompt = f"""
Drug Candidate: {candidate.name}
Target Disease: {disease_name}
Recorded Mechanism / Source: {candidate.mechanism_category}
Provenance ID: {candidate.provenance[0].source_id if candidate.provenance else 'Unknown'}

Analyze this candidate's repurposing potential. Assign critical scores:
1. mechanism_fit (0-10): How biologically plausible is the alignment between drug target and disease pathway?
2. evidence_strength (0-10): Proxy for expected literature support quality.
3. safety_feasibility (0-10): Likelihood of tolerability in the given rare disease population.
4. contradiction_burden (0-10): 10 = massive contraindications/missed endpoints, 0 = no known opposing evidence.
5. translational_readiness (0-10): Ease of getting to clinical trials.
6. rationale: A single sentence specialized justification.
7. priority_class: "Tier 1", "Tier 2", or "Tier 3".
8. gaps: List of strings (e.g. "Requires in vivo efficacy validation").

Output Schema:
{{
  "mechanism_fit": 5.0,
  "evidence_strength": 3.0,
  "safety_feasibility": 8.0,
  "contradiction_burden": 1.0,
  "translational_readiness": 4.0,
  "rationale": "...",
  "priority_class": "Tier 2",
  "gaps": ["gap 1"]
}}
"""
        res = self.llm.generate(sys_prompt, user_prompt, json_mode=True)
        if "error" not in res:
            try:
                fit = float(res.get("mechanism_fit", 3.0))
                evid = float(res.get("evidence_strength", 3.0))
                safety = float(res.get("safety_feasibility", 5.0))
                contra = float(res.get("contradiction_burden", 5.0))
                readiness = float(res.get("translational_readiness", 3.0))
                
                candidate.ranking_breakdown = RankingBreakdown(
                    mechanism_fit=fit,
                    evidence_strength=evid,
                    safety_feasibility=safety,
                    contradiction_burden=contra,
                    translational_readiness=readiness
                )
                candidate.rationale = res.get("rationale", "")
                candidate.priority_class = res.get("priority_class", "Tier 3")
                candidate.evidence_gaps = res.get("gaps", [])
                
                # Expert Composite Matrix: 
                # Heavy weight on fit and evidence, penalty on contradiction.
                composite = (fit * 2.0) + (evid * 2.5) + (safety * 1.5) + (readiness * 1.0) - (contra * 2.0)
                candidate.score = max(0.0, composite)
                
            except Exception as e:
                self.log(f"Error parsing ranking for {candidate.name}: {e}", "WARN")

    def _rank_heuristic(self, candidate: CandidateDrug) -> None:
        candidate.ranking_breakdown = RankingBreakdown(mechanism_fit=5.0)
        candidate.score = 5.0
        candidate.priority_class = "Tier 3"
        candidate.rationale = "Heuristic baseline."
