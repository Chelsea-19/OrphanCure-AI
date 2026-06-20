"""Claim-level traceability and provenance models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.evidence import (
    EvidencePolarity,
    MechanismEvidence,
    PaperEvidence,
    VerificationStatus,
)


class ClaimEvidenceBundle(BaseModel):
    """Full provenance for a single claim."""

    paper_evidence: List[PaperEvidence] = Field(default_factory=list)
    mechanism_evidence: List[MechanismEvidence] = Field(default_factory=list)
    retrieval_queries_used: List[str] = Field(default_factory=list)
    source_agent: str = ""
    source_run: str = ""  # run_id or rerun_id
    timestamp: str = ""


class Claim(BaseModel):
    """A single scientific claim with full provenance."""

    claim_id: str = ""
    statement: str = ""
    confidence_numeric: float = 0.0
    confidence_label: str = "LOW"  # HIGH | MEDIUM | LOW
    polarity: EvidencePolarity = EvidencePolarity.INCONCLUSIVE
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    supported_targets: List[str] = Field(default_factory=list)
    provenance: ClaimEvidenceBundle = Field(default_factory=ClaimEvidenceBundle)
    risk_flags: List[str] = Field(default_factory=list)

    def compute_confidence_label(self) -> str:
        if self.confidence_numeric >= 0.7:
            self.confidence_label = "HIGH"
        elif self.confidence_numeric >= 0.4:
            self.confidence_label = "MEDIUM"
        else:
            self.confidence_label = "LOW"
        return self.confidence_label
