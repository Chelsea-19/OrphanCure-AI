# Full Pipeline Entry Point

## Current Entry Point

The current OrphanCure application entry point is the Streamlit app in
`app/main.py`. The app constructs:

- `UnifiedRunState` from the user drug-disease input
- `Settings` from environment variables and `.env`
- `GeminiProvider`
- `Pipeline(state, llm, settings)`

The actual full pipeline class is `app/orchestrator/pipeline.py::Pipeline`.
For a drug-disease pair, `Pipeline.run_full()` executes:

1. `run_wave1()`: entity resolution, candidate generation, and mechanism/target discovery.
2. `run_wave2()`: PubMed literature retrieval, LLM synthesis/critique, evidence verification through the quality gate, and final result state.

The quality gate uses `app/verification/evidence_verifier.py::EvidenceVerifier`
to verify claim-level paper evidence against retrieved abstracts.

## Phase 6C Evaluation Wrapper

Phase 6C adds a thin evaluation wrapper rather than rewriting the agent system:

- Reusable module: `app/evaluation/full_pipeline_eval.py`
- CLI script: `scripts/run_full_pipeline_eval.py`

The wrapper selects repoDB pairs with the strongest evidence availability first,
normalizes outputs into a stable CSV schema, saves raw JSON and markdown report
artifacts, and records explicit `TODO_NOT_RUN` rows when required configuration
is missing.

## Required Inputs

- repoDB pairs: `data/benchmark/repodb_pairs.csv`
- Unified features: `data/benchmark/unified_benchmark_features.csv`
- Optional cached evidence from previous phases:
  - Open Targets cache/features
  - PubMed cache/features
  - graph features

## Required API Keys

The full synthesis/report path requires:

- `GEMINI_API_KEY`

PubMed and Open Targets retrieval may use existing code paths and cached data.
For live PubMed retrieval, NCBI requires a real contact email and optionally
`NCBI_API_KEY`, but Phase 6C did not rerun PubMed retrieval directly.

## Output Schema

`scripts/run_full_pipeline_eval.py` writes:

- `eval_results/full_pipeline/raw_outputs/{mode}/{pair_id}.json`
- `eval_results/full_pipeline/reports/{mode}/{pair_id}.md`
- `eval_results/full_pipeline/per_pair_results_{mode}.csv`
- `eval_results/full_pipeline/summary_metrics_{mode}.json`
- `eval_results/full_pipeline/claim_verification_summary.csv`

Normalized per-pair fields include:

- `pair_id`, `drug_name`, `disease_name`, `expected_label`
- `mode`, `predicted_label`, `confidence_score`, `final_assessment`
- claim counts and citation verification rates
- PubMed/Open Targets/graph evidence usage counts
- raw/report artifact paths
- runtime, status, error message, and notes

## Supported Modes

- `full`
- `no_verifier`
- `no_target_expansion`
- `no_graph_features`
- `pubmed_only_report`
- `structured_only_report`

## Current Readiness

The full pipeline is a partial research-agent pipeline, not a production
biomedical system. It can orchestrate entity resolution, mechanism evidence,
literature retrieval, LLM synthesis, claim verification, and quality gating, but
it has not yet been clinically validated and generated reports require manual
biomedical review.

Phase 6C-A demonstrated the missing-configuration path: when `GEMINI_API_KEY`
was absent, artifacts recorded `TODO_NOT_RUN` rather than fabricated
predictions, reports, claims, or metrics.

Phase 6C-B ran a real 5-pair full-agent smoke evaluation after
`GEMINI_API_KEY` was configured. Phase 6C-C then fixed the repeated
mechanism-discovery failure and scaled full-agent evaluation to 20 selected
pairs. Full mode completed 16 pairs, marked 4 as `partial_success`, and had 0
hard failures.
