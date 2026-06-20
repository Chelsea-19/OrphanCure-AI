"""Tests for verification module."""

import pytest

from app.models.claims import Claim, ClaimEvidenceBundle
from app.models.evidence import (
    EvidencePolarity,
    Paper,
    PaperEvidence,
    VerificationStatus,
)
from app.models.state import UnifiedRunState
from app.verification.evidence_verifier import EvidenceVerifier


def _make_state_with_papers() -> UnifiedRunState:
    state = UnifiedRunState()
    state.papers = [
        Paper(
            pmid="111",
            title="Drug X in Disease Y",
            abstract="This study demonstrates that Drug X significantly reduces inflammation via the JAK-STAT pathway in Disease Y models.",
        ),
        Paper(
            pmid="222",
            title="Another paper",
            abstract="No relevant content here.",
        ),
    ]
    return state


class TestEvidenceVerifier:
    def test_verified_claim(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C1",
                statement="Drug X reduces inflammation",
                confidence_numeric=0.8,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(
                            pmid="111",
                            evidence_snippet="Drug X significantly reduces inflammation via the JAK-STAT pathway",
                        )
                    ]
                ),
            )
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        assert len(state.verified_claims) == 1
        claim = state.verified_claims[0]
        assert claim.verification_status == VerificationStatus.VERIFIED

    def test_unverified_pmid_missing(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C2",
                statement="Some claim",
                confidence_numeric=0.7,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(pmid="999", evidence_snippet="Some text")
                    ]
                ),
            )
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        claim = state.verified_claims[0]
        assert claim.verification_status == VerificationStatus.UNVERIFIED
        assert claim.provenance.paper_evidence[0].verification_error == "PMID not in retrieved set"

    def test_unverified_quote_mismatch(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C3",
                statement="Some claim",
                confidence_numeric=0.7,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(
                            pmid="111",
                            evidence_snippet="This text does not appear anywhere in the abstract at all whatsoever",
                        )
                    ]
                ),
            )
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        claim = state.verified_claims[0]
        assert claim.verification_status == VerificationStatus.UNVERIFIED

    def test_confidence_downgrade_on_failure(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C4",
                statement="Bad claim",
                confidence_numeric=0.9,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(pmid="999", evidence_snippet="nope")
                    ]
                ),
            )
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        claim = state.verified_claims[0]
        assert claim.confidence_numeric < 0.3  # Severely downgraded

    def test_no_evidence_claim(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C5",
                statement="Empty claim",
                confidence_numeric=0.5,
                provenance=ClaimEvidenceBundle(),
            )
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        claim = state.verified_claims[0]
        assert claim.verification_status == VerificationStatus.UNVERIFIED
        assert "No paper evidence attached" in claim.risk_flags

    def test_evidence_matrix_updated(self):
        state = _make_state_with_papers()
        state.draft_claims = [
            Claim(
                claim_id="C6",
                statement="Good claim",
                confidence_numeric=0.8,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(
                            pmid="111",
                            evidence_snippet="Drug X significantly reduces inflammation",
                        )
                    ]
                ),
            ),
            Claim(
                claim_id="C7",
                statement="Bad claim",
                confidence_numeric=0.5,
                provenance=ClaimEvidenceBundle(
                    paper_evidence=[
                        PaperEvidence(pmid="999", evidence_snippet="nope")
                    ]
                ),
            ),
        ]

        verifier = EvidenceVerifier(state)
        verifier.verify_all()

        assert state.evidence_matrix.verified == 1
        assert state.evidence_matrix.unverified == 1
