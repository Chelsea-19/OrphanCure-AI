# OrphanCure

OrphanCure is a benchmark-driven biomedical AI research project for rare-disease
drug repurposing evidence assessment. It integrates repoDB proxy labels, Open
Targets target evidence, and PrimeKG graph mechanism features into a unified
evaluation framework with transparent baselines, ablations, documentation, and
a deployable demo package.

OrphanCure is for research and educational use only. It is not medical advice,
clinical decision support, or evidence that any drug is safe or effective for a
disease.

## Project Pitch

Most biomedical agent demos can generate plausible text, but they often lack
real benchmark labels, provenance, and honest failure accounting. OrphanCure
takes the opposite route: it first builds a reproducible benchmark stack, then
evaluates deterministic evidence-only baselines before claiming any full-agent
performance.

Current evaluated scope: evidence-only baselines, a 20-pair PubMed-only smoke
baseline, and a selected 20-pair real full-agent evaluation. Report-only modes
are still marked `TODO_NOT_RUN`.

## Architecture Summary

```text
repoDB approved/failed proxy labels
        +
Open Targets target evidence
        +
PrimeKG graph mechanism features
        |
        v
Unified benchmark feature table
        |
        v
Deterministic baselines + ablation status
        |
        v
Reports, figures, and Streamlit research demo
```

## Benchmark Summary

| Layer | Current Status |
|---|---|
| repoDB | Real Figshare data; 200 balanced pairs; 100 positive and 100 negative_or_failed |
| Open Targets | Real API used; 50 pairs enriched; disease resolution 0.82; target overlap 0.18 |
| PrimeKG | Real graph normalized; 84,289 nodes and 4,130,337 edges; 50 pairs mapped/evaluated |
| Unified benchmark | 200 rows; 50 both_available; 150 missing_evidence |
| PubMed | Real NCBI smoke run on 20 pairs; 461 unique PMIDs retrieved; evidence availability 0.85 |
| Full pipeline | Real 20-pair run; 16 completed, 4 partial_success, 0 failed; reports require manual review |

## Key Current Results

| Mode | Accuracy | F1 | ROC-AUC | Evaluated |
|---|---:|---:|---:|---:|
| `opentargets_only` | 0.50 | 0.667 | 0.5216 | 50 |
| `graph_only` | 0.50 | 0.667 | 0.5432 | 50 |
| `ot_plus_graph` | 0.50 | 0.667 | 0.5664 | 50 |
| `heuristic_combined` | 0.50 | 0.667 | 0.5712 | 50 |
| `pubmed_only` | 0.588 | 0.696 | 0.6528 | 17 |
| `full` | 0.4375 | 0.400 | 0.4683 | 16 |

These are sanity baselines, not strong predictive models. The all-positive
threshold behavior shows that target and graph mechanism evidence alone is not
enough to predict clinical success from repoDB proxy labels.

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-benchmark.txt
```

## Running Locally

Run the original Streamlit app:

```bash
streamlit run app/main.py
```

Run the public release demo:

```bash
cd orphancure_release
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The release demo starts in demo mode without API keys or large data files.

## Preparing Data

Download repoDB:

```bash
python scripts/download_repodb_source.py
```

Prepare repoDB benchmark pairs:

```bash
python scripts/prepare_repodb_benchmark.py --input data/external/repodb.csv --output data/benchmark/repodb_pairs.csv --balanced --max_pairs 200 --seed 42
```

Open Targets enrichment:

```bash
python scripts/prepare_opentargets_benchmark.py --pairs data/benchmark/repodb_pairs.csv --output data/benchmark/opentargets_evidence.csv --features_output data/benchmark/opentargets_pair_features.csv --cache_dir data/external/opentargets_cache/ --max_pairs 50
```

PrimeKG graph preparation requires local PrimeKG files under
`data/external/primekg/`. The full graph is not bundled.

```bash
python scripts/prepare_graph_benchmark.py --graph_source primekg --graph_dir data/external/primekg/ --pairs data/benchmark/repodb_pairs.csv --output_dir data/benchmark/graph/ --max_pairs 50
```

## Running Evaluation

Build the unified table:

```bash
python scripts/build_unified_benchmark_table.py --repodb_pairs data/benchmark/repodb_pairs.csv --opentargets_features data/benchmark/opentargets_pair_features.csv --graph_features data/benchmark/graph/graph_pair_features.csv --output data/benchmark/unified_benchmark_features.csv
```

Run unified baselines:

```bash
python scripts/evaluate_benchmark.py --benchmark unified --mode opentargets_only --input data/benchmark/unified_benchmark_features.csv --output_dir eval_results/unified
python scripts/evaluate_benchmark.py --benchmark unified --mode graph_only --input data/benchmark/unified_benchmark_features.csv --output_dir eval_results/unified
python scripts/evaluate_benchmark.py --benchmark unified --mode ot_plus_graph --input data/benchmark/unified_benchmark_features.csv --output_dir eval_results/unified
python scripts/run_ablation_suite.py --input data/benchmark/unified_benchmark_features.csv --output_dir eval_results/unified
```

Prepare and evaluate the PubMed-only baseline after configuring a real NCBI
contact email:

```bash
python scripts/prepare_pubmed_baseline.py --pairs data/benchmark/repodb_pairs.csv --output data/benchmark/pubmed_pair_features.csv --evidence_output data/benchmark/pubmed_evidence.csv --cache_dir data/external/pubmed_cache --max_pairs 20 --max_results_per_query 20 --email YOUR_EMAIL
python scripts/evaluate_benchmark.py --benchmark pubmed --mode pubmed_only --input data/benchmark/repodb_pairs.csv --pubmed_features data/benchmark/pubmed_pair_features.csv --output_dir eval_results/pubmed --max_pairs 20
```

PubMed-only uses literature co-mention counts and simple keyword query buckets.
The 20-pair smoke run retrieved 461 global unique PMIDs and evaluated 17
evidence-available pairs. It does not classify abstract polarity and does not
make clinical claims.

Run the Phase 6C full-pipeline evaluation wrapper:

```bash
python scripts/run_full_pipeline_eval.py --pairs data/benchmark/repodb_pairs.csv --unified_features data/benchmark/unified_benchmark_features.csv --output_dir eval_results/full_pipeline --max_pairs 20 --mode full --use_cached
```

The Phase 6C-C run processed 20 selected evidence-rich pairs after debugging a
missing Open Targets mechanism-detail failure. Full mode completed 16 pairs,
marked 4 as `partial_success`, and had 0 hard failures. Full-agent reports are
research artifacts and require manual biomedical review.

Prepare Phase 6F scaled 50/100-pair diagnostics without overwriting the
original 20-pair run:

```bash
python scripts/select_scaled_eval_pairs.py
python scripts/build_scaling_comparison.py
```

The generated cohorts are balanced: 50 pairs = 25 positive / 25
negative_or_failed with 10 dev rows; 100 pairs = 50 / 50 with 20 dev rows.
Phase 6F-B expanded PubMed to 50 feature rows and ran the real 50-pair full mode
plus `no_verifier` ablation. Full mode completed 42 pairs, marked 8 as
`partial_success`, had F1 `0.5333333333333333`, and unsupported-claim rate
`0.10897435897435898`. `no_verifier` had unsupported-claim rate `1.0`, so the
verifier effect held up at 50 pairs.

Run tests:

```bash
python -m pytest -q -p no:cacheprovider
```

Latest result: `119 passed` after Phase 6C-D diagnostics.

## Documentation

- [English project report](docs/project_report_en.md)
- [Chinese interview report](docs/project_report_zh.md)
- [Implementation status](docs/implementation_status.md)
- [Evaluation documentation](docs/evaluation.md)
- [Full pipeline entry point](docs/full_pipeline_entrypoint.md)
- [Case studies](docs/case_studies/case_studies_en.md)
- [Deployment guide](orphancure_release/DEPLOYMENT.md)
- [Final project summary](eval_results/unified/final_project_summary.md)

## Release Package

The public-safe release package is under:

```text
orphancure_release/
```

It excludes raw external data, API keys, `.env`, and the full PrimeKG graph.
It includes a demo Streamlit app, sample outputs, documentation, figures, and
reproducibility instructions.

## Limitations

- repoDB is a proxy approved/failed benchmark, not clinical truth.
- Open Targets support is target evidence support, not clinical validation.
- PrimeKG graph connectivity is mechanism support, not proof of efficacy.
- Current Open Targets and graph coverage is 50 of 200 pairs.
- Full-agent results currently cover only a selected 20-pair run.
- 50-pair scaled full and no_verifier runs are complete; 100-pair scaled
  full-agent execution remains TODO_NOT_RUN until explicitly requested.
- Four full-mode rows are `partial_success` because they completed without a
  final report object.
- `pubmed_only_report` and `structured_only_report` remain TODO_NOT_RUN.
- PubMed co-mention is not evidence of efficacy, even when PMIDs are retrieved.
- Phase 6D selected five case-study artifacts for manual review. They are stored
  under `docs/case_studies/` and remain `TODO_MANUAL_REVIEW`.

## Case Studies

Phase 6D selected five representative full-agent outputs:

| pair_id | Drug | Disease | Case Type | Review Status |
|---|---|---|---|---|
| `repodb_0557bc43eff59f45` | Theophylline | Asthma | `correct_positive` | `TODO_MANUAL_REVIEW` |
| `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `correct_negative_or_failed` | `TODO_MANUAL_REVIEW` |
| `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `verifier_effect` | `TODO_MANUAL_REVIEW` |
| `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `incorrect_but_informative` | `TODO_MANUAL_REVIEW` |
| `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `partial_success_error_analysis` | `TODO_MANUAL_REVIEW` |

These cases demonstrate evidence grounding, verifier behavior, incorrect but
informative outputs, and partial-success handling. They do not establish
biomedical validity and should be reviewed by a qualified human before being
used as project showcase examples.

## Medical Disclaimer

This repository is for research and educational purposes only. It must not be
used for clinical decision-making. Drug repurposing hypotheses require
independent expert biomedical, clinical, and regulatory review before any
real-world use.
