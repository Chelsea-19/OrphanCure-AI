# OrphanCure Final Project Summary

## Evidence Coverage

| Metric | Value |
|---|---:|
| n_pairs | 200 |
| opentargets_availability_rate | 0.25 |
| graph_availability_rate | 0.25 |
| pubmed_availability_rate | 0.1 |
| both_evidence_layers_available_rate | 0.25 |
| all_three_evidence_layers_available_rate | 0.1 |
| ot_disease_resolution_rate | 0.82 |
| graph_disease_mapping_rate | 0.16 |
| target_overlap_rate | 0.18 |
| graph_path_recovery_rate | 0.12 |
| pubmed_direct_evidence_rate | 0.85 |
| pubmed_clinical_evidence_rate | 0.85 |

## Baseline And Ablation Status

| Mode | Status | Accuracy | F1 | ROC-AUC | Evaluated | Skipped |
|---|---|---:|---:|---:|---:|---:|
| opentargets_only | completed | 0.5 | 0.6666666666666666 | 0.5216 | 50.0 | 150.0 |
| graph_only | completed | 0.5 | 0.6666666666666666 | 0.5432 | 50.0 | 150.0 |
| pubmed_only | completed | 0.55 | 0.64 | 0.56 | 20.0 | 180.0 |
| ot_plus_graph | completed | 0.5 | 0.6666666666666666 | 0.5664 | 50.0 | 150.0 |
| heuristic_combined | completed | 0.5 | 0.6666666666666666 | 0.5712 | 50.0 | 150.0 |
| combined_structured_literature | completed | 0.55 | 0.5714285714285713 | 0.56 | 20.0 | 180.0 |
| full | completed | 0.4375 | 0.4 | 0.46825396825396826 | 16.0 | 4.0 |
| no_verifier | completed | 0.375 | 0.375 | 0.40476190476190477 | 16.0 | 4.0 |
| no_target_expansion | completed | 0.4666666666666667 | 0.5 | 0.4642857142857143 | 15.0 | 5.0 |
| no_graph_features | completed | 0.5 | 0.5 | 0.5 | 16.0 | 4.0 |
| pubmed_only_report | TODO_NOT_RUN | nan | nan | nan | 0.0 | 200.0 |
| structured_only_report | TODO_NOT_RUN | nan | nan | nan | 0.0 | 200.0 |

## Limitations

- repoDB labels are proxy labels, not clinical truth.
- PubMed co-mentions are not evidence of efficacy.
- Open Targets and graph support are mechanism/evidence features, not clinical validation.
- TODO_NOT_RUN rows are intentionally not fabricated.

## Phase 6C-C Full-Pipeline Debug And 20-Pair Scale-Up

The repeated 5-pair failure was traced to mechanism discovery:
Open Targets drug details returned `None` for Cisplatin / Esophageal neoplasm
metastatic, and `MechanismAgent._extract_drug_targets()` called `.get(...)` on
that `None` value. The code now treats missing Open Targets details as missing
evidence, logs a warning, and continues with zero targets.

After the fix, the 5-pair full-mode rerun completed all 5 pairs with no hard
failures.

20-pair full mode:

| Metric | Value |
|---|---:|
| Selected pairs | 20 |
| Completed | 16 |
| Partial success | 4 |
| Failed | 0 |
| Accuracy | 0.4375 |
| Precision | 0.5 |
| Recall | 0.3333333333333333 |
| F1 | 0.4 |
| ROC-AUC | 0.46825396825396826 |
| Citation verified rate | 0.78125 |
| Unsupported claim rate | 0.0625 |
| Mean runtime seconds | 26.606305390014313 |

20-pair full-agent ablations:

| Mode | Completed | Partial | Failed | F1 | Citation Verified | Unsupported Claims |
|---|---:|---:|---:|---:|---:|---:|
| `full` | 16 | 4 | 0 | 0.4 | 0.78125 | 0.0625 |
| `no_verifier` | 16 | 4 | 0 | 0.375 | 0.0 | 1.0 |
| `no_target_expansion` | 15 | 5 | 0 | 0.5 | 0.7708333333333333 | 0.14583333333333331 |
| `no_graph_features` | 16 | 4 | 0 | 0.5 | 0.75 | 0.08333333333333333 |

These are smoke-scale report-generation metrics, not clinical validation.

## Phase 6D Case-Study Selection

Phase 6D inspected all 20 full-mode rows from the completed full-agent run and
selected five representative case studies for manual review.

| pair_id | Drug | Disease | Case Type | Full Status | Review Status |
|---|---|---|---|---|---|
| `repodb_0557bc43eff59f45` | Theophylline | Asthma | `correct_positive` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `correct_negative_or_failed` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `verifier_effect` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `incorrect_but_informative` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `partial_success_error_analysis` | `partial_success` | `TODO_MANUAL_REVIEW` |

Artifacts:

- `docs/case_studies/case_inventory.csv`
- `docs/case_studies/selected_cases.csv`
- `docs/case_studies/case_studies_en.md`
- `docs/case_studies/case_studies_zh.md`
- individual case markdown files under `docs/case_studies/`

These cases demonstrate evidence traceability and verifier behavior, but they
do not establish efficacy or clinical validity. Human biomedical review is still
required before using them as finalized public case analyses.

## Phase 6C-D Full-Pipeline Diagnostics

Phase 6C-D diagnosed the real 20-pair full-agent run without changing labels,
fabricating predictions, or tuning on test rows.

Original full-mode confusion counts:

| Category | Count |
|---|---:|
| TP | 3 |
| TN | 4 |
| FP | 3 |
| FN | 6 |
| partial/skipped | 4 |

The main reason for low F1 was recall loss. There were 6 false negatives and 3
false positives. Five false negatives had no PubMed, Open Targets, or graph
evidence used by the full run, and one was a conservative negative output.
False positives included PubMed-heavy or noisy `negative_or_failed` rows, which
is consistent with repoDB labels being proxy labels rather than clean biological
truth.

Threshold calibration used only dev rows, but only 3 completed dev rows were
evaluable, so calibration is exploratory. The best F1 threshold for the original
full confidence score was `0.55`; on all 16 completed evaluable rows it produced
accuracy `0.5`, precision `0.5714285714285714`, recall `0.4444444444444444`,
F1 `0.5`, and ROC-AUC `0.46825396825396826`.

The best exploratory alternative score was `safety_penalized_score`, with
threshold `0.06473928278103082`, accuracy `0.65`, precision `0.6`, recall
`0.9`, F1 `0.7200000000000001`, and ROC-AUC `0.72` on the 20 selected rows.
This is a transparent feature-score result, not a trained model result.

Triage classification covered 13/20 rows and abstained on 7/20 as
`uncertain_mixed`. Accuracy on covered cases was `0.6153846153846154`. This is
more reliable operationally than forcing every mixed-evidence case into a binary
prediction.

Artifacts:

- `eval_results/full_pipeline/error_analysis_full.csv`
- `eval_results/full_pipeline/confusion_matrix_full.md`
- `eval_results/full_pipeline/threshold_calibration.csv`
- `eval_results/full_pipeline/best_thresholds.json`
- `eval_results/full_pipeline/alternative_score_comparison.csv`
- `eval_results/full_pipeline/triage_classification_full.csv`
- `docs/figures/full_pipeline_threshold_curve.png`

## Phase 6F Scaling Preparation

Phase 6F prepared the next full-agent scale step without overwriting the
original 20-pair run.

Selected cohorts:

| Cohort | Selected | Positive | Negative_or_failed | Dev | Test |
|---|---:|---:|---:|---:|---:|
| 50-pair | 50 | 25 | 25 | 10 | 40 |
| 100-pair | 100 | 50 | 50 | 20 | 80 |

Selection was deterministic, label-balanced, split-aware, and ranked by PubMed,
Open Targets, and graph evidence availability. It did not use previous
full-agent correctness.

`PUBMED_EMAIL` and `GEMINI_API_KEY` were not configured in the current shell, so
PubMed expansion and real scaled full-agent execution were not run. The 50- and
100-pair scaled output directories contain explicit `TODO_NOT_RUN` artifacts;
no scaled predictions, reports, claims, citations, PMIDs, or metrics were
fabricated.

The 20-pair `safety_penalized_score` result remains promising but exploratory.
It is not yet confirmed by a real 50- or 100-pair full-agent run.

Scaling artifacts:

- `docs/scale_to_50_100_plan.md`
- `eval_results/full_pipeline/scaled_selected_pairs_50.csv`
- `eval_results/full_pipeline/scaled_selected_pairs_100.csv`
- `eval_results/scaling_comparison/scaling_summary.csv`
- `eval_results/scaling_comparison/scaling_summary.md`
- `docs/figures/scaling_f1_comparison.png`
- `docs/figures/scaling_roc_auc_comparison.png`
- `docs/figures/scaling_triage_coverage_accuracy.png`
- `docs/figures/scaling_verifier_effect.png`

## Phase 6F-B Real 50-Pair Scaled Evaluation

Phase 6F-B expanded PubMed and ran the real 50-pair full-agent evaluation.

PubMed expansion:

| Metric | Value |
|---|---:|
| Pair feature rows | 50 |
| Evidence rows | 2149 |
| Summed pair unique PMIDs | 1058 |
| Evidence-available pairs | 37 |
| Evidence availability rate | 0.74 |

Full 50-pair mode:

| Metric | Value |
|---|---:|
| Completed | 42 |
| Partial success | 8 |
| Failed | 0 |
| Accuracy | 0.5 |
| Precision | 0.5714285714285714 |
| Recall | 0.5 |
| F1 | 0.5333333333333333 |
| ROC-AUC | 0.5173611111111112 |
| Citation verified rate | 0.7532051282051282 |
| Unsupported claim rate | 0.10897435897435898 |

`no_verifier` 50-pair ablation:

| Metric | Value |
|---|---:|
| Completed | 41 |
| Partial success | 9 |
| Failed | 0 |
| F1 | 0.5531914893617021 |
| Citation verified rate | 0.0 |
| Unsupported claim rate | 1.0 |

Best alternative score:

| Metric | Value |
|---|---:|
| Score | safety_penalized_score |
| Threshold | 0.13312792223387354 |
| Accuracy | 0.66 |
| Precision | 0.625 |
| Recall | 0.8 |
| F1 | 0.7017543859649122 |
| ROC-AUC | 0.6464 |

The `safety_penalized_score` finding is strengthened at 50 pairs because it
again outperformed original full confidence on F1. The verifier effect also
held up: full mode sharply reduced unsupported claims versus `no_verifier`.
These are research-support evaluation metrics, not clinical validation.
