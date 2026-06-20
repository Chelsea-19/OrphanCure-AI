"""Two-wave orchestration pipeline."""

from __future__ import annotations

import logging

from app.agents.entity_resolution import EntityResolutionAgent
from app.agents.candidate_generator import CandidateGeneratorAgent
from app.agents.literature import LiteratureAgent
from app.agents.mechanism import MechanismAgent
from app.agents.synthesis_critic import SynthesisCriticAgent
from app.config.settings import Settings
from app.models.state import UnifiedRunState
from app.orchestrator.quality_gate import QualityGate
from app.services.llm_provider import GeminiProvider

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Two-wave orchestration pipeline.

    Wave 1: Entity resolution → Mechanism discovery
    Wave 2: Literature retrieval → Synthesis/Critique → Quality gate
    """

    def __init__(self, state: UnifiedRunState, llm: GeminiProvider, settings: Settings):
        self.state = state
        self.llm = llm
        self.settings = settings

    # ------------------------------------------------------------------
    # Wave 1: Resolution + Mechanism
    # ------------------------------------------------------------------

    def run_wave1(self) -> None:
        """Entity resolution + mechanism/target discovery."""
        self.state.log("Pipeline", "=== Wave 1: Entity Resolution + Mechanism ===")

        # Entity Resolution
        er_agent = EntityResolutionAgent(self.state, self.llm, self.settings)
        er_agent.execute()

        if self.state.disease_entity:
            # Candidate Discovery
            cg_agent = CandidateGeneratorAgent(self.state, self.llm, self.settings)
            cg_agent.execute()

        # If we have a specific drug to evaluate, run mechanism discovery immediately
        if self.state.input_mode == "drug_and_disease":
            if self.state.drug_entity and self.state.disease_entity:
                mech_agent = MechanismAgent(self.state, self.llm, self.settings)
                mech_agent.execute()
            else:
                self.state.log("Pipeline", "Wave 1 paused — awaiting manual entity resolution", "WARN")
        else:
            # Phase 3: In disease_only mode, execute top-tier Candidate Ranker
            from app.agents.ranker import RankerAgent
            ranker = RankerAgent(self.state, self.llm, self.settings)
            ranker.execute()
            self.state.stage = "results"
            self.state.log("Pipeline", "Wave 1 complete — Transparently ranked candidates ready for review.")

    # ------------------------------------------------------------------
    # Wave 2: Literature + Synthesis + Quality
    # ------------------------------------------------------------------

    def run_wave2(self) -> None:
        """Literature retrieval → synthesis → quality gate loop."""
        self.state.log("Pipeline", "=== Wave 2: Literature + Synthesis + Quality Gate ===")

        if not self.state.drug_entity or not self.state.disease_entity:
            self.state.log("Pipeline", "Cannot run Wave 2 — entities not resolved", "ERROR")
            return

        # If mechanism hasn't run yet (e.g., after manual resolution), run it now
        if not self.state.common_targets and not self.state.drug_data:
            self.state.log("Pipeline", "Running mechanism discovery (deferred from Wave 1)")
            mech_agent = MechanismAgent(self.state, self.llm, self.settings)
            mech_agent.execute()

        # Literature retrieval
        lit_agent = LiteratureAgent(self.state, self.llm, self.settings)
        lit_agent.execute()

        # Synthesis + Critique
        if self.llm.enabled:
            synth_agent = SynthesisCriticAgent(self.state, self.llm, self.settings)
            synth_agent.execute()

            # Quality gate loop
            gate = QualityGate(self.state, self.llm, self.settings)

            max_iterations = self.settings.max_reruns + 1
            for iteration in range(max_iterations):
                result = gate.evaluate_and_act()

                if result in ("finalized", "max_reruns_reached"):
                    break

                if result == "rerun":
                    self.state.log("Pipeline", f"Quality gate rerun iteration {iteration + 1}")
                    # After rerun, the quality gate will re-evaluate on next loop

        # Final stage
        self.state.stage = "results"
        self.state.log("Pipeline", "Pipeline complete — results ready")

    # ------------------------------------------------------------------
    # Full run (when entities auto-resolve)
    # ------------------------------------------------------------------

    def run_full(self) -> None:
        """Execute both waves sequentially (for auto-resolved entities)."""
        self.run_wave1()
        if self.state.stage == "analysis":
            self.run_wave2()
