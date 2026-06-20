"""Tests for service layer (non-network, unit-level)."""

import pytest

from app.models.evidence import EvidencePolarity, Paper, RerankingScores
from app.services.pubmed import PubMedService


class TestPubMedReranking:
    """Test the static reranking method."""

    def _make_paper(self, pmid, title, abstract="", year="2024"):
        return Paper(pmid=pmid, title=title, abstract=abstract, year=year)

    def test_drug_in_title_scores_higher(self):
        papers = [
            self._make_paper("1", "Metformin in Alzheimer's disease", "Metformin reduces tau."),
            self._make_paper("2", "General review of neurodegenerative diseases", "No specific drug."),
        ]
        ranked = PubMedService._rerank(papers, "Metformin", "Alzheimer's disease", [])
        assert ranked[0].pmid == "1"
        assert ranked[0].relevance_score > ranked[1].relevance_score

    def test_target_overlap_increases_score(self):
        papers = [
            self._make_paper("1", "PPARG and diabetes", "PPARG pathway analysis"),
            self._make_paper("2", "General biology", "Nothing specific"),
        ]
        ranked = PubMedService._rerank(papers, "Metformin", "diabetes", ["PPARG"])
        assert ranked[0].pmid == "1"
        assert "Targets: 1" in ranked[0].match_reasons

    def test_clinical_signal(self):
        papers = [
            self._make_paper("1", "Drug study", "A randomized clinical trial of Drug."),
            self._make_paper("2", "Drug study", "A basic science review of Drug."),
        ]
        ranked = PubMedService._rerank(papers, "Drug", "Disease", [])
        clinical = [p for p in ranked if "Clinical study" in p.match_reasons]
        assert len(clinical) == 1

    def test_contradiction_signal(self):
        papers = [
            self._make_paper("1", "Drug failed", "The drug showed no effect on disease markers."),
        ]
        ranked = PubMedService._rerank(papers, "Drug", "disease", [])
        assert ranked[0].polarity == EvidencePolarity.CONTRADICTS
        assert "Contradiction signal" in ranked[0].match_reasons

    def test_recency_bonus(self):
        papers = [
            self._make_paper("1", "Old study", year="2010"),
            self._make_paper("2", "New study", year="2024"),
        ]
        ranked = PubMedService._rerank(papers, "X", "Y", [])
        new_p = next(p for p in ranked if p.pmid == "2")
        assert new_p.reranking.recency > 0


class TestPubMedQueryBuilder:
    """Test query building logic (no network calls)."""

    def test_builds_base_query(self):
        from app.config.settings import Settings
        svc = PubMedService(Settings())
        queries = svc.build_queries("Metformin", "Alzheimer", [], [], [], 2015)
        assert len(queries) >= 3  # base + contradiction + clinical
        types = [q.query_type for q in queries]
        assert "base" in types
        assert "contradiction" in types
        assert "clinical" in types

    def test_alias_expansion(self):
        from app.config.settings import Settings
        svc = PubMedService(Settings())
        queries = svc.build_queries(
            "Metformin", "AD", ["Glucophage"], ["Alzheimer's disease"], [], 2015
        )
        alias_qs = [q for q in queries if q.query_type == "alias_expanded"]
        assert len(alias_qs) == 2  # One for drug alias, one for disease alias

    def test_target_expansion(self):
        from app.config.settings import Settings
        svc = PubMedService(Settings())
        queries = svc.build_queries(
            "Metformin", "AD", [], [], ["PPARG", "AMPK"], 2015, use_target_expansion=True
        )
        target_qs = [q for q in queries if q.query_type == "target_expanded"]
        assert len(target_qs) == 2
