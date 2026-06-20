# Scale-To-50/100 Full-Agent Evaluation Plan

## Purpose

The 20-pair full-agent run was useful for debugging the OrphanCure evaluation
harness, claim verification, and failure modes, but it is too small for reliable
threshold calibration or stable conclusions about alternative scoring. Phase
6C-D found that the raw LLM-derived confidence score was poorly calibrated
against repoDB proxy labels, while a transparent `safety_penalized_score` looked
better. That finding may be real, or it may be an artifact of a small selected
sample. Phase 6F tests whether it holds when the benchmark is scaled.

## Why 50 Pairs Is The Minimum Next Step

Fifty pairs is the smallest practical next step because Open Targets and PrimeKG
features currently cover 50 benchmark rows. It is large enough to include more
dev rows for threshold selection, more negative_or_failed rows, more
partial-success/failure opportunities, and a broader range of evidence
availability. It also keeps full-agent runtime and LLM cost bounded.

## Why 100 Pairs Is Preferable

One hundred pairs is preferable if runtime and cost allow because it gives a
larger dev set, better label-balance checks, and a more credible estimate of
whether `safety_penalized_score`, triage abstention, and verifier effects remain
stable. A 100-pair run should ideally be preceded by expanding PubMed, Open
Targets, and graph features to 100 pairs, so the scaled run does not become a
missing-evidence stress test only.

## Pair Selection

Pairs are selected deterministically from `data/benchmark/repodb_pairs.csv`,
`data/benchmark/repodb_split.csv`, and
`data/benchmark/unified_benchmark_features.csv`.

Selection priorities:

1. `pubmed_available = true`
2. `opentargets_available = true`
3. `graph_available = true`
4. completed or available extracted evidence features
5. balanced `expected_label`
6. enough `dev` rows for calibration

The selector ranks rows by an evidence availability score, then applies
label-balanced and split-aware quotas. It does not use previous full-agent
correctness, so it does not select only easy or previously successful cases.
Selected `pair_id` values are saved under `eval_results/full_pipeline/`.

## Dev/Test Preservation

The existing repoDB split is preserved. The selected scaled cohorts include both
`dev` and `test` rows and aim for roughly 20 percent dev rows while preserving
50/50 positive versus negative_or_failed label balance where possible.

## Threshold Calibration Without Leakage

Thresholds are selected on `dev` rows only. Test rows are used only for final
reporting. If the dev subset is still too small or lacks both labels, the
calibration artifact must be marked exploratory. The final test set must not be
used to choose thresholds, scoring formulas, triage bands, or report wording.

## Metrics To Report

For each real scaled run, report:

- selected, completed, partial_success, and failed counts
- original full confidence accuracy, precision, recall, F1, and ROC-AUC
- best dev-calibrated threshold and test metrics
- alternative score metrics for `evidence_strength_score`,
  `clinical_support_score`, `safety_penalized_score`, `pubmed_only`, and
  `combined_structured_literature`
- triage coverage, abstention, and accuracy/precision/recall/F1 on covered rows
- TP, TN, FP, FN, partial, and skipped counts
- citation verified rate and unsupported claim rate
- full versus `no_verifier` unsupported-claim rate
- runtime and any available cost estimate

## Evidence Expansion Before Scaling

PubMed coverage should be expanded from 20 pairs to at least 50 pairs before the
50-pair full-agent run. If `PUBMED_EMAIL` is not configured, the PubMed
expansion must not fabricate PMIDs and should remain explicitly not run. For 100
pairs, PubMed, Open Targets, and graph coverage should be expanded to 100 pairs
if feasible.

## Limitations

- repoDB labels are proxy approved/failed labels, not clinical truth.
- PubMed co-mentions are not evidence of efficacy.
- Open Targets and graph connectivity are evidence features, not clinical
  validation.
- LLM-generated full-agent reports require manual biomedical review.
- Threshold calibration remains exploratory until enough dev rows are available.
- Scaling improves statistical reliability, but it does not make OrphanCure a
  clinical decision-support system.
