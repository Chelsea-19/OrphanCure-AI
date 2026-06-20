"""Quality scorecard for the agent manager / quality gate."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class QualityDimension(BaseModel):
    """A single scored dimension of the quality scorecard."""

    name: str
    score: float = 0.0  # 0.0 – 1.0
    reason: str = ""


class QualityScorecard(BaseModel):
    """Multi-dimensional scorecard used by the quality gate."""

    dimensions: List[QualityDimension] = Field(default_factory=list)
    overall_score: float = 0.0
    decision: str = "pending"  # "finalize" | "rerun" | "pending"
    weak_dimensions: List[str] = Field(default_factory=list)
    rerun_targets: List[str] = Field(default_factory=list)

    # ----- Factory -----

    @classmethod
    def create_default(cls) -> "QualityScorecard":
        dim_names = [
            "completeness",
            "evidence_support",
            "citation_validity",
            "mechanistic_specificity",
            "contradiction_handling",
            "traceability",
            "output_structure",
            "actionability",
        ]
        return cls(dimensions=[QualityDimension(name=n) for n in dim_names])

    # ----- Computation -----

    def compute_overall(self) -> float:
        if not self.dimensions:
            self.overall_score = 0.0
            return 0.0
        self.overall_score = sum(d.score for d in self.dimensions) / len(self.dimensions)
        self.weak_dimensions = [d.name for d in self.dimensions if d.score < 0.5]
        return self.overall_score

    def make_decision(self, threshold: float = 0.70) -> str:
        self.compute_overall()
        if self.overall_score >= threshold:
            self.decision = "finalize"
        else:
            self.decision = "rerun"
            self._assign_rerun_targets()
        return self.decision

    def _assign_rerun_targets(self) -> None:
        """Map weak dimensions to the agent(s) responsible for correcting them."""
        dim_to_agent = {
            "completeness": "SynthesisCriticAgent",
            "evidence_support": "LiteratureAgent",
            "citation_validity": "LiteratureAgent",
            "mechanistic_specificity": "MechanismAgent",
            "contradiction_handling": "LiteratureAgent",
            "traceability": "SynthesisCriticAgent",
            "output_structure": "SynthesisCriticAgent",
            "actionability": "SynthesisCriticAgent",
        }
        targets = set()
        for dim_name in self.weak_dimensions:
            agent = dim_to_agent.get(dim_name)
            if agent:
                targets.add(agent)
        self.rerun_targets = sorted(targets)

    def get_dimension(self, name: str) -> QualityDimension | None:
        for d in self.dimensions:
            if d.name == name:
                return d
        return None

    def set_dimension(self, name: str, score: float, reason: str = "") -> None:
        dim = self.get_dimension(name)
        if dim:
            dim.score = score
            dim.reason = reason

    def to_summary_dict(self) -> Dict:
        return {
            "overall_score": round(self.overall_score, 3),
            "decision": self.decision,
            "dimensions": {d.name: {"score": round(d.score, 3), "reason": d.reason} for d in self.dimensions},
            "weak_dimensions": self.weak_dimensions,
            "rerun_targets": self.rerun_targets,
        }
