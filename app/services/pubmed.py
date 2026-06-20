"""PubMed E-utilities service — upgraded with multi-strategy query expansion and multi-dim reranking."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Set

import requests

from app.config.settings import Settings
from app.models.evidence import (
    EvidencePolarity,
    Paper,
    RerankingScores,
    RetrievalQuery,
    StudyType,
)
from app.utils.helpers import rate_limit

logger = logging.getLogger(__name__)


class PubMedService:
    """Search and fetch papers via PubMed E-utilities."""

    def __init__(self, settings: Settings):
        self._search_url = settings.api_pubmed_search
        self._fetch_url = settings.api_pubmed_fetch

    # ------------------------------------------------------------------
    # Low-level API calls
    # ------------------------------------------------------------------

    @rate_limit(0.34)
    def _search_ids(self, query: str, max_results: int) -> List[str]:
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance",
        }
        try:
            r = requests.get(self._search_url, params=params, timeout=15)
            if r.ok:
                return r.json().get("esearchresult", {}).get("idlist", [])
        except Exception as exc:
            logger.error("PubMed search failed: %s", exc)
        return []

    @rate_limit(0.34)
    def _fetch_details(self, ids: List[str]) -> str:
        if not ids:
            return ""
        params = {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
        try:
            r = requests.get(self._fetch_url, params=params, timeout=20)
            if r.ok:
                return r.text
        except Exception as exc:
            logger.error("PubMed fetch failed: %s", exc)
        return ""

    # ------------------------------------------------------------------
    # Query building — multi-strategy expansion
    # ------------------------------------------------------------------

    def build_queries(
        self,
        drug: str,
        disease: str,
        aliases_drug: List[str],
        aliases_disease: List[str],
        targets: List[str],
        year_start: int,
        *,
        use_target_expansion: bool = True,
    ) -> List[RetrievalQuery]:
        """Build multiple query variants for comprehensive retrieval."""
        queries: List[RetrievalQuery] = []
        ts = datetime.now(timezone.utc).isoformat()
        date_filter = f'("{year_start}"[Date - Publication] : "3000"[Date - Publication])'

        # 1. Base query
        base = f'("{drug}"[Title/Abstract] AND "{disease}"[Title/Abstract]) AND {date_filter}'
        queries.append(RetrievalQuery(query_string=base, query_type="base", timestamp=ts))

        # 2. Alias-expanded queries
        for alias in aliases_drug[:3]:
            if alias.lower() != drug.lower():
                q = f'("{alias}"[Title/Abstract] AND "{disease}"[Title/Abstract]) AND {date_filter}'
                queries.append(RetrievalQuery(query_string=q, query_type="alias_expanded", timestamp=ts))

        for alias in aliases_disease[:3]:
            if alias.lower() != disease.lower():
                q = f'("{drug}"[Title/Abstract] AND "{alias}"[Title/Abstract]) AND {date_filter}'
                queries.append(RetrievalQuery(query_string=q, query_type="alias_expanded", timestamp=ts))

        # 3. Target-expanded queries
        if use_target_expansion and targets:
            for t in targets[:3]:
                q = f'("{t}"[Title/Abstract] AND "{disease}"[Title/Abstract]) AND {date_filter}'
                queries.append(RetrievalQuery(query_string=q, query_type="target_expanded", timestamp=ts))

        # 4. Contradiction-seeking query
        contra = (
            f'("{drug}"[Title/Abstract] AND "{disease}"[Title/Abstract] '
            f'AND ("no effect" OR "no association" OR "negative" OR "failed" OR "ineffective")) '
            f"AND {date_filter}"
        )
        queries.append(RetrievalQuery(query_string=contra, query_type="contradiction", timestamp=ts))

        # 5. Clinical evidence query
        clinical = (
            f'("{drug}"[Title/Abstract] AND "{disease}"[Title/Abstract] '
            f'AND ("clinical trial" OR "randomized" OR "phase" OR "meta-analysis")) '
            f"AND {date_filter}"
        )
        queries.append(RetrievalQuery(query_string=clinical, query_type="clinical", timestamp=ts))

        # 6. Case Report evidence (Crucial for rare diseases)
        case_rep = (
            f'("{drug}"[Title/Abstract] AND "{disease}"[Title/Abstract] '
            f'AND ("case report" OR "case series" OR "anecdotal")) '
            f"AND {date_filter}"
        )
        queries.append(RetrievalQuery(query_string=case_rep, query_type="case_report", timestamp=ts))

        return queries

    # ------------------------------------------------------------------
    # Full retrieval pipeline
    # ------------------------------------------------------------------

    def search_and_rank(
        self,
        drug: str,
        disease: str,
        targets: List[str],
        *,
        aliases_drug: List[str] | None = None,
        aliases_disease: List[str] | None = None,
        year_start: int = 2015,
        max_fetch: int = 20,
        use_target_expansion: bool = True,
    ) -> tuple[List[Paper], List[RetrievalQuery]]:
        """Execute multi-strategy search, dedupe, parse XML, then rerank."""

        aliases_drug = aliases_drug or []
        aliases_disease = aliases_disease or []

        queries = self.build_queries(
            drug, disease, aliases_drug, aliases_disease, targets, year_start,
            use_target_expansion=use_target_expansion,
        )

        # Collect all PMIDs (deduplicated)
        all_ids: List[str] = []
        seen: Set[str] = set()
        for q in queries:
            ids = self._search_ids(q.query_string, max_fetch)
            q.result_count = len(ids)
            q.pmids_returned = ids
            for pid in ids:
                if pid not in seen:
                    seen.add(pid)
                    all_ids.append(pid)

        logger.info("PubMed: %d unique PMIDs from %d queries", len(all_ids), len(queries))

        # Fetch paper details
        xml_data = self._fetch_details(all_ids[:max_fetch * 3])  # cap to avoid huge fetches
        if not xml_data:
            return [], queries

        raw_papers = self._parse_xml(xml_data)

        # Rerank
        ranked = self._rerank(raw_papers, drug, disease, targets)
        return ranked, queries

    # ------------------------------------------------------------------
    # XML parsing (preserved from app6.py)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_xml(xml_data: str) -> List[Paper]:
        papers: List[Paper] = []
        try:
            root = ET.fromstring(xml_data)
            for article in root.findall(".//PubmedArticle"):
                pmid = article.findtext(".//PMID") or ""
                title = article.findtext(".//ArticleTitle") or ""
                abstract_parts = article.findall(".//Abstract/AbstractText")
                abstract = " ".join(t.text for t in abstract_parts if t.text)
                year = article.findtext(".//PubDate/Year") or "N/A"

                if title:
                    papers.append(
                        Paper(
                            pmid=pmid,
                            title=title,
                            abstract=abstract,
                            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            year=year,
                        )
                    )
        except ET.ParseError as exc:
            logger.error("PubMed XML parse error: %s", exc)
        return papers

    # ------------------------------------------------------------------
    # Multi-dimensional reranking
    # ------------------------------------------------------------------

    @staticmethod
    def _rerank(papers: List[Paper], drug: str, disease: str, targets: List[str]) -> List[Paper]:
        drug_l = drug.lower()
        dis_l = disease.lower()
        targets_l = [t.lower() for t in targets]

        study_type_kw = {
            "clinical trial": StudyType.CLINICAL_TRIAL.value,
            "randomized": StudyType.CLINICAL_TRIAL.value,
            "meta-analysis": StudyType.META_ANALYSIS.value,
            "systematic review": StudyType.SYSTEMATIC_REVIEW.value,
            "case report": StudyType.CASE_REPORT.value,
            "case series": StudyType.CASE_REPORT.value,
            "in vitro": StudyType.IN_VITRO.value,
            "cell line": StudyType.IN_VITRO.value,
            "in vivo": StudyType.IN_VIVO.value,
            "mouse model": StudyType.IN_VIVO.value,
            "mice": StudyType.IN_VIVO.value,
            "rat": StudyType.IN_VIVO.value,
            "computational": StudyType.COMPUTATIONAL.value,
            "in silico": StudyType.COMPUTATIONAL.value,
            "molecular docking": StudyType.COMPUTATIONAL.value
        }
        contra_kw = ["no effect", "no association", "negative result", "failed", "ineffective", "not effective", "contradictory", "adverse event", "failed to show", "did not improve"]

        for p in papers:
            text_lower = (p.title + " " + p.abstract).lower()
            scores = RerankingScores()

            # Drug mention
            if drug_l in text_lower:
                scores.drug_mention = 3.0 if drug_l in p.title.lower() else 1.0

            # Disease mention
            if dis_l in text_lower:
                scores.disease_mention = 3.0 if dis_l in p.title.lower() else 1.0

            # Target overlap
            hit_targets = [t for t in targets_l if t in text_lower]
            scores.target_overlap = min(len(hit_targets) * 2.0, 6.0)
            if hit_targets:
                p.match_reasons.append(f"Targets: {len(hit_targets)}")

            # Mechanistic relevance
            mech_kw = ["mechanism", "pathway", "signaling", "receptor", "inhibit", "activate", "binding"]
            mech_hits = sum(1 for k in mech_kw if k in text_lower)
            scores.mechanistic_relevance = min(mech_hits * 0.5, 3.0)

            # Contradiction signal
            contra_hits = sum(1 for k in contra_kw if k in text_lower)
            if contra_hits > 0:
                scores.contradiction_signal = min(contra_hits * 1.0, 3.0)
                p.polarity = EvidencePolarity.CONTRADICTS
                p.match_reasons.append("Contradiction signal")

            # Study type and Clinical signal
            for kw, stype in study_type_kw.items():
                if kw in text_lower:
                    if stype not in p.study_types:
                        p.study_types.append(stype)
            
            if StudyType.CLINICAL_TRIAL.value in p.study_types or StudyType.META_ANALYSIS.value in p.study_types:
                scores.clinical_signal = 2.0
                p.match_reasons.append("Clinical study")
            elif StudyType.CASE_REPORT.value in p.study_types:
                scores.clinical_signal = 1.0
                p.match_reasons.append("Case report limit")

            # Recency
            try:
                yr = int(p.year)
                if yr >= 2023:
                    scores.recency = 2.0
                elif yr >= 2020:
                    scores.recency = 1.0
                if yr >= 2022:
                    p.match_reasons.append("Recent")
            except (ValueError, TypeError):
                pass

            # Abstract availability
            if p.abstract:
                scores.abstract_available = 1.0

            # Title match bonus
            if drug_l in p.title.lower() and dis_l in p.title.lower():
                p.match_reasons.append("Title Match")

            # Composite
            scores.composite = (
                scores.drug_mention
                + scores.disease_mention
                + scores.target_overlap
                + scores.mechanistic_relevance
                + scores.contradiction_signal
                + scores.clinical_signal
                + scores.recency
                + scores.abstract_available
            )

            p.reranking = scores
            p.relevance_score = scores.composite

            # Default polarity
            if p.polarity == EvidencePolarity.INCONCLUSIVE and scores.drug_mention > 0 and scores.disease_mention > 0:
                p.polarity = EvidencePolarity.SUPPORTS

        return sorted(papers, key=lambda x: x.relevance_score, reverse=True)
