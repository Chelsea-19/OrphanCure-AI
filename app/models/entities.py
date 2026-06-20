"""Entity and entity-resolution models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class EntityCandidate(BaseModel):
    """A single candidate returned by a search backend."""

    id: str
    name: str
    score: float
    source: str = "OpenTargets"


class AliasExpansion(BaseModel):
    """Synonym / alias expansion for downstream retrieval."""

    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    ontology_ids: List[str] = Field(default_factory=list)


class ProvenanceSource(BaseModel):
    """Provenance tracking for a candidate or claim."""
    
    source_type: str  # e.g., "literature", "opentargets", "mechanism_agent"
    source_id: str    # e.g., PMID or DB ID
    confidence: float = 1.0
    rationale: str = ""


class RankingBreakdown(BaseModel):
    """Transparent multi-factor ranking scores."""
    
    mechanism_fit: float = 0.0
    evidence_strength: float = 0.0
    safety_feasibility: float = 0.0
    contradiction_burden: float = 0.0
    translational_readiness: float = 0.0


class CandidateDrug(BaseModel):
    """A generated candidate drug for a target disease."""
    
    id: str  # typically generic name or db ID
    name: str
    mechanism_category: str = "Unknown"
    provenance: List[ProvenanceSource] = Field(default_factory=list)
    score: float = 0.0
    ranking_breakdown: RankingBreakdown = Field(default_factory=RankingBreakdown)
    priority_class: str = "Unranked"  # High | Medium | Low | Unranked
    rationale: str = ""
    evidence_gaps: List[str] = Field(default_factory=list)


class Entity(BaseModel):
    """A resolved biomedical entity (drug or disease)."""

    id: str
    name: str
    entity_type: str  # "drug" | "disease"
    source_method: str  # "auto" | "manual" | "correction"
    confidence: float = 1.0
    candidates: List[EntityCandidate] = Field(default_factory=list)
    aliases: AliasExpansion = Field(default_factory=lambda: AliasExpansion(canonical_name=""))

    def model_post_init(self, __context) -> None:
        if not self.aliases.canonical_name:
            self.aliases.canonical_name = self.name


class TargetInfo(BaseModel):
    """A protein target shared between drug and disease."""

    symbol: str
    name: str
    drug_action: str = "Unknown"
    disease_assoc_score: float = 0.0
