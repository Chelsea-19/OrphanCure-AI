# OrphanCure: Benchmark-Driven Evidence Assessment for Rare-Disease Drug Repurposing

## 1. Project Overview

OrphanCure is a research-engineering project for evaluating drug-disease
repurposing hypotheses with traceable biomedical evidence. Given a drug-disease
pair, the system organizes benchmark labels, target evidence, graph mechanism
features, and deterministic baseline scores into an auditable evaluation
workflow.

Rare-disease repurposing matters because many rare conditions have limited
commercial incentives for de novo drug development, while existing drugs may
already have relevant biological mechanisms or clinical histories. OrphanCure
does not claim to validate treatments. It provides a structured way to assemble
evidence and measure simple baselines before building more complex agentic
systems.

The final Phase 5 system includes a repoDB approved/failed proxy benchmark, an
Open Targets evidence layer, a PrimeKG graph mechanism layer, a unified feature
table, deterministic baseline and ablation evaluation, bilingual documentation,
case-study templates, and a deployable Streamlit demo package.

## 2. Motivation

Rare-disease drug repurposing is evidence-fragmented. Literature may mention
case reports or mechanism hypotheses, target databases may connect diseases to
genes, and knowledge graphs may encode broad biomedical relationships. A large
language model can summarize this material, but direct free-form generation is
not enough for reliable research engineering: evidence needs provenance,
coverage accounting, benchmark labels, and ablation-friendly metrics.

OrphanCure therefore prioritizes benchmark-driven evaluation. The project first
asks what can be measured from real public data, then adds richer evidence
layers and baseline comparisons without fabricating full-agent results.

## 3. Task Definition

Input: a drug-disease pair.

Output: an evidence-supported repurposing assessment and benchmark features,
including repoDB proxy label, Open Targets support features, PrimeKG graph
features, baseline confidence scores, predicted labels for deterministic
baselines, and evaluation metrics.

Current evaluated scope: evidence-only baselines over the 50 pairs with both
Open Targets and graph features available. These are not full clinical
predictions and are not full OrphanCure agent results.

## 4. System Architecture

The current architecture has five evaluated layers:

1. repoDB label benchmark: maps approved indications to `positive` and selected
   failed or discontinued indications to `negative_or_failed`.
2. Open Targets evidence layer: resolves drugs and diseases, extracts disease
   targets, drug targets, target overlap, and support scores.
3. PrimeKG graph mechanism layer: normalizes graph nodes and edges, maps
   drug/disease names, extracts short graph paths, and computes connectivity
   features.
4. Unified feature table: left-joins repoDB, Open Targets, and PrimeKG features
   by `pair_id`, preserving every repoDB row.
5. Deterministic baseline scoring: evaluates transparent evidence-only modes
   against repoDB proxy labels.

The broader OrphanCure agent pipeline adds PubMed retrieval, evidence synthesis,
verifier checks, target expansion, and structured report generation. Phase 6C-B
ran a real 5-pair full-agent smoke evaluation; report-only modes remain
`TODO_NOT_RUN`.

## 5. Data Sources

### 5.1 repoDB

repoDB provides approved and failed drug-indication pairs and is used as a
proxy approved/failed benchmark. The local Phase 1 dataset was downloaded from
Figshare, normalized, balanced, and split into development and test subsets.

### 5.2 Open Targets

Open Targets Platform GraphQL API is used as an external target-evidence layer.
It provides entity resolution, disease-associated targets, drug target
mechanisms when available, and target overlap features. Open Targets support is
not clinical truth.

### 5.3 PrimeKG

PrimeKG is used as a biomedical knowledge graph for mechanism-oriented
connectivity features. Graph paths and connectivity scores are interpreted as
mechanism support only, not proof of efficacy.

### 5.4 PubMed

The broader OrphanCure system includes PubMed-oriented retrieval and evidence
summarization components. Phase 6B implements a PubMed-only baseline module and
CLI, and Phase 6B-B runs a real 20-pair NCBI PubMed smoke evaluation. Phase
6C-B then uses PubMed retrieval inside the full-agent smoke run.

### 5.5 Provenance And Metadata

The project records source paths, source identifiers, row counts, status fields,
and metadata files where available. Large raw external files are not bundled in
the release package; reproducibility instructions tell users how to download
repoDB and PrimeKG themselves.

## 6. Benchmark Design

### 6.1 repoDB Approved/Failed Benchmark

repoDB labels provide the benchmark target:

- `positive`: approved indications.
- `negative_or_failed`: terminated, withdrawn, suspended, failed, or
  no-development indications.

These labels are proxy labels. Trial failure can reflect safety, operations,
funding, endpoints, or other non-mechanistic reasons.

### 6.2 Open Targets Evidence Layer

Open Targets evaluates whether the drug and disease can be resolved and whether
drug targets overlap disease-associated targets. It measures evidence support,
not clinical success.

### 6.3 PrimeKG Graph Mechanism Layer

PrimeKG evaluates whether drug and disease graph nodes can be mapped and whether
short paths exist between them. Short paths can indicate biological
connectivity, but not therapeutic efficacy.

### 6.4 Unified Benchmark Table

The unified table preserves all 200 repoDB pairs with columns for labels,
splits, availability flags, Open Targets features, graph features, unified
status, and notes. Missing evidence is retained and counted.

## 7. Method

### 7.1 repoDB Preparation And Label Mapping

The repoDB adapter normalizes common drug, disease, ID, and status columns.
Approved statuses are mapped to `positive`. Selected failed or discontinued
statuses are mapped to `negative_or_failed`. Ambiguous statuses are excluded by
default rather than forced into labels.

### 7.2 Open Targets Entity Resolution And Evidence Extraction

For each selected repoDB pair, the Open Targets API resolves drug and disease
entities, retrieves disease-associated targets and drug mechanisms, and
calculates target overlap and support scores. Rows are retained when resolution
is partial.

### 7.3 PrimeKG Graph Normalization

PrimeKG edges are normalized into node and edge tables with standard node IDs,
names, types, relations, and graph source fields.

### 7.4 Graph Mapping And Path Extraction

Drug and disease names are mapped to graph nodes using deterministic exact-name
and synonym matching. Short paths up to length 4 are extracted when both nodes
are mapped. Path counts and connectivity scores are computed from path length
and path type.

### 7.5 Unified Feature Construction

The unified builder left-joins repoDB pairs, Open Targets features, and graph
features by `pair_id`. It preserves all repoDB pairs and marks missing evidence
through `opentargets_available`, `graph_available`, `unified_status`, and
notes.

### 7.6 Baseline Scoring

The implemented deterministic modes are:

| Mode | Score |
|---|---|
| `opentargets_only` | `opentargets_support_score` |
| `graph_only` | `graph_connectivity_score` |
| `ot_plus_graph` | `0.6 * minmax(OT support) + 0.4 * minmax(graph connectivity)` |
| `heuristic_combined` | weighted OT support, target overlap, graph path availability, graph connectivity, and a missing disease-mapping penalty |

Thresholds are selected on the development split only when sufficient dev rows
and both classes are available. Test rows are not used for threshold tuning.

### 7.7 Ablation Framework

The ablation suite runs implemented evidence-only modes, PubMed modes, and
full-agent smoke modes when real output files exist. Missing report-only modes
remain `TODO_NOT_RUN`, which prevents accidental fabrication of results.

## 8. Evaluation Metrics

### 8.1 repoDB Label Metrics

Metrics include accuracy, precision, recall, F1, ROC-AUC when both classes and
numeric scores are available, confusion matrix, evaluated pair count, and
skipped pair count.

### 8.2 Open Targets Coverage Metrics

Open Targets metrics include drug resolution, disease resolution, target
overlap, and support score summaries.

### 8.3 PrimeKG Graph Metrics

Graph metrics include drug mapping, disease mapping, both-mapped rate, path
recovery, shortest path length, and graph connectivity score.

### 8.4 Unified Baseline Metrics

Unified metrics combine evidence coverage and repoDB label metrics for each
baseline mode.

## 9. Results

### repoDB Preparation Summary

| Metric | Value |
|---|---:|
| Source | Figshare repoDB |
| Prepared pairs | 200 |
| Positive pairs | 100 |
| Negative or failed pairs | 100 |
| Dev split | 40 |
| Test split | 160 |
| Validation | Passed |
| Metadata and SHA256 | Recorded |

### Open Targets Enrichment Summary

| Metric | Value |
|---|---:|
| repoDB pairs enriched | 50 |
| Successful | 33 |
| Partial success | 17 |
| Failed | 0 |
| Drug resolution rate | 1.00 |
| Disease resolution rate | 0.82 |
| Target overlap rate | 0.18 |
| Mean Open Targets support score | 0.058937472016996055 |

### PrimeKG Graph Summary

| Metric | Value |
|---|---:|
| Normalized nodes | 84,289 |
| Normalized edges | 4,130,337 |
| repoDB pairs processed | 50 |
| Graph path rows | 9 |
| Drug mapping rate | 0.98 |
| Disease mapping rate | 0.16 |
| Both mapped rate | 0.16 |
| Path recovery rate | 0.12 |
| Mean shortest path length | 1.5 |
| Mean graph connectivity score | 0.118 |

### Unified Evidence Coverage

| Metric | Value |
|---|---:|
| Unified rows | 200 |
| Both evidence layers available | 50 |
| Missing evidence rows | 150 |
| Open Targets availability | 0.25 |
| Graph availability | 0.25 |
| Both layers available | 0.25 |
| Open Targets disease resolution | 0.82 |
| Graph disease mapping | 0.16 |
| Target overlap | 0.18 |
| Graph path recovery | 0.12 |

### Baseline Comparison

| Mode | Accuracy | Precision | Recall | F1 | ROC-AUC | Evaluated | Skipped |
|---|---:|---:|---:|---:|---:|---:|---:|
| `opentargets_only` | 0.50 | 0.50 | 1.00 | 0.667 | 0.5216 | 50 | 150 |
| `graph_only` | 0.50 | 0.50 | 1.00 | 0.667 | 0.5432 | 50 | 150 |
| `ot_plus_graph` | 0.50 | 0.50 | 1.00 | 0.667 | 0.5664 | 50 | 150 |
| `heuristic_combined` | 0.50 | 0.50 | 1.00 | 0.667 | 0.5712 | 50 | 150 |
| `pubmed_only` | 0.588 | 0.533 | 1.00 | 0.696 | 0.6528 | 17 | 3 |
| `combined_structured_literature` | 0.55 | 0.545 | 0.60 | 0.571 | 0.56 | 20 | 180 |
| `full` | 0.50 | 0.667 | 0.667 | 0.667 | 0.00 | 4 | 1 |
| `no_verifier` | 0.75 | 0.75 | 1.00 | 0.857 | 0.50 | 4 | 1 |
| `no_target_expansion` | 0.50 | 0.667 | 0.667 | 0.667 | 0.00 | 4 | 1 |
| `no_graph_features` | 0.50 | 0.667 | 0.667 | 0.667 | 0.50 | 4 | 1 |

### Ablation Status

| Ablation | Status |
|---|---|
| `opentargets_only` | Completed |
| `graph_only` | Completed |
| `ot_plus_graph` | Completed |
| `heuristic_combined` | Completed |
| `pubmed_only` | Completed on 20-pair PubMed smoke run |
| `combined_structured_literature` | Completed on 20 rows with PubMed, Open Targets, and graph features |
| `full` | Completed on 5-pair full-agent smoke run |
| `no_verifier` | Completed on 5-pair full-agent smoke run |
| `no_target_expansion` | Completed on 5-pair full-agent smoke run |
| `no_graph_features` | Completed on 5-pair full-agent smoke run |
| `pubmed_only_report` | TODO_NOT_RUN |
| `structured_only_report` | TODO_NOT_RUN |

## 10. Interpretation

The deterministic evidence-only baselines show weak ranking signal against
repoDB proxy labels. Combining Open Targets and graph features slightly improves
ROC-AUC over either layer alone, but the effect is small.

The threshold selected from the dev split produced all-positive predictions for
the evidence-covered subset, yielding 0.50 accuracy on a balanced set. This is
important: mechanistic evidence and target support can exist for both approved
and failed indications. These features alone are insufficient for clinical
success prediction.

The result should be interpreted as an evaluation framework, not a validated
clinical prediction engine.

## 11. Error Analysis

PrimeKG disease mapping is the largest coverage bottleneck: only 16% of the 50
processed pairs had disease mapping. This limits graph path recovery and
combined scoring.

Open Targets disease resolution is stronger but still incomplete. Target
overlap is low at 18%, which is expected for conservative target matching and
heterogeneous indications.

Graph connectivity can be broad. Short paths may reflect general biological
relationships rather than a specific drug mechanism for a disease.

repoDB negatives are proxy labels. A failed trial can still have plausible
mechanistic evidence, while an approved indication can lack strong target
overlap in Open Targets. This explains why evidence-only baselines can rank
weakly against approved/failed labels.

## 12. Case Study Templates

Manual case studies have not yet been reviewed. The project includes templates
for:

1. Approved positive pair: `TODO_MANUAL_REVIEW`.
2. Failed or negative pair: `TODO_MANUAL_REVIEW`.
3. Mechanistically plausible but clinically uncertain pair:
   `TODO_MANUAL_REVIEW`.

Each template separates repoDB label, Open Targets evidence, PrimeKG paths,
PubMed evidence, interpretation, safety notes, and manual review status.

## 13. Limitations

- The current unified evidence features cover 50 of 200 repoDB pairs.
- repoDB labels are proxy labels, not clinical truth.
- Open Targets support is target evidence support, not clinical validation.
- PrimeKG connectivity is mechanism support, not proof of efficacy.
- Disease normalization is currently conservative.
- Full-agent results currently cover only a 5-pair smoke run, with one failed
  pair.
- `pubmed_only_report` and `structured_only_report` remain TODO_NOT_RUN.
- PubMed co-mention scoring is not evidence polarity classification; the
  20-pair run retrieved 461 unique PMIDs globally, but publication count can
  reflect research attention rather than drug efficacy.
- No case study has been manually reviewed for biomedical correctness.

## 14. Future Work

- Expand Open Targets and graph coverage from 50 to all 200 repoDB pairs.
- Add fuzzy disease normalization with MONDO, UMLS, MeSH, or Disease Ontology.
- Expand PubMed-only retrieval beyond the current 20-pair smoke run.
- Debug the repeated failed full-agent pair.
- Scale the full OrphanCure pipeline from 5 pairs to 20-50 pairs.
- Run `pubmed_only_report` and `structured_only_report` report-generation modes.
- Add manual evidence review for 3-5 case studies.
- Deploy and test the public Streamlit demo.
- Add stronger calibration and ranking metrics after full-agent predictions are
  available.

## 15. Safety And Medical Disclaimer

OrphanCure is for research and educational purposes only. It is not medical
advice, clinical decision support, or a substitute for professional biomedical,
clinical, or regulatory review. Open Targets support and PrimeKG graph
connectivity must not be interpreted as evidence that a drug is safe or
effective for a disease.

## Phase 6C Full-Pipeline Evaluation Addendum

Phase 6C moves the project from evidence-only baselines toward full agent
evaluation. The current full pipeline entry point is
`app/orchestrator/pipeline.py::Pipeline.run_full()`, which orchestrates entity
resolution, mechanism discovery, PubMed literature retrieval, LLM
synthesis/critique, claim verification, quality gating, and report generation.

The Phase 6C evaluation harness adds:

- `app/evaluation/full_pipeline_eval.py`
- `scripts/run_full_pipeline_eval.py`
- `docs/full_pipeline_entrypoint.md`

Supported modes are `full`, `no_verifier`, `no_target_expansion`,
`no_graph_features`, `pubmed_only_report`, and `structured_only_report`.

Current status: Phase 6C-B ran a real 5-pair full-agent smoke evaluation. Full
mode completed 4 pairs and failed 1 pair. The completed full-mode rows had
accuracy 0.5, F1 0.6666666666666666, ROC-AUC 0.0, citation verified rate 1.0,
unsupported claim rate 0.0, and mean runtime 18.4490972999949 seconds.

This distinction matters for interpretation. Evidence-only baselines compare
transparent numeric features against repoDB proxy labels. PubMed-only measures
literature co-mention signal. The full OrphanCure agent would evaluate the
report-generation and verification loop, including claim support and citation
verification rates. The current result is a smoke test only; it is not a
validated biomedical performance estimate and needs manual review before case
study use.

## Phase 6C-C Debug And Scale-Up Addendum

The repeated failed pair from Phase 6C-B was:

- `repodb_0ee62470d8ffb2ae`
- Cisplatin / Esophageal neoplasm metastatic

The root cause was missing Open Targets drug details during mechanism discovery:
`state.drug_data` was `None`, and `MechanismAgent._extract_drug_targets()`
called `.get(...)` on it. The fix treats missing Open Targets drug or disease
details as missing evidence, logs warnings, and continues with zero targets
instead of crashing.

After the fix, the 5-pair rerun completed all 5 pairs. The full-agent evaluation
was then scaled to 20 selected pairs.

| Mode | Completed | Partial | Failed | Accuracy | F1 | ROC-AUC | Citation Verified | Unsupported Claims |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `full` | 16 | 4 | 0 | 0.4375 | 0.4 | 0.46825396825396826 | 0.78125 | 0.0625 |
| `no_verifier` | 16 | 4 | 0 | 0.375 | 0.375 | 0.40476190476190477 | 0.0 | 1.0 |
| `no_target_expansion` | 15 | 5 | 0 | 0.4666666666666667 | 0.5 | 0.4642857142857143 | 0.7708333333333333 | 0.14583333333333331 |
| `no_graph_features` | 16 | 4 | 0 | 0.5 | 0.5 | 0.5 | 0.75 | 0.08333333333333333 |

The main interpretation is not that the full pipeline is clinically predictive.
Rather, the verifier materially reduces unsupported claims compared with
`no_verifier`, while label metrics remain weak and unstable on the selected
20-pair subset.

## Case Study Analysis

Phase 6D converts the completed 20-pair full-agent outputs into manually
reviewable case-study artifacts. The purpose is to make evidence provenance,
claim verification, and failure modes inspectable for GitHub documentation and
interview discussion. These case studies are not clinical recommendations and
remain marked `TODO_MANUAL_REVIEW`.

| Case | pair_id | Drug | Disease | repoDB Label | Full Prediction | Case Type | Manual Review |
|---|---|---|---|---|---|---|---|
| 1 | `repodb_0557bc43eff59f45` | Theophylline | Asthma | `positive` | `positive` | `correct_positive` | `TODO_MANUAL_REVIEW` |
| 2 | `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `negative_or_failed` | `negative_or_failed` | `correct_negative_or_failed` | `TODO_MANUAL_REVIEW` |
| 3 | `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `negative_or_failed` | `positive` | `verifier_effect` | `TODO_MANUAL_REVIEW` |
| 4 | `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `negative_or_failed` | `positive` | `incorrect_but_informative` | `TODO_MANUAL_REVIEW` |
| 5 | `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `negative_or_failed` | `unknown` | `partial_success_error_analysis` | `TODO_MANUAL_REVIEW` |

The selected cases demonstrate three important properties of OrphanCure. First,
completed reports can be traced back to PubMed, Open Targets, PrimeKG, and
claim-verification outputs through preserved `pair_id` values. Second, the
verifier changes report reliability by reducing unsupported claims relative to
`no_verifier`, even when repoDB label metrics remain weak. Third, incorrect and
partial-success cases are valuable: they show where repoDB proxy labels,
literature co-mentions, structured mechanism evidence, and generated reports can
disagree.

The case-study files are stored in `docs/case_studies/`:

- `case_inventory.csv`
- `selected_cases.csv`
- `case_01_correct_positive.md`
- `case_02_correct_negative_or_failed.md`
- `case_03_verifier_effect.md`
- `case_04_incorrect_but_informative.md`
- `case_05_partial_success_optional.md`
- `case_studies_en.md`
- `case_studies_zh.md`

Every case file includes a manual review checklist. The checklist is intentionally
unchecked until repoDB rows, PubMed abstracts, Open Targets mappings, PrimeKG
paths, generated claims, and citations have been reviewed by a qualified human
reviewer.
