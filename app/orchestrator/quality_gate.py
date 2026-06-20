"""Quality gate — decides whether to finalize or trigger targeted reruns."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from app.agents.literature import LiteratureAgent
from app.agents.mechanism import MechanismAgent
from app.agents.synthesis_critic import SynthesisCriticAgent
from app.config.settings import Settings
from app.models.scorecard import QualityScorecard
from app.models.state import RerunRecord, UnifiedRunState
from app.services.llm_provider import GeminiProvider
from app.verification.evidence_verifier import EvidenceVerifier


class QualityGate:
    """
    Central quality manager.

    Evaluates the scorecard after synthesis and decides:
    - FINALIZE if overall >= threshold
    - TARGETED RERUN if below threshold, up to max_reruns
    """

    def __init__(self, state: UnifiedRunState, llm: GeminiProvider, settings: Settings):
        self.state = state
        self.llm = llm
        self.settings = settings

    def evaluate_and_act(self) -> str:
        """
        Check scorecard, run verification, decide finalize vs. rerun.

        Returns: "finalized" | "rerun" | "max_reruns_reached"
        """
        scorecard = self.state.scorecard

        # Always run verification first
        verifier = EvidenceVerifier(self.state)
        verifier.verify_all()

        # Re-score citation validity after verification
        self._update_citation_score(scorecard)

        decision = scorecard.make_decision(self.settings.quality_threshold)

        if decision == "finalize":
            self.state.log("QualityGate", f"Quality passed ({scorecard.overall_score:.2f}) — finalizing")
            return "finalized"

        # Check rerun budget
        if len(self.state.rerun_history) >= self.settings.max_reruns:
            self.state.log(
                "QualityGate",
                f"Quality below threshold ({scorecard.overall_score:.2f}) but max reruns reached — forced finalize",
                "WARN"
            )
            return "max_reruns_reached"

        # Targeted rerun
        self.state.log(
            "QualityGate",
            f"Quality below threshold ({scorecard.overall_score:.2f}) — triggering rerun for: "
            f"{', '.join(scorecard.rerun_targets)}",
            "WARN"
        )

        rerun_record = RerunRecord(
            rerun_id=uuid.uuid4().hex[:8],
            reason=f"Score {scorecard.overall_score:.2f} < {self.settings.quality_threshold}",
            target_agents=scorecard.rerun_targets,
            weak_dimensions=scorecard.weak_dimensions,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.state.rerun_history.append(rerun_record)

        self._execute_targeted_rerun(scorecard.rerun_targets)
        return "rerun"

    def _update_citation_score(self, scorecard: QualityScorecard) -> None:
        """Update citation_validity based on actual verification results."""
        claims = self.state.verified_claims or self.state.draft_claims
        if not claims:
            return

        from app.models.evidence import VerificationStatus

        verified = sum(
            1 for c in claims
            if c.verification_status == VerificationStatus.VERIFIED
        )
        partial = sum(
            1 for c in claims
            if c.verification_status == VerificationStatus.PARTIALLY_VERIFIED
        )

        total = len(claims)
        score = (verified + 0.5 * partial) / total if total > 0 else 0.0
        scorecard.set_dimension(
            "citation_validity", score,
            f"{verified} verified, {partial} partial out of {total}"
        )

    def _execute_targeted_rerun(self, target_agents: List[str]) -> None:
        """Re-execute only the weak agents."""
        for agent_name in target_agents:
            self.state.log("QualityGate", f"Re-running {agent_name}")

            if agent_name == "MechanismAgent":
                agent = MechanismAgent(self.state, self.llm, self.settings)
                agent.execute()

            elif agent_name == "LiteratureAgent":
                agent = LiteratureAgent(self.state, self.llm, self.settings)
                agent.execute()

            elif agent_name == "SynthesisCriticAgent":
                agent = SynthesisCriticAgent(self.state, self.llm, self.settings)
                agent.execute()
