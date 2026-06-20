# OrphanCure

**A benchmark-driven research demo for rare-disease drug repurposing evidence assessment.**

OrphanCure integrates repoDB proxy labels, Open Targets target evidence, and
PrimeKG graph mechanism features into a transparent evaluation framework. It is
designed for research portfolios, technical interviews, and future biomedical
AI-agent experiments.

## What This Project Does

Given a drug-disease pair, OrphanCure is designed to assemble evidence from:

- repoDB approved/failed proxy labels,
- Open Targets target and disease evidence,
- PrimeKG biomedical graph connectivity,
- future PubMed and verifier-based agent outputs.

The current release includes evaluated deterministic evidence-only baselines and
a Streamlit demo that summarizes the benchmark and results.

## Why It Matters

Rare-disease drug repurposing evidence is fragmented across literature,
databases, and knowledge graphs. OrphanCure demonstrates how to structure that
evidence into a benchmark-driven workflow instead of relying on unsupported
free-form model generation.

## Architecture

```text
repoDB proxy labels
Open Targets target evidence
PrimeKG graph mechanisms
        |
        v
Unified benchmark table
        |
        v
Deterministic baselines and ablations
        |
        v
Reports and Streamlit research demo
```

## Benchmark Design

| Layer | Role |
|---|---|
| repoDB | Proxy approved/failed drug-indication benchmark |
| Open Targets | Target evidence support layer |
| PrimeKG | Graph mechanism support layer |
| PubMed | Literature co-mention baseline, implemented but live run pending |
| Unified table | Left-joined feature table preserving every `pair_id` |
| Ablation suite | Transparent baseline comparison and TODO tracking |

## Current Results

| Mode | Accuracy | F1 | ROC-AUC |
|---|---:|---:|---:|
| `opentargets_only` | 0.50 | 0.667 | 0.5216 |
| `graph_only` | 0.50 | 0.667 | 0.5432 |
| `ot_plus_graph` | 0.50 | 0.667 | 0.5664 |
| `heuristic_combined` | 0.50 | 0.667 | 0.5712 |

These are sanity baselines on the 50 evidence-covered pairs, not strong
predictive models.

PubMed-only is implemented as a transparent retrieval/scoring baseline. The
current smoke run processed 20 pairs, retrieved 461 global unique PMIDs, and
evaluated 17 evidence-available pairs. Co-mentions are not evidence of efficacy.

Full-pipeline evaluation has a runnable harness and a real selected 20-pair run.
Full mode completed 16 pairs, marked 4 as `partial_success`, and had 0 hard
failures after a missing Open Targets mechanism-detail bug was fixed. These
generated reports are research artifacts and require manual biomedical review.

Scaling diagnostics are prepared for 50- and 100-pair cohorts. Phase 6F-B
expanded PubMed to 50 feature rows and ran the real 50-pair full mode plus
`no_verifier` ablation. Full mode completed 42 pairs, marked 8 as
`partial_success`, had F1 `0.5333333333333333`, and unsupported-claim rate
`0.10897435897435898`. `no_verifier` had unsupported-claim rate `1.0`, so the
verifier effect held up at 50 pairs. The release bundle includes public-safe
scaling summaries and figures.

## Web Demo

Run locally:

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The demo launches without API keys in `DEMO_MODE=true`.

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Reproducing Benchmarks

This release folder includes scripts and sample outputs. Full reproduction
requires downloading repoDB and PrimeKG outside this folder.

```bash
python scripts/prepare_repodb_benchmark.py
python scripts/prepare_opentargets_benchmark.py
python scripts/prepare_graph_benchmark.py
python scripts/build_unified_benchmark_table.py
python scripts/run_ablation_suite.py
```

Full-agent evaluation:

```bash
python scripts/run_full_pipeline_eval.py --pairs data/benchmark/repodb_pairs.csv --unified_features data/benchmark/unified_benchmark_features.csv --output_dir eval_results/full_pipeline --max_pairs 20 --mode full --use_cached
```

See `DEPLOYMENT.md` and `docs/evaluation.md` for details.

## Repository Structure

```text
app/                         Streamlit demo
src/orphancure/              Minimal package marker
scripts/                     Benchmark and evaluation scripts
docs/                        Reports, figures, implementation status
eval_results_sample/         Small public-safe sample outputs
data_sample/                 Small benchmark sample files
.streamlit/config.toml       Streamlit display config without secrets
DEPLOYMENT.md                Deployment instructions
```

## Limitations

- repoDB is a proxy approved/failed benchmark, not clinical truth.
- Open Targets support is target evidence support, not clinical validation.
- PrimeKG graph connectivity is mechanism support, not proof of efficacy.
- Full-agent results currently cover only a selected 20-pair run.
- 50-pair scaled full and no_verifier runs are complete; 100-pair scaled
  execution remains TODO_NOT_RUN until explicitly requested.
- Some rows are `partial_success` because they completed without final reports.
- `pubmed_only_report` and `structured_only_report` remain TODO_NOT_RUN.
- PubMed co-mention is not evidence of efficacy and does not classify abstract
  polarity.
- Manual biomedical review is still needed for case studies.

## Case Studies

The release includes public-safe Phase 6D case-study artifacts under
`docs/case_studies/`. They were selected from the 20-pair full-agent run to
illustrate evidence grounding, verifier behavior, incorrect-but-informative
outputs, and partial-success handling.

| pair_id | Drug | Disease | Case Type | Review Status |
|---|---|---|---|---|
| `repodb_0557bc43eff59f45` | Theophylline | Asthma | `correct_positive` | `TODO_MANUAL_REVIEW` |
| `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `correct_negative_or_failed` | `TODO_MANUAL_REVIEW` |
| `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `verifier_effect` | `TODO_MANUAL_REVIEW` |
| `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `incorrect_but_informative` | `TODO_MANUAL_REVIEW` |
| `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `partial_success_error_analysis` | `TODO_MANUAL_REVIEW` |

These are manually reviewable research artifacts. They are not treatment
recommendations and should not be interpreted as clinical evidence.

## Medical Disclaimer

This project is for research and educational purposes only. It is not medical
advice and must not be used for clinical decision-making.

## Citation And Data Source Notes

- repoDB: Brown AS, Patel CJ. A standard database for drug repositioning.
  Scientific Data 4:170029 (2017). doi:10.1038/sdata.2017.29.
- Open Targets Platform GraphQL API.
- PrimeKG: Chandak et al., Scientific Data 10, 67 (2023).

Raw external data is not bundled in this release package.

## License Notice

See `LICENSE_NOTICE.md`. Dataset licenses and terms belong to their respective
providers.
