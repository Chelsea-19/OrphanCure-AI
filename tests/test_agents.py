"""Tests for agent layer (unit-level, no network calls)."""

import pytest

from app.config.settings import Settings
from app.models.state import UnifiedRunState
from app.services.llm_provider import GeminiProvider


class TestBaseAgentContract:
    """Verify agent interface compliance."""

    def test_all_agents_have_name(self):
        from app.agents.entity_resolution import EntityResolutionAgent
        from app.agents.literature import LiteratureAgent
        from app.agents.mechanism import MechanismAgent
        from app.agents.synthesis_critic import SynthesisCriticAgent

        settings = Settings()
        state = UnifiedRunState()
        llm = GeminiProvider(settings)  # Will be disabled (no key)

        agents = [
            EntityResolutionAgent(state, llm, settings),
            MechanismAgent(state, llm, settings),
            LiteratureAgent(state, llm, settings),
            SynthesisCriticAgent(state, llm, settings),
        ]

        for agent in agents:
            assert hasattr(agent, "name")
            assert isinstance(agent.name, str)
            assert len(agent.name) > 0

    def test_all_agents_have_execute(self):
        from app.agents.entity_resolution import EntityResolutionAgent
        from app.agents.literature import LiteratureAgent
        from app.agents.mechanism import MechanismAgent
        from app.agents.synthesis_critic import SynthesisCriticAgent

        settings = Settings()
        state = UnifiedRunState()
        llm = GeminiProvider(settings)

        agents = [
            EntityResolutionAgent(state, llm, settings),
            MechanismAgent(state, llm, settings),
            LiteratureAgent(state, llm, settings),
            SynthesisCriticAgent(state, llm, settings),
        ]

        for agent in agents:
            assert hasattr(agent, "execute")
            assert callable(agent.execute)

    def test_agent_logging(self):
        from app.agents.mechanism import MechanismAgent

        settings = Settings()
        state = UnifiedRunState()
        llm = GeminiProvider(settings)

        agent = MechanismAgent(state, llm, settings)
        agent.log("test message")

        assert len(state.logs) == 1
        assert state.logs[0].agent == "MechanismAgent"
        assert state.logs[0].message == "test message"

    def test_synthesis_skips_malformed_llm_claim_items(self):
        from app.agents.synthesis_critic import SynthesisCriticAgent

        settings = Settings()
        state = UnifiedRunState()
        llm = GeminiProvider(settings)
        agent = SynthesisCriticAgent(state, llm, settings)
        report = {
            "key_mechanisms": [
                None,
                {
                    "claim": "Drug A has a mechanism relevant to Disease A.",
                    "supported_targets": ["ABC1", None],
                    "supported_papers": [
                        None,
                        {"pmid": "123", "evidence_snippet": "Drug A was studied.", "polarity": "SUPPORTS"},
                    ],
                    "confidence": None,
                },
            ],
            "contradictory_evidence": [None],
        }

        claims = agent._build_claims(report)

        assert len(claims) == 1
        assert claims[0].statement == "Drug A has a mechanism relevant to Disease A."
        assert claims[0].provenance.paper_evidence[0].pmid == "123"
        assert claims[0].confidence_numeric == 0.0
        assert any("Skipped" in entry.message for entry in state.logs)

    def test_mechanism_handles_missing_opentargets_details(self):
        from app.agents.mechanism import MechanismAgent
        from app.models.entities import Entity

        settings = Settings()
        state = UnifiedRunState()
        state.drug_entity = Entity(id="drug1", name="Drug A", entity_type="drug", source_method="auto")
        state.disease_entity = Entity(id="disease1", name="Disease A", entity_type="disease", source_method="auto")
        state.drug_data = None
        state.disease_data = {"associatedTargets": {"rows": [None, {"target": None}]}}
        llm = GeminiProvider(settings)
        agent = MechanismAgent(state, llm, settings)

        assert agent._extract_drug_targets() == {}
        assert agent._extract_disease_targets() == {}
