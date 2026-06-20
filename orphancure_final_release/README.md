# OrphanCure

**Benchmark-driven biomedical AI agent evaluation for drug-disease evidence assessment.**

Status: **Research demo** | **Not medical advice** | **Streamlit-ready**

OrphanCure is a research-support and educational framework for evaluating
drug-disease evidence assessment agents. It integrates repoDB benchmark labels,
PubMed literature retrieval, Open Targets target evidence, PrimeKG graph
mechanism features, LLM-based synthesis, claim verification, ablation analysis,
scaling diagnostics, and manually reviewable case studies.

## What This Project Does

Given drug-disease pairs, OrphanCure organizes benchmark labels and biomedical
evidence signals into an auditable evaluation workflow. The project measures
agent and baseline behavior against repoDB proxy labels, tracks evidence
coverage, compares ablation modes, and highlights safety/faithfulness through
claim verification.

## Why It Is Not Just an LLM Wrapper

- Uses a balanced repoDB benchmark: 200 pairs, 100 positive and 100
  negative_or_failed.
- Adds structured evidence from PubMed, Open Targets, and PrimeKG.
- Runs full-agent and ablation modes, including `no_verifier`,
  `no_target_expansion`, and `no_graph_features`.
- Measures unsupported claim rate, citation verification, alternative scoring,
  triage coverage, and error types.
- Bundles a demo-mode Streamlit app that uses existing public-safe summaries
  without live API calls.

## Architecture

1. Benchmark layer: repoDB labels and dev/test split.
2. Evidence retrieval layer: PubMed, Open Targets, PrimeKG.
3. Agent synthesis layer: entity resolution, mechanism discovery, retrieval,
   LLM synthesis, and report generation.
4. Claim verification layer: checks generated claims against citations.
5. Diagnostics layer: ablations, threshold calibration, safety-penalized
   scoring, triage, and error analysis.
6. Deployment layer: Streamlit demo and GitHub-ready release package.

## Data Sources

| Source | Role | Bundled in this release |
|---|---|---|
| repoDB | Proxy approved/failed benchmark labels | compact sample benchmark files |
| PubMed | Literature retrieval and co-mention features | summary and pair-feature outputs |
| Open Targets | Target evidence and target overlap | summary and pair-feature outputs |
| PrimeKG | Graph mechanism features | compact pair features only |

Raw external data, caches, full PubMed cache, Open Targets cache, and full
PrimeKG graph files are not bundled.

## Evaluation Summary

| Evaluation | Key result |
|---|---:|
| 20-pair full-agent completed / partial / failed | 16 / 4 / 0 |
| 20-pair full original F1 | 0.4000 |
| 50-pair full-agent completed / partial / failed | 42 / 8 / 0 |
| 50-pair full original accuracy | 0.5000 |
| 50-pair full original F1 | 0.5333 |
| 50-pair full original ROC-AUC | 0.5174 |
| 50-pair mean runtime seconds | 28.2992 |

## Key Results

The 50-pair selected cohort contained 25 positive and 25 negative_or_failed
repoDB rows. Evidence availability among selected pairs was PubMed 48/50,
Open Targets 48/50, and graph 48/50.

Main low-F1 causes were false negatives, recall loss, and partial-success rows.
The 50-pair error analysis counted TP 12, TN 9, FP 9, FN 12, and 8 partial rows.

## Safety-Penalized Score Result

The best alternative score on the 50-pair diagnostics was
`safety_penalized_score` with threshold `0.13312792223387354`, accuracy 0.66,
precision 0.625, recall 0.8, F1 0.7018, and ROC-AUC 0.6464.

## Verifier Ablation Result

The verifier effect held up strongly:

| Run | Full unsupported claim rate | no_verifier unsupported claim rate |
|---|---:|---:|
| 20-pair | 0.0625 | 1.0000 |
| 50-pair | 0.1090 | 1.0000 |

## Case Studies

All selected cases remain `TODO_MANUAL_REVIEW`.

| Pair | Drug | Disease | Case type |
|---|---|---|---|
| repodb_0557bc43eff59f45 | Theophylline | Asthma | correct_positive |
| repodb_118c436e16e1ab51 | Paclitaxel | Testicular Germ Cell Tumor | correct_negative_or_failed |
| repodb_04246cb3a1c31ef7 | Progesterone | Premature Birth | verifier_effect |
| repodb_0ee62470d8ffb2ae | Cisplatin | Esophageal neoplasm metastatic | incorrect_but_informative |
| repodb_04ab2c145755011f | Azacitidine | Myelofibrosis due to another disorder | partial_success_error_analysis |

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Demo mode is enabled by default. No API keys are required.

## Streamlit Deployment

On Streamlit Cloud, select this repository and set:

- Main file path: `app/streamlit_app.py`
- Secrets: none required for demo mode
- Optional environment variable: `DEMO_MODE=true`

## Reproduce Evaluation

The release includes scripts and compact sample outputs. Full reproduction may
require downloading external data and configuring optional API keys.

```bash
python scripts/validate_benchmark_files.py
python scripts/prepare_pubmed_baseline.py --help
python scripts/run_full_pipeline_eval.py --help
```

Do not commit raw data, caches, or secrets after rerunning workflows.

## Repository Structure

```text
app/                         Streamlit demo
src/orphancure/              Minimal release package placeholder
scripts/                     Reproducibility and evaluation scripts
docs/technical_report/       English technical report in LaTeX
docs/manuscript/             Manuscript-style LaTeX draft
docs/interview_notes/        Chinese interview-oriented notes
docs/case_studies/           Selected case-study packets
eval_results_sample/         Public-safe evaluation summaries
data_sample/benchmark/       Compact sample benchmark features
```

## Limitations

This is not clinical validation. repoDB labels are proxy approved/failed labels,
not clinical truth. PubMed co-mention is not evidence of efficacy. Open Targets
and PrimeKG are support signals, not proof of therapeutic efficacy. The selected
20- and 50-pair cohorts are small, LLM behavior is dependency-sensitive, and all
generated biomedical case studies require expert manual review.

## Safety Disclaimer

OrphanCure is for research support and education only. It must not be used for
medical advice, treatment recommendation, clinical decision-making, or patient
care.

## Citation and Data Source Notes

Use `CITATION.cff` as the release citation template and replace
`TODO_AUTHOR_NAME` before public publication. Cite repoDB, PubMed/NCBI, Open
Targets, and PrimeKG according to their official guidance when using the full
workflow.
