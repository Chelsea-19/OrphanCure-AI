"""Tests for Pydantic models."""

import json

import pytest

from app.models.claims import Claim, ClaimEvidenceBundle
from app.models.entities import AliasExpansion, Entity, EntityCandidate, TargetInfo
from app.models.evidence import (
    EvidenceMatrixSummary,
    EvidencePolarity,
    MechanismEvidence,
    Paper,
    PaperEvidence,
    RerankingScores,
    RetrievalQuery,
    VerificationStatus,
)
from app.models.scorecard import QualityDimension, QualityScorecard
from app.models.state import UnifiedRunState


# ------------------------------------------------------------------
# Entities
# ------------------------------------------------------------------

class TestEntityCandidate:
    def test_creation(self):
        ec = EntityCandidate(id="CHEMBL25", name="Aspirin", score=0.95)
        assert ec.source == "OpenTargets"
        assert ec.score == 0.95

    def test_serialization(self):
        ec = EntityCandidate(id="CHEMBL25", name="Aspirin", score=0.95)
        data = ec.model_dump()
        assert data["id"] == "CHEMBL25"


class TestEntity:
    def test_alias_auto_population(self):
        e = Entity(id="X", name="Metformin", entity_type="drug", source_method="auto")
        assert e.aliases.canonical_name == "Metformin"

    def test_with_aliases(self):
        aliases = AliasExpansion(canonical_name="Metformin", aliases=["Glucophage", "Fortamet"])
        e = Entity(id="X", name="Metformin", entity_type="drug", source_method="auto", aliases=aliases)
        assert len(e.aliases.aliases) == 2


class TestTargetInfo:
    def test_defaults(self):
        t = TargetInfo(symbol="PPARG", name="Peroxisome proliferator...")
        assert t.drug_action == "Unknown"
        assert t.disease_assoc_score == 0.0


# ------------------------------------------------------------------
# Evidence
# ------------------------------------------------------------------

class TestPaper:
    def test_default_polarity(self):
        p = Paper(pmid="12345", title="Test Paper")
        assert p.polarity == EvidencePolarity.INCONCLUSIVE

    def test_reranking_scores(self):
        p = Paper(pmid="12345", title="Test", reranking=RerankingScores(drug_mention=3.0))
        assert p.reranking.drug_mention == 3.0


class TestPaperEvidence:
    def test_default_status(self):
        pe = PaperEvidence(pmid="123")
        assert pe.verification_status == VerificationStatus.UNVERIFIED


class TestEvidenceMatrixSummary:
    def test_defaults(self):
        m = EvidenceMatrixSummary()
        assert m.total_retrieved == 0


# ------------------------------------------------------------------
# Claims
# ------------------------------------------------------------------

class TestClaim:
    def test_confidence_label_high(self):
        c = Claim(claim_id="C1", statement="Test", confidence_numeric=0.85)
        label = c.compute_confidence_label()
        assert label == "HIGH"

    def test_confidence_label_medium(self):
        c = Claim(claim_id="C2", statement="Test", confidence_numeric=0.5)
        label = c.compute_confidence_label()
        assert label == "MEDIUM"

    def test_confidence_label_low(self):
        c = Claim(claim_id="C3", statement="Test", confidence_numeric=0.2)
        label = c.compute_confidence_label()
        assert label == "LOW"


# ------------------------------------------------------------------
# Scorecard
# ------------------------------------------------------------------

class TestQualityScorecard:
    def test_create_default(self):
        sc = QualityScorecard.create_default()
        assert len(sc.dimensions) == 8

    def test_compute_overall(self):
        sc = QualityScorecard.create_default()
        for dim in sc.dimensions:
            dim.score = 0.8
        result = sc.compute_overall()
        assert result == pytest.approx(0.8)

    def test_decision_finalize(self):
        sc = QualityScorecard.create_default()
        for dim in sc.dimensions:
            dim.score = 0.9
        decision = sc.make_decision(0.70)
        assert decision == "finalize"

    def test_decision_rerun(self):
        sc = QualityScorecard.create_default()
        for dim in sc.dimensions:
            dim.score = 0.3
        decision = sc.make_decision(0.70)
        assert decision == "rerun"
        assert len(sc.rerun_targets) > 0

    def test_set_dimension(self):
        sc = QualityScorecard.create_default()
        sc.set_dimension("completeness", 0.95, "all good")
        dim = sc.get_dimension("completeness")
        assert dim.score == 0.95
        assert dim.reason == "all good"


# ------------------------------------------------------------------
# State
# ------------------------------------------------------------------

class TestUnifiedRunState:
    def test_run_id_generated(self):
        s = UnifiedRunState()
        assert len(s.run_id) == 12

    def test_log(self):
        s = UnifiedRunState()
        s.log("TestAgent", "hello", "INFO")
        assert len(s.logs) == 1
        assert s.logs[0].agent == "TestAgent"

    def test_serialization(self):
        s = UnifiedRunState()
        s.log("Test", "msg")
        json_str = s.export_json()
        data = json.loads(json_str)
        assert "run_id" in data
        assert len(data["logs"]) == 1
