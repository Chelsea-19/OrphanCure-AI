"""EntityResolutionAgent — normalize and disambiguate drug / disease terms."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.entities import AliasExpansion, Entity, EntityCandidate
from app.services.opentargets import OpenTargetsService


class EntityResolutionAgent(BaseAgent):
    """
    Responsibilities:
    - Search OpenTargets for candidate entities
    - LLM-assisted correction when search fails or is ambiguous
    - Auto-select when confidence is high
    - Create synonym/alias expansion objects for downstream retrieval
    - Produce structured confidence scores
    """

    name = "EntityResolutionAgent"

    def __init__(self, state, llm, settings):
        super().__init__(state, llm, settings)
        self._ot = OpenTargetsService(settings)

    def execute(self) -> None:
        self.log("Starting entity resolution")

        # --- Drug (if applicable) ---
        if self.state.input_mode == "drug_and_disease" and self.state.drug_input:
            self.state.drug_candidates = self._resolve_term(
                self.state.drug_input, "drug"
            )
            drug_entity = self._auto_select(
                self.state.drug_candidates, "drug", self.state.drug_input
            )
            self.state.drug_entity = drug_entity

        # --- Disease ---
        if self.state.disease_input:
            self.state.disease_candidates = self._resolve_term(
                self.state.disease_input, "disease"
            )
            disease_entity = self._auto_select(
                self.state.disease_candidates, "disease", self.state.disease_input
            )
            self.state.disease_entity = disease_entity

        if self.state.input_mode == "drug_and_disease":
            if self.state.drug_entity and self.state.disease_entity:
                self.state.stage = "analysis"
                self.log(
                    f"Auto-resolved: {self.state.drug_entity.name} & "
                    f"{self.state.disease_entity.name}"
                )
            else:
                self.state.stage = "resolution"
                self.log("Ambiguous entities — manual resolution required", "WARN")
        else:
            # Disease only
            if self.state.disease_entity:
                self.state.stage = "analysis"
                self.log(f"Auto-resolved Disease: {self.state.disease_entity.name}")
            else:
                self.state.stage = "resolution"
                self.log("Ambiguous disease entity — manual resolution required", "WARN")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_term(self, term: str, entity_type: str) -> list[EntityCandidate]:
        """Search OT, fall back to LLM correction if needed."""
        hits = self._ot.search_candidates(term, entity_type)

        if not hits and self.llm.enabled:
            corrected = self._llm_correct(term, entity_type)
            if corrected and corrected.lower() != term.lower():
                self.log(f"LLM corrected '{term}' → '{corrected}'")
                hits = self._ot.search_candidates(corrected, entity_type)

        return hits

    def _llm_correct(self, term: str, entity_type: str) -> str | None:
        """Use LLM to suggest a corrected term."""
        sys_prompt = (
            "You are a biomedical terminologist. "
            "Check the input term for typos/synonyms. Output JSON."
        )
        user_prompt = f"""
Input: "{term}" (Type: {entity_type})
Task:
1. Identify standard medical name (e.g., 'Metformn' -> 'Metformin').
2. Provide confidence (0.0 to 1.0).
3. Explain rationale.

Output Schema:
{{
    "correction": "Standard Name or Original if correct",
    "confidence": 0.9,
    "rationale": "Reasoning..."
}}
"""
        result = self.llm.generate(sys_prompt, user_prompt, json_mode=True)
        if "error" not in result and result.get("confidence", 0) > 0.7:
            return result.get("correction")
        return None

    def _auto_select(
        self, candidates: list[EntityCandidate], entity_type: str, original_term: str
    ) -> Entity | None:
        """Auto-select if single candidate or high-confidence top hit."""
        if not candidates:
            return None

        th_score = self.settings.resolution_min_score
        th_delta = self.settings.resolution_min_delta

        auto = False
        if len(candidates) == 1:
            auto = True
        elif candidates[0].score > th_score:
            delta = candidates[0].score - candidates[1].score
            if delta > th_delta:
                auto = True

        if auto:
            h = candidates[0]
            # Build alias expansion via LLM
            aliases = self._build_aliases(h.name, entity_type)
            return Entity(
                id=h.id,
                name=h.name,
                entity_type=entity_type,
                source_method="auto",
                confidence=h.score,
                candidates=candidates,
                aliases=aliases,
            )
        return None

    def _build_aliases(self, name: str, entity_type: str) -> AliasExpansion:
        """Ask LLM for synonyms / aliases to improve downstream retrieval."""
        if not self.llm.enabled:
            return AliasExpansion(canonical_name=name)

        sys_prompt = (
            "You are a biomedical ontology expert. "
            "List common synonyms, trade names, and abbreviations. Output JSON."
        )
        user_prompt = f"""
Entity: "{name}" (Type: {entity_type})
Provide:
{{
    "canonical_name": "{name}",
    "aliases": ["synonym1", "synonym2", ...]
}}
Return at most 5 aliases.
"""
        result = self.llm.generate(sys_prompt, user_prompt, json_mode=True)
        if "error" not in result:
            return AliasExpansion(
                canonical_name=result.get("canonical_name", name),
                aliases=result.get("aliases", []),
            )
        return AliasExpansion(canonical_name=name)
