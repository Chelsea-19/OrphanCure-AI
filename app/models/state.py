"""Unified run-state model for the entire pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.claims import Claim
from app.models.entities import AliasExpansion, CandidateDrug, Entity, EntityCandidate, TargetInfo
from app.models.evidence import (
    EvidenceMatrixSummary,
    MechanismEvidence,
    Paper,
    RetrievalQuery,
)
from app.models.scorecard import QualityScorecard


class LogEntry(BaseModel):
    """Structured log entry."""

    timestamp: str = ""
    agent: str = ""
    message: str = ""
    status: str = "INFO"  # INFO | WARN | ERROR | DEBUG
    details: Any = None


class RerunRecord(BaseModel):
    """Record of a targeted rerun."""

    rerun_id: str = ""
    reason: str = ""
    target_agents: List[str] = Field(default_factory=list)
    weak_dimensions: List[str] = Field(default_factory=list)
    timestamp: str = ""


class UnifiedRunState(BaseModel):
    """
    Central state for a single analysis run.

    Every agent reads from and writes to this state object.
    The state is fully serializable via Pydantic.
    """

    # ---- Identity ----
    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ---- Stage ----
    stage: str = "input"  # input -> resolution -> analysis -> results

    # ---- User Input ----
    input_mode: str = "drug_and_disease"  # 'drug_and_disease' or 'disease_only'
    drug_input: str = ""
    disease_input: str = ""
    
    # ---- Candidate Discovery ----
    generated_candidates: List[CandidateDrug] = Field(default_factory=list)

    # ---- Entity Resolution ----
    drug_candidates: List[EntityCandidate] = Field(default_factory=list)
    disease_candidates: List[EntityCandidate] = Field(default_factory=list)
    drug_entity: Optional[Entity] = None
    disease_entity: Optional[Entity] = None

    # ---- Drug / Disease Metadata ----
    drug_data: Dict = Field(default_factory=dict)
    disease_data: Dict = Field(default_factory=dict)

    # ---- Mechanism Layer ----
    common_targets: List[TargetInfo] = Field(default_factory=list)
    mechanism_evidence: List[MechanismEvidence] = Field(default_factory=list)

    # ---- Literature Layer ----
    retrieval_queries: List[RetrievalQuery] = Field(default_factory=list)
    papers: List[Paper] = Field(default_factory=list)
    evidence_matrix: EvidenceMatrixSummary = Field(default_factory=EvidenceMatrixSummary)

    # ---- Claims & Report ----
    draft_claims: List[Claim] = Field(default_factory=list)
    verified_claims: List[Claim] = Field(default_factory=list)
    final_report: Dict = Field(default_factory=dict)

    # ---- Quality Gate ----
    scorecard: QualityScorecard = Field(default_factory=QualityScorecard.create_default)
    rerun_history: List[RerunRecord] = Field(default_factory=list)

    # ---- Logging ----
    logs: List[LogEntry] = Field(default_factory=list)

    # ---- UI Messages ----
    ui_messages: List[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def log(
        self,
        agent: str,
        message: str,
        status: str = "INFO",
        details: Any = None,
    ) -> None:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = LogEntry(timestamp=ts, agent=agent, message=message, status=status, details=details)
        self.logs.append(entry)

    def add_ui_message(self, msg: str) -> None:
        self.ui_messages.append(msg)

    def export_json(self) -> str:
        """Serialize entire state to JSON."""
        return self.model_dump_json(indent=2)
