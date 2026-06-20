"""Tests for the orchestration / quality gate layer."""

import pytest

from app.models.claims import Claim, ClaimEvidenceBundle
from app.models.evidence import Paper, PaperEvidence, VerificationStatus
from app.models.scorecard import QualityScorecard
from app.models.state import UnifiedRunState


class TestQualityGateDecision:
    """Test the scorecard decision logic (without network calls)."""

    def test_finalize_on_good_score(self):
        sc = QualityScorecard.create_default()
        for dim in sc.dimensions:
            dim.score = 0.85
        decision = sc.make_decision(0.70)
        assert decision == "finalize"

    def test_rerun_on_low_score(self):
        sc = QualityScorecard.create_default()
        for dim in sc.dimensions:
            dim.score = 0.3
        decision = sc.make_decision(0.70)
        assert decision == "rerun"
        assert len(sc.weak_dimensions) > 0
        assert len(sc.rerun_targets) > 0

    def test_rerun_targets_map_correctly(self):
        sc = QualityScorecard.create_default()
        # Only citation_validity is weak
        for dim in sc.dimensions:
            dim.score = 0.9
        sc.set_dimension("citation_validity", 0.2, "Bad citations")
        decision = sc.make_decision(0.70)
        # Overall should still be above threshold since others are 0.9
        # (0.2 + 7*0.9) / 8 = 0.8125, which is > 0.70
        assert decision == "finalize"

    def test_mixed_scores_rerun(self):
        sc = QualityScorecard.create_default()
        # Many dimensions weak
        for dim in sc.dimensions:
            dim.score = 0.4
        sc.set_dimension("evidence_support", 0.2)
        sc.set_dimension("mechanistic_specificity", 0.1)
        decision = sc.make_decision(0.70)
        assert decision == "rerun"
        assert "LiteratureAgent" in sc.rerun_targets
        assert "MechanismAgent" in sc.rerun_targets


class TestRerunHistory:
    def test_rerun_history_tracks(self):
        state = UnifiedRunState()
        from app.models.state import RerunRecord
        rr = RerunRecord(
            rerun_id="test123",
            reason="Low score",
            target_agents=["LiteratureAgent"],
            weak_dimensions=["citation_validity"],
        )
        state.rerun_history.append(rr)
        assert len(state.rerun_history) == 1
        assert state.rerun_history[0].target_agents == ["LiteratureAgent"]
