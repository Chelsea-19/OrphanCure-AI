# OrphanCure Implementation Status

## Completed Modules

- repoDB source download, provenance metadata, label mapping, balanced pair generation, split generation, and validation.
- Open Targets enrichment with real API responses, JSON cache support, entity resolution, target extraction, target overlap, and feature summaries.
- PrimeKG graph loading, normalization, node/edge export, drug/disease mapping, path extraction, and graph feature generation.
- Unified benchmark table construction with left joins by `pair_id` and explicit missing-evidence flags.
- Deterministic baseline evaluation for `opentargets_only`, `graph_only`, `ot_plus_graph`, and `heuristic_combined`.
- Ablation status tracking with future full-pipeline modes marked `TODO_NOT_RUN`.
- PubMed-only baseline module, preparation CLI, validation, evaluation mode,
  unified merge support, and fixture/mock tests.
- Full-pipeline evaluation harness, CLI wrapper, normalized output schema,
  claim-verification metric extraction, and TODO_NOT_RUN handling for missing
  LLM configuration.
- Full-pipeline robustness fix for missing Open Targets mechanism details,
  followed by a 20-pair full-agent scale-up.
- Documentation figures, summary tables, bilingual project reports, case-study templates, and release package scaffolding.

## Generated Data Files

- `data/external/repodb.csv`
- `data/benchmark/repodb_pairs.csv`
- `data/benchmark/repodb_split.csv`
- `data/benchmark/repodb_metadata.json`
- `data/benchmark/opentargets_evidence.csv`
- `data/benchmark/opentargets_pair_features.csv`
- `data/benchmark/graph/graph_nodes_normalized.csv`
- `data/benchmark/graph/graph_edges_normalized.csv`
- `data/benchmark/graph/graph_pair_mappings.csv`
- `data/benchmark/graph/graph_pair_paths.csv`
- `data/benchmark/graph/graph_pair_features.csv`
- `data/benchmark/unified_benchmark_features.csv`
- `data/benchmark/pubmed_pair_features.csv`
- `data/benchmark/pubmed_evidence.csv`

Large raw and generated graph files are not intended for the public release
folder.

## Generated Evaluation Outputs

- `eval_results/opentargets/per_pair_features.csv`
- `eval_results/opentargets/summary_metrics.json`
- `eval_results/opentargets/summary_table.md`
- `eval_results/graph/per_pair_features.csv`
- `eval_results/graph/summary_metrics.json`
- `eval_results/graph/summary_table.md`
- `eval_results/unified/unified_per_pair_results.csv`
- `eval_results/unified/baseline_comparison.csv`
- `eval_results/unified/summary_metrics.json`
- `eval_results/unified/summary_table.md`
- `eval_results/unified/final_project_summary.md`
- `eval_results/pubmed/per_pair_results.csv`
- `eval_results/pubmed/per_pair_features.csv`
- `eval_results/pubmed/summary_metrics.json`
- `eval_results/pubmed/summary_table.md`
- `eval_results/full_pipeline/per_pair_results_full.csv`
- `eval_results/full_pipeline/per_pair_results_no_verifier.csv`
- `eval_results/full_pipeline/per_pair_results_no_target_expansion.csv`
- `eval_results/full_pipeline/per_pair_results_no_graph_features.csv`
- `eval_results/full_pipeline/summary_metrics_full.json`
- `eval_results/full_pipeline/summary_metrics_no_verifier.json`
- `eval_results/full_pipeline/summary_metrics_no_target_expansion.json`
- `eval_results/full_pipeline/summary_metrics_no_graph_features.json`
- `eval_results/full_pipeline/claim_verification_summary.csv`

## Tests Passed

Latest full test command:

```bash
python -m pytest -q -p no:cacheprovider
```

Latest result after Phase 6C-C debugging and scale-up: `109 passed`.

## TODO_NOT_RUN Modules

- `no_verifier`
- `no_target_expansion`
- `no_graph_features`
- `full`
- `pubmed_only_report`
- `structured_only_report`

These modes are intentionally not reported as completed because full OrphanCure
pipeline predictions have not been generated for the benchmark.

Phase 6C-A generated explicit `TODO_NOT_RUN` artifacts for `full` mode when
`GEMINI_API_KEY` was not configured. Phase 6C-B then ran a real 5-pair
full-agent smoke evaluation after the key was configured.

Phase 6C-C full mode after debugging and scaling to 20 pairs:

- selected pairs: 20
- completed pairs: 16
- partial success pairs: 4
- failed pairs: 0
- accuracy: 0.4375
- F1: 0.4
- ROC-AUC: 0.46825396825396826
- citation verified rate: 0.78125
- unsupported claim rate: 0.0625
- mean runtime seconds: 26.606305390014313

The previously failed Cisplatin / Esophageal neoplasm metastatic pair now
completes after missing Open Targets drug details are handled as missing
evidence.

## Known Limitations

- repoDB labels are proxy approved/failed labels, not clinical truth.
- Open Targets support is target evidence support, not proof of clinical
  efficacy.
- PrimeKG graph connectivity is mechanism support, not proof of efficacy.
- Current Open Targets and graph evidence coverage is 50 of 200 pairs.
- Disease mapping in PrimeKG is currently low.
- No manually reviewed case studies are included yet.
- PubMed-only has been run on 20 pairs with 461 unique PMIDs retrieved globally;
  it remains a co-mention baseline and not evidence polarity classification.
- Full-pipeline results currently come from a selected 20-pair run only.
  Report-level metrics are not clinical validation.
- Four full-mode rows are `partial_success` because they completed without a
  final report object.
- Phase 6D case studies are generated for review but remain
  `TODO_MANUAL_REVIEW`.

## Manual Biomedical Review Needed

- Review the 5 selected Phase 6D drug-disease case studies.
- Review repoDB status context and source row.
- Review Open Targets entity resolution and target evidence.
- Review PrimeKG graph paths and edge semantics.
- Review PubMed literature evidence before making any narrative claims.
- Review generated claims and citations before replacing any
  `TODO_MANUAL_REVIEW` status.

## Phase 6D Case-Study Artifacts

Generated review artifacts:

- `docs/case_studies/case_inventory.csv`
- `docs/case_studies/selected_cases.csv`
- `docs/case_studies/case_01_correct_positive.md`
- `docs/case_studies/case_02_correct_negative_or_failed.md`
- `docs/case_studies/case_03_verifier_effect.md`
- `docs/case_studies/case_04_incorrect_but_informative.md`
- `docs/case_studies/case_05_partial_success_optional.md`
- `docs/case_studies/case_studies_en.md`
- `docs/case_studies/case_studies_zh.md`

Selected pairs:

| pair_id | Drug | Disease | Case Type |
|---|---|---|---|
| `repodb_0557bc43eff59f45` | Theophylline | Asthma | `correct_positive` |
| `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `correct_negative_or_failed` |
| `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `verifier_effect` |
| `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `incorrect_but_informative` |
| `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `partial_success_error_analysis` |

## Recommended Next Technical Steps

- Expand Open Targets and PrimeKG feature generation to all 200 pairs.
- Improve disease normalization with MONDO, UMLS, MeSH, or Disease Ontology.
- Add a PubMed-only baseline.
- Expand PubMed-only retrieval from 20 pairs to all 200 pairs.
- Run the full OrphanCure pipeline on a selected 20-50 pair subset.
- Add verifier, target-expansion, and graph-feature ablations.
- Investigate the `partial_success` rows that completed without final reports.
- Scale the full-agent run beyond 20 pairs after report generation is more
  stable.
- Add automated Streamlit smoke checks after deployment.

## Recommended Next Research Steps

- Manually review selected approved, failed, and uncertain cases.
- Compare evidence patterns between approved and failed repoDB pairs.
- Add calibration analysis after full-agent scores exist.
- Distinguish mechanistic plausibility from clinical outcome prediction.

## Website Deployment Status

A Streamlit demo package is prepared under `orphancure_release/`. It launches in
demo mode without API keys and uses sample evaluation outputs. Public deployment
to Streamlit Community Cloud remains a Phase 6 task.
