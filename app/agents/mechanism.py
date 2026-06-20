"""MechanismAgent — drug mechanism discovery and common target analysis."""

from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.models.entities import TargetInfo
from app.models.evidence import MechanismEvidence
from app.services.opentargets import OpenTargetsService


class MechanismAgent(BaseAgent):
    """
    Responsibilities:
    - Retrieve drug mechanisms and disease-associated targets from OpenTargets
    - Compute common targets (drug MOA targets ∩ disease targets)
    - Rank targets by disease association score
    - Generate structured mechanism evidence objects
    - Optionally enrich with pathway summaries via LLM
    """

    name = "MechanismAgent"

    def __init__(self, state, llm, settings):
        super().__init__(state, llm, settings)
        self._ot = OpenTargetsService(settings)

    def execute(self) -> None:
        self.log("Starting mechanism discovery")

        if not self.state.drug_entity or not self.state.disease_entity:
            self.log("Cannot run — entities not resolved", "ERROR")
            return

        # 1. Fetch details from OpenTargets
        self.state.drug_data = self._ot.get_drug_details(self.state.drug_entity.id) or {}
        self.state.disease_data = self._ot.get_disease_details(self.state.disease_entity.id) or {}
        if not self.state.drug_data:
            self.log("Open Targets drug details missing; continuing with zero drug targets", "WARN")
        if not self.state.disease_data:
            self.log("Open Targets disease details missing; continuing with zero disease targets", "WARN")

        # 2. Extract target sets
        drug_targets = self._extract_drug_targets()
        disease_targets = self._extract_disease_targets()

        # 3. Compute overlap
        common_symbols = set(drug_targets.keys()) & set(disease_targets.keys())
        self.log(f"Found {len(common_symbols)} common targets")

        # 4. Build TargetInfo list (sorted by disease score)
        common_targets: list[TargetInfo] = []
        for sym in common_symbols:
            score, approved_name = disease_targets[sym]
            common_targets.append(
                TargetInfo(
                    symbol=sym,
                    name=approved_name,
                    drug_action=drug_targets[sym],
                    disease_assoc_score=score,
                )
            )
        common_targets.sort(key=lambda t: t.disease_assoc_score, reverse=True)
        self.state.common_targets = common_targets

        # 5. Build mechanism evidence objects
        self.state.mechanism_evidence = [
            MechanismEvidence(
                target_symbol=t.symbol,
                drug_action=t.drug_action,
                disease_assoc_score=t.disease_assoc_score,
                source_agent=self.name,
            )
            for t in common_targets
        ]

        # 6. Optional LLM pathway enrichment for top targets
        if self.llm.enabled and common_targets:
            self._enrich_pathways(common_targets[:5])

        self.log(f"Mechanism discovery complete — {len(common_targets)} targets")

    # ------------------------------------------------------------------
    # Extraction helpers (preserved logic from app6.py step_2_analysis)
    # ------------------------------------------------------------------

    def _extract_drug_targets(self) -> dict[str, str]:
        """Return {symbol: action_type} from drug MOA data."""
        targets: dict[str, str] = {}
        drug_data = self.state.drug_data if isinstance(self.state.drug_data, dict) else {}
        rows = self._rows_from_nested(drug_data, "mechanismsOfAction")
        for r in rows:
            if not isinstance(r, dict):
                continue
            action = r.get("actionType", "Unknown")
            for t in r.get("targets") or []:
                if isinstance(t, dict) and t.get("approvedSymbol"):
                    targets[t["approvedSymbol"]] = action
        return targets

    def _extract_disease_targets(self) -> dict[str, tuple[float, str]]:
        """Return {symbol: (assoc_score, approved_name)} from disease data."""
        targets: dict[str, tuple[float, str]] = {}
        disease_data = self.state.disease_data if isinstance(self.state.disease_data, dict) else {}
        rows = self._rows_from_nested(disease_data, "associatedTargets")
        for r in rows:
            if not isinstance(r, dict):
                continue
            t = r.get("target")
            if isinstance(t, dict) and t.get("approvedSymbol"):
                targets[t["approvedSymbol"]] = (r.get("score", 0), t.get("approvedName", ""))
        return targets

    def _rows_from_nested(self, data: dict[str, Any], key: str) -> list:
        nested = data.get(key) or {}
        if not isinstance(nested, dict):
            self.log(f"Open Targets field {key} malformed; expected object", "WARN")
            return []
        rows = nested.get("rows") or []
        if not isinstance(rows, list):
            self.log(f"Open Targets field {key}.rows malformed; expected list", "WARN")
            return []
        return rows

    # ------------------------------------------------------------------
    # LLM pathway enrichment
    # ------------------------------------------------------------------

    def _enrich_pathways(self, top_targets: list[TargetInfo]) -> None:
        """Ask LLM for brief pathway context for the top common targets."""
        target_list = ", ".join(t.symbol for t in top_targets)
        drug = self.state.drug_entity.name
        disease = self.state.disease_entity.name

        sys_prompt = (
            "You are a molecular biology expert. "
            "For each target, provide a one-sentence summary of how it connects "
            "the drug's mechanism to the disease pathology. Output JSON."
        )
        user_prompt = f"""
Drug: {drug}
Disease: {disease}
Targets: {target_list}

Output Schema:
{{
    "pathways": [
        {{"target": "SYM", "summary": "Brief mechanistic context..."}}
    ]
}}
"""
        result = self.llm.generate(sys_prompt, user_prompt, json_mode=True)
        if isinstance(result, dict) and "error" not in result:
            pathway_map = {
                p["target"]: p["summary"]
                for p in result.get("pathways", []) or []
                if isinstance(p, dict) and "target" in p and "summary" in p
            }
            for me in self.state.mechanism_evidence:
                if me.target_symbol in pathway_map:
                    me.pathway_summary = pathway_map[me.target_symbol]
