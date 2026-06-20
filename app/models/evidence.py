"""Evidence and paper models."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class EvidencePolarity(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INCONCLUSIVE = "INCONCLUSIVE"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class StudyType(str, Enum):
    CLINICAL_TRIAL = "clinical_trial"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    CASE_REPORT = "case_report"
    IN_VITRO = "in_vitro"
    IN_VIVO = "in_vivo"
    COMPUTATIONAL = "computational"
    OTHER = "other"


# ------------------------------------------------------------------
# Paper / Literature Evidence
# ------------------------------------------------------------------

class RerankingScores(BaseModel):
    """Multi-dimensional reranking scores for a paper."""

    drug_mention: float = 0.0
    disease_mention: float = 0.0
    target_overlap: float = 0.0
    mechanistic_relevance: float = 0.0
    contradiction_signal: float = 0.0
    clinical_signal: float = 0.0
    recency: float = 0.0
    abstract_available: float = 0.0
    composite: float = 0.0


class Paper(BaseModel):
    """A PubMed paper with reranking metadata."""

    pmid: str
    title: str
    abstract: str = ""
    url: str = ""
    year: str = "N/A"
    relevance_score: float = 0.0
    reranking: RerankingScores = Field(default_factory=RerankingScores)
    match_reasons: List[str] = Field(default_factory=list)
    study_types: List[str] = Field(default_factory=list)
    polarity: EvidencePolarity = EvidencePolarity.INCONCLUSIVE


class PaperEvidence(BaseModel):
    """A single piece of evidence extracted from a paper."""

    pmid: str
    evidence_snippet: str = ""
    polarity: EvidencePolarity = EvidencePolarity.INCONCLUSIVE
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verification_error: Optional[str] = None
    reranking_score: float = 0.0


class MechanismEvidence(BaseModel):
    """Structured evidence for a mechanism / target overlap."""

    target_symbol: str
    drug_action: str = "Unknown"
    disease_assoc_score: float = 0.0
    pathway_summary: str = ""
    source_agent: str = "MechanismAgent"


# ------------------------------------------------------------------
# Retrieval Query Log
# ------------------------------------------------------------------

class RetrievalQuery(BaseModel):
    """Record of a literature search query."""

    query_string: str
    query_type: str = "base"  # base | alias_expanded | target_expanded | contradiction | clinical
    result_count: int = 0
    pmids_returned: List[str] = Field(default_factory=list)
    timestamp: str = ""


# ------------------------------------------------------------------
# Evidence Matrix Counts
# ------------------------------------------------------------------

class EvidenceMatrixSummary(BaseModel):
    """Aggregated evidence counts."""

    total_retrieved: int = 0
    supports: int = 0
    contradicts: int = 0
    inconclusive: int = 0
    verified: int = 0
    partially_verified: int = 0
    unverified: int = 0
