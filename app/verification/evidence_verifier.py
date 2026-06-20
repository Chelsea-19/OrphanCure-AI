"""Evidence verifier — claim-level verification with polarity and status tags."""

from __future__ import annotations

import logging
from typing import Dict, List

from app.models.claims import Claim
from app.models.evidence import Paper, PaperEvidence, VerificationStatus
from app.models.state import UnifiedRunState
from app.utils.helpers import clean_text

logger = logging.getLogger(__name__)


class EvidenceVerifier:
    """
    Strengthened evidence verification.

    For every claim, verifies that:
    1. Referenced PMIDs exist in the retrieved paper set
    2. Quoted evidence snippets actually appear in the abstract (fuzzy)
    3. Tags each piece of evidence as VERIFIED / PARTIALLY_VERIFIED / UNVERIFIED

    If a claim has ONLY failed evidence → downgrade confidence or exclude.
    """

    def __init__(self, state: UnifiedRunState):
        self.state = state
        self._paper_map: Dict[str, str] = {}

    def verify_all(self) -> None:
        """Run verification on all draft claims and produce verified_claims."""
        self._paper_map = {p.pmid: p.abstract for p in self.state.papers}

        verified_claims: List[Claim] = []
        total_claims = 0
        fully_verified = 0

        for claim in self.state.draft_claims:
            total_claims += 1
            claim = self._verify_claim(claim)
            verified_claims.append(claim)

            if claim.verification_status == VerificationStatus.VERIFIED:
                fully_verified += 1

        self.state.verified_claims = verified_claims

        # Update evidence matrix verification counts
        v_counts = {"verified": 0, "partial": 0, "unverified": 0}
        for c in verified_claims:
            if c.verification_status == VerificationStatus.VERIFIED:
                v_counts["verified"] += 1
            elif c.verification_status == VerificationStatus.PARTIALLY_VERIFIED:
                v_counts["partial"] += 1
            else:
                v_counts["unverified"] += 1

        self.state.evidence_matrix.verified = v_counts["verified"]
        self.state.evidence_matrix.partially_verified = v_counts["partial"]
        self.state.evidence_matrix.unverified = v_counts["unverified"]

        # Update final report with verification status
        self._update_report_verification(total_claims, fully_verified)

        self.state.log(
            "EvidenceVerifier",
            f"Verification complete: {fully_verified}/{total_claims} claims fully verified"
        )

    def _verify_claim(self, claim: Claim) -> Claim:
        """Verify a single claim's evidence."""
        if not claim.provenance.paper_evidence:
            claim.verification_status = VerificationStatus.UNVERIFIED
            claim.risk_flags.append("No paper evidence attached")
            return claim

        verified_count = 0
        total_refs = len(claim.provenance.paper_evidence)

        for pe in claim.provenance.paper_evidence:
            pe.verification_status = self._verify_paper_evidence(pe)
            if pe.verification_status == VerificationStatus.VERIFIED:
                verified_count += 1

        # Claim-level status
        if verified_count == total_refs:
            claim.verification_status = VerificationStatus.VERIFIED
        elif verified_count > 0:
            claim.verification_status = VerificationStatus.PARTIALLY_VERIFIED
        else:
            claim.verification_status = VerificationStatus.UNVERIFIED
            claim.confidence_numeric = max(claim.confidence_numeric * 0.2, 0.0)
            claim.compute_confidence_label()
            claim.risk_flags.append("All evidence verification failed")

        return claim

    def _verify_paper_evidence(self, pe: PaperEvidence) -> VerificationStatus:
        """Verify a single PaperEvidence reference."""
        # Check 1: PMID in retrieved set
        if pe.pmid not in self._paper_map:
            pe.verification_error = "PMID not in retrieved set"
            return VerificationStatus.UNVERIFIED

        abstract = self._paper_map[pe.pmid]

        # Check 2: Snippet appears in abstract (fuzzy match)
        snippet = pe.evidence_snippet.strip()
        if not snippet:
            pe.verification_error = "Empty evidence snippet"
            return VerificationStatus.UNVERIFIED

        norm_snippet = clean_text(snippet)
        norm_abstract = clean_text(abstract)

        if not norm_abstract:
            pe.verification_error = "Abstract not available for verification"
            return VerificationStatus.PARTIALLY_VERIFIED

        if norm_snippet in norm_abstract:
            return VerificationStatus.VERIFIED

        # Partial match — check if a substantial substring matches
        # Try progressively shorter substrings (at least 60% of the original)
        min_len = max(int(len(norm_snippet) * 0.6), 20)
        for end in range(len(norm_snippet), min_len, -5):
            if norm_snippet[:end] in norm_abstract:
                pe.verification_error = "Partial quote match"
                return VerificationStatus.PARTIALLY_VERIFIED

        pe.verification_error = "Quote mismatch (fuzzy check failed)"
        return VerificationStatus.UNVERIFIED

    def _update_report_verification(self, total: int, verified: int) -> None:
        """Update the final_report dict based on verification outcomes."""
        report = self.state.final_report
        if not report or "error" in report:
            return

        if total > 0 and verified == 0:
            report["conclusion"] = "Unlikely"
            report["overall_confidence"] = "Low"
            report.setdefault("risk_flags", []).append("ALL evidence verification failed")

        # Add verification summary to report
        report["verification_summary"] = {
            "total_claims": total,
            "fully_verified": verified,
            "status": "Passed" if verified == total else ("Partial" if verified > 0 else "Failed")
        }
