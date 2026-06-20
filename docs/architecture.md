# Architecture Overview

## System Design

OrphanCure-AI Pro implements a **two-wave, multi-agent scientific analysis pipeline** for drug repurposing hypothesis validation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                             │
│  ┌─────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Input   │ │ Resolution │ │  Results │ │  7-Tab Display   │  │
│  │  Stage   │ │   Stage    │ │  Stage   │ │  + Export        │  │
│  └────┬─────┘ └─────┬──────┘ └────┬─────┘ └──────────────────┘  │
│       │             │              │                              │
└───────┼─────────────┼──────────────┼─────────────────────────────┘
        │             │              │
┌───────▼─────────────▼──────────────▼─────────────────────────────┐
│                      Orchestration Layer                          │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │     Pipeline (2-wave)     │  │      Quality Gate            │  │
│  │                           │  │  ┌────────────────────────┐  │  │
│  │  Wave 1:                  │  │  │   8-dim Scorecard      │  │  │
│  │    Entity Resolution      │  │  │   Decision: finalize   │  │  │
│  │    Mechanism Discovery    │  │  │         or rerun       │  │  │
│  │                           │  │  └────────────────────────┘  │  │
│  │  Wave 2:                  │  │  ┌────────────────────────┐  │  │
│  │    Literature Retrieval   │  │  │  Targeted Agent Rerun  │  │  │
│  │    Synthesis + Critique   │  │  │  (max N iterations)    │  │  │
│  │    Quality Gate Loop      │  │  └────────────────────────┘  │  │
│  └──────────────────────────┘  └──────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
        │             │              │              │
┌───────▼─────────────▼──────────────▼──────────────▼──────────────┐
│                         Agent Layer                               │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐│
│  │ EntityResolution│ │  Mechanism     │ │     Literature         ││
│  │     Agent       │ │    Agent       │ │       Agent            ││
│  │                 │ │                │ │                        ││
│  │ • OT search     │ │ • Drug targets │ │ • Multi-query search   ││
│  │ • LLM correct   │ │ • Disease tgts │ │ • Alias expansion      ││
│  │ • Alias expand   │ │ • Overlap      │ │ • Target expansion     ││
│  │ • Auto-select    │ │ • Pathway LLM  │ │ • 8-dim reranking      ││
│  └────────────────┘ └────────────────┘ │ • Polarity classif.    ││
│                                         └────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────┐│
│  │              SynthesisCritic Agent                             ││
│  │ • LLM synthesis with mechanism context                        ││
│  │ • Claim-level output with provenance bundles                  ││
│  │ • 8-dimension quality scorecard computation                   ││
│  └───────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
        │             │              │
┌───────▼─────────────▼──────────────▼─────────────────────────────┐
│                       Service Layer                               │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐│
│  │ GeminiProvider  │ │ OpenTargets    │ │     PubMed             ││
│  │                 │ │   Service      │ │     Service            ││
│  │ • Gemini API    │ │                │ │                        ││
│  │ • Default/FB    │ │ • GraphQL      │ │ • E-utilities          ││
│  │ • JSON mode     │ │ • Drug/Disease │ │ • Multi-strategy query ││
│  │ • Auto-retry    │ │ • Cached       │ │ • XML parsing          ││
│  └────────────────┘ └────────────────┘ └────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                        Data Layer                                 │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              UnifiedRunState (Pydantic)                     │   │
│  │                                                            │   │
│  │  Entities │ Mechanisms │ Literature │ Claims │ Scorecard   │   │
│  │  Logs     │ Rerun History │ Final Report │ Provenance      │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. User enters drug + disease → `UnifiedRunState` created
2. **Wave 1**: `EntityResolutionAgent` resolves entities → `MechanismAgent` finds common targets
3. If ambiguous → UI shows resolution stage → user selects → continues
4. **Wave 2**: `LiteratureAgent` retrieves papers → `SynthesisCriticAgent` generates claims
5. `EvidenceVerifier` verifies each claim at the evidence level
6. `QualityGate` evaluates scorecard → finalize or targeted rerun
7. `ReportBuilder` assembles the 11-section report
8. UI displays results across 7 tabs

## Quality Gate Flow

```
SynthesisCritic → Scorecard → Quality Gate Decision
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                     score >= 0.70       score < 0.70
                          │                   │
                      FINALIZE           Check rerun budget
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                               budget OK            exhausted
                                    │                   │
                              Targeted rerun      Force finalize
                              (weak agents only)
```

## Claim Provenance

Every claim carries a `ClaimEvidenceBundle`:
- Paper evidence (PMID, snippet, polarity, verification status)
- Mechanism evidence (target, action, disease score)
- Retrieval queries used
- Source agent name
- Source run/rerun ID
- Timestamp
