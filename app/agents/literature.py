"""LiteratureAgent — mechanism-aware literature retrieval and evidence classification."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.evidence import EvidenceMatrixSummary, EvidencePolarity
from app.services.pubmed import PubMedService


class LiteratureAgent(BaseAgent):
    """
    Responsibilities:
    - Build mechanism-aware search queries using aliases + target expansion
    - Query PubMed via multi-strategy expansion
    - Rerank papers by multi-dimensional scoring
    - Classify evidence polarity (SUPPORTS / CONTRADICTS / INCONCLUSIVE)
    - Build evidence matrix summary
    """

    name = "LiteratureAgent"

    def __init__(self, state, llm, settings):
        super().__init__(state, llm, settings)
        self._pubmed = PubMedService(settings)

    def execute(self) -> None:
        self.log("Starting literature retrieval")

        if not self.state.drug_entity or not self.state.disease_entity:
            self.log("Cannot run — entities not resolved", "ERROR")
            return

        drug_name = self.state.drug_entity.name
        disease_name = self.state.disease_entity.name
        target_symbols = [t.symbol for t in self.state.common_targets]

        # Gather aliases
        aliases_drug = self.state.drug_entity.aliases.aliases if self.state.drug_entity.aliases else []
        aliases_disease = self.state.disease_entity.aliases.aliases if self.state.disease_entity.aliases else []

        # Run search
        papers, queries = self._pubmed.search_and_rank(
            drug_name,
            disease_name,
            target_symbols,
            aliases_drug=aliases_drug,
            aliases_disease=aliases_disease,
            year_start=self.settings.pubmed_year_start,
            max_fetch=self.settings.pubmed_max_fetch,
            use_target_expansion=self.settings.pubmed_target_expansion,
        )

        self.state.papers = papers
        self.state.retrieval_queries = queries

        self.log(f"Retrieved {len(papers)} papers via {len(queries)} queries")

        # Build evidence matrix
        self._build_evidence_matrix()

    def _build_evidence_matrix(self) -> None:
        """Compute polarity and verification counts."""
        matrix = EvidenceMatrixSummary(total_retrieved=len(self.state.papers))

        for p in self.state.papers:
            if p.polarity == EvidencePolarity.SUPPORTS:
                matrix.supports += 1
            elif p.polarity == EvidencePolarity.CONTRADICTS:
                matrix.contradicts += 1
            else:
                matrix.inconclusive += 1

        self.state.evidence_matrix = matrix
        self.log(
            f"Evidence matrix: {matrix.supports} support, "
            f"{matrix.contradicts} contradict, {matrix.inconclusive} inconclusive"
        )
