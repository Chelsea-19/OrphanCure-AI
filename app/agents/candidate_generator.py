"""CandidateGeneratorAgent — discovers and expands candidate drugs for a disease."""

from __future__ import annotations

from typing import List

from app.agents.base import BaseAgent
from app.models.entities import CandidateDrug, ProvenanceSource
from app.services.opentargets import OpenTargetsService


class CandidateGeneratorAgent(BaseAgent):
    """
    Responsibilities:
    - Receive a normalized disease (or gene/phenotype).
    - Query sources (OpenTargets, etc.) for known associated drugs.
    - Query sources for drugs targeting associated pathways/genes.
    - Deduplicate and normalize candidates.
    - Attach source provenance and initial confidence scores.
    """

    name = "CandidateGeneratorAgent"

    def __init__(self, state, llm, settings):
        super().__init__(state, llm, settings)
        self._ot = OpenTargetsService(settings)

    def execute(self) -> None:
        self.log(f"Starting candidate generation for disease: {self.state.disease_entity.name}")

        if self.state.input_mode == "drug_and_disease":
            # If a specific drug was already provided, we just wrap it as a candidate.
            if self.state.drug_entity:
                candidate = CandidateDrug(
                    id=self.state.drug_entity.id,
                    name=self.state.drug_entity.name,
                    mechanism_category="User input",
                    provenance=[
                        ProvenanceSource(
                            source_type="user",
                            source_id="input",
                            confidence=1.0,
                            rationale="Provided explicitly by user."
                        )
                    ],
                    score=1.0
                )
                self.state.generated_candidates = [candidate]
                self.log(f"Wrapped user-provided drug into candidates list: {candidate.name}")
            return

        # Disease-only mode: Fetch candidates from OpenTargets or other sources
        # TODO: Implement full OpenTargets candidate fetch logic.
        # For now, we stub this out to demonstrate the module structure.
        
        candidates = self._fetch_candidates_for_disease(self.state.disease_entity.id)
        
        self.state.generated_candidates = candidates
        self.log(f"Candidate generation complete. Found {len(candidates)} candidates.")

    def _fetch_candidates_for_disease(self, disease_id: str) -> List[CandidateDrug]:
        """Fetch candidates leveraging disease associations from OpenTargets."""
        known_drugs = self._ot.get_disease_known_drugs(disease_id)
        candidates = []
        seen = set()
        
        for row in known_drugs:
            drug_info = row.get("drug", {})
            drug_id = drug_info.get("id")
            drug_name = drug_info.get("name")
            
            if not drug_id or not drug_name or drug_id in seen:
                continue
                
            seen.add(drug_id)
            candidates.append(
                CandidateDrug(
                    id=drug_id,
                    name=drug_name,
                    mechanism_category="Known Association",
                    provenance=[
                        ProvenanceSource(
                            source_type="opentargets", 
                            source_id=f"known_drug:{disease_id}",
                            confidence=0.9,
                            rationale="Historically associated or indicated in OpenTargets."
                        )
                    ],
                    score=0.8
                )
            )
            
        return candidates
