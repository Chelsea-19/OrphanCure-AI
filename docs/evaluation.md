# OrphanCure Evaluation Roadmap

This document tracks the benchmark-driven upgrade plan. Evaluation code must not
fabricate biomedical evidence or invent benchmark labels. Every benchmark run
should record source files, identifiers, and metrics artifacts.

## Phase 1: repoDB Preparation

repoDB is the first drug-disease benchmark integrated into OrphanCure. The
original source describes approved indications from DrugCentral and failed
indications from AACT/ClinicalTrials.gov. The final repoDB database contains
approved and failed drug-indication pairs and is distributed through Figshare.

Source metadata:

- Citation: Brown AS, Patel CJ. A standard database for drug repositioning.
  Scientific Data 4:170029 (2017). doi:10.1038/sdata.2017.29
- Data DOI: `10.6084/m9.figshare.c.3462048`
- Expected local fallback file: `data/external/repodb.csv`
- Raw download directory: `data/external/repodb_raw/`
- Source provenance metadata: `data/external/repodb_source_metadata.json`
- Prepared pairs file: `data/benchmark/repodb_pairs.csv`
- Prepared split file: `data/benchmark/repodb_split.csv`
- Prepared metadata file: `data/benchmark/repodb_metadata.json`

The preparation adapter supports common repoDB CSV column names, including:

- Drug name: `drug_name`, `drug`, `drug_label`
- Drug ID: `drug_id`, `drugbank_id`, `chembl_id`
- Disease/indication name: `ind_name`, `indication`, `disease_name`
- Disease/indication ID: `ind_id`, `umls_id`, `cui`, `disease_id`, `efo_id`
- Status: `status`, `indication_status`, `trial_status`

Statuses mapped as `positive`:

- `Approved`
- `Approved indication`

Statuses mapped as `negative_or_failed`:

- `Terminated`
- `Withdrawn`
- `Suspended`
- `Failed`
- `No development`

Ambiguous, unknown, or missing statuses are mapped to `TODO_REVIEW`, then
excluded by default. They are not forced into benchmark labels.

### Prepare repoDB

First try automatic source download:

```bash
python scripts/download_repodb_source.py
```

The downloader tries public sources in this order:

1. Figshare repoDB Final Database
2. Figshare repoDB Data and Code Collection
3. Original authors' GitHub repository, if a suitable CSV is available

If successful, it writes:

- Raw source file under `data/external/repodb_raw/`
- Normalized local source at `data/external/repodb.csv`
- Provenance metadata at `data/external/repodb_source_metadata.json`

Verify provenance metadata before preparing the benchmark:

```bash
python -m json.tool data/external/repodb_source_metadata.json
```

Check the `source_url`, `sha256`, `row_count`, and `column_names` fields.

If automatic download is unavailable or fails, download the final repoDB CSV
manually from the Figshare DOI above and place it at:

```bash
data/external/repodb.csv
```

Prepare the normalized benchmark:

```bash
python scripts/prepare_repodb_benchmark.py \
  --input data/external/repodb.csv \
  --output data/benchmark/repodb_pairs.csv \
  --balanced \
  --max_pairs 200 \
  --seed 42
```

The script also writes:

- `data/benchmark/repodb_split.csv`
- `data/benchmark/repodb_metadata.json`

To try a Figshare metadata-based download first:

```bash
python scripts/prepare_repodb_benchmark.py --download
```

Validate prepared files:

```bash
python scripts/validate_benchmark_files.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --split data/benchmark/repodb_split.csv
```

### Evaluation After Preparation

Create an OrphanCure prediction CSV with at least:

```text
drug_name,disease_name,score
```

Optional but preferred for traceable matching:

```text
drug_id,disease_id
```

Then run the evaluator against the prepared pairs:

```bash
python scripts/evaluate_repodb.py \
  --repodb-path data/benchmark/repodb_pairs.csv \
  --predictions eval_results/predictions.csv \
  --out-dir eval_results/repodb
```

The evaluator writes:

- `eval_results/repodb/metrics.json`
- `eval_results/repodb/matched_predictions.csv`
- `eval_results/repodb/unmatched_predictions.csv`
- `eval_results/repodb/run_config.json`

### Smoke Test

Smoke mode uses tiny toy fixtures in `tests/fixtures/`. These fixtures exercise
parsing, matching, metrics, and artifact writing only. They are not biomedical
benchmark evidence.

```bash
python scripts/evaluate_repodb.py --smoke
```

### Metrics

The Phase 1 runner reports:

- Coverage: fraction of predictions matched to repoDB
- Threshold metrics: accuracy, precision, recall, F1, confusion matrix
- Ranking metrics: ROC AUC, average precision, precision@k, recall@k
- Audit outputs: matched and unmatched prediction rows with repoDB row IDs,
  labels, statuses, source file, citation, and DOI

### Known Limitations

- Matching is deterministic and uses IDs when both sides provide them, otherwise
  normalized names. Name-only matching can miss synonym-equivalent pairs.
- repoDB failed or terminated statuses are not all biological efficacy failures.
  Some failures may reflect trial operations, funding, safety, or other reasons.
- Scores are evaluated as supplied. This script does not run OrphanCure agents or
  generate predictions by itself.
- The toy smoke fixture is not a biomedical validation dataset.

### Manual Biomedical Review Still Needed

- Confirm that the downloaded CSV is the final repoDB release and not a raw
  preprocessing table.
- Review unmatched predictions for synonym, spelling, or identifier mismatches.
- Review false positives and false negatives before treating them as scientific
  conclusions.
- Review repoDB failed pairs before interpreting them as mechanistic or efficacy
  negatives.

## Phase 2: Open Targets Enrichment

Open Targets is used as an external target/disease/drug evidence layer over the
prepared repoDB benchmark. It is not a final clinical truth source. It provides
support features such as entity resolution, disease-associated targets,
drug-target mechanisms when available, known-drug evidence, and target overlap.

Leakage warning: OrphanCure may use Open Targets internally. Therefore Open
Targets enrichment must be interpreted as external support and mechanism
context, not as an independent gold label for model performance.

### Smoke Enrichment

Run a small live-API smoke test:

```bash
python scripts/prepare_opentargets_benchmark.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --output data/benchmark/opentargets_evidence.csv \
  --features_output data/benchmark/opentargets_pair_features.csv \
  --cache_dir data/external/opentargets_cache/ \
  --max_pairs 5
```

This writes:

- `data/benchmark/opentargets_evidence.csv`
- `data/benchmark/opentargets_pair_features.csv`
- JSON cache files under `data/external/opentargets_cache/`

### Cached Mode

Use cached responses and skip the API when a cache entry is missing:

```bash
python scripts/prepare_opentargets_benchmark.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --output data/benchmark/opentargets_evidence.csv \
  --features_output data/benchmark/opentargets_pair_features.csv \
  --cache_dir data/external/opentargets_cache/ \
  --max_pairs 5 \
  --use_cached \
  --skip_api_if_missing
```

Rows with missing cache/API failures are retained with `status` and
`error_message`.

### Open Targets Validation

```bash
python scripts/validate_benchmark_files.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --split data/benchmark/repodb_split.csv \
  --opentargets_evidence data/benchmark/opentargets_evidence.csv \
  --opentargets_features data/benchmark/opentargets_pair_features.csv
```

Validation checks required columns, valid pair IDs, parseable numeric fields,
valid boolean fields, valid statuses, retained failed/unresolved rows, and
matching Open Targets evidence/features pair IDs.

### Open Targets Only Evaluation

This mode does not call PubMed, Gemini, or any LLM. It only summarizes prepared
Open Targets feature tables.

```bash
python scripts/evaluate_benchmark.py \
  --benchmark opentargets \
  --mode opentargets_only \
  --features data/benchmark/opentargets_pair_features.csv \
  --pairs data/benchmark/repodb_pairs.csv
```

Outputs:

- `eval_results/opentargets/per_pair_features.csv`
- `eval_results/opentargets/summary_metrics.json`
- `eval_results/opentargets/summary_table.md`

Metrics include drug/disease resolution rates, target-overlap rate, known-drug
recovery rate, mean Open Targets support score, support grouped by repoDB
`expected_label`, and counts of successful, partial-success, and failed pairs.
The current public GraphQL schema does not expose disease-level `knownDrugs` on
the `Disease` object, so `known_drug_recovery_rate` is retained as a stable
feature but may remain zero unless a supported Open Targets known-drug source is
added later.

### Open Targets Limitations

- Open Targets is updated over time, so cached responses should be preserved for
  reproducibility.
- Not every repoDB drug maps cleanly to a ChEMBL/Open Targets drug entity.
- Not every repoDB indication maps cleanly to an EFO/Open Targets disease entity.
- Target overlap is mechanism support, not clinical validation.
- Known-drug evidence is schema-dependent and may be unavailable in the public
  GraphQL API.
- Failed or unresolved pairs are retained for audit and should be reviewed
  manually.

## Phase 3: Graph Mechanism Benchmark

PrimeKG and PharmKG-style graph files complement repoDB and Open Targets by
testing graph-based mechanistic connectivity. repoDB provides approved/failed
drug-disease labels, Open Targets provides target/disease/drug evidence support,
and graph benchmarks ask whether drug and disease nodes are connected through
short mechanistic paths such as drug-target-disease or drug-gene-disease.

Graph connectivity is mechanism support only. It is not proof of clinical
efficacy, safety, or causal therapeutic effect.

### Local Graph Files

PrimeKG is the preferred first graph source. Place local PrimeKG files under:

```text
data/external/primekg/
```

The preferred file is `kg.csv`, with columns similar to:

```text
relation,x_id,x_type,x_name,y_id,y_type,y_name
```

The PrimeKG GitHub quick-start documents this direct Harvard Dataverse download:

```bash
wget -O data/external/primekg/kg.csv https://dataverse.harvard.edu/api/access/datafile/6180620
```

On Windows PowerShell:

```powershell
Invoke-WebRequest -Uri https://dataverse.harvard.edu/api/access/datafile/6180620 -OutFile data/external/primekg/kg.csv
```

Separate `nodes.csv` and `edges.csv` files are also supported when they contain
standard node and edge columns. PharmKG can be used with:

```bash
--graph_source pharmkg --graph_dir data/external/pharmkg/
```

if local node/edge exports are available.

If files are missing, the script prints manual download instructions and exits.
It does not fabricate graph data and does not use toy fixtures as real graph
data.

### Prepare Graph Outputs

```bash
python scripts/prepare_graph_benchmark.py \
  --graph_source primekg \
  --graph_dir data/external/primekg/ \
  --pairs data/benchmark/repodb_pairs.csv \
  --output_dir data/benchmark/graph/ \
  --max_pairs 10 \
  --max_path_length 4 \
  --top_k_paths 10
```

Outputs:

- `data/benchmark/graph/graph_nodes_normalized.csv`
- `data/benchmark/graph/graph_edges_normalized.csv`
- `data/benchmark/graph/graph_pair_mappings.csv`
- `data/benchmark/graph/graph_pair_paths.csv`
- `data/benchmark/graph/graph_pair_features.csv`

### Validate Graph Outputs

```bash
python scripts/validate_benchmark_files.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --split data/benchmark/repodb_split.csv \
  --graph_nodes data/benchmark/graph/graph_nodes_normalized.csv \
  --graph_edges data/benchmark/graph/graph_edges_normalized.csv \
  --graph_mappings data/benchmark/graph/graph_pair_mappings.csv \
  --graph_paths data/benchmark/graph/graph_pair_paths.csv \
  --graph_features data/benchmark/graph/graph_pair_features.csv
```

Validation checks required columns, valid repoDB `pair_id` references,
parseable numeric fields, valid boolean fields, valid statuses, retained
unmapped rows, and no silent drops between mapping and feature outputs.

### Graph-Only Evaluation

This mode does not call PubMed, Open Targets, Gemini, or other LLMs.

```bash
python scripts/evaluate_benchmark.py \
  --benchmark graph \
  --mode graph_only \
  --input data/benchmark/repodb_pairs.csv \
  --graph_features data/benchmark/graph/graph_pair_features.csv \
  --output_dir eval_results/graph \
  --max_pairs 10
```

Outputs:

- `eval_results/graph/per_pair_features.csv`
- `eval_results/graph/summary_metrics.json`
- `eval_results/graph/summary_table.md`
- `eval_results/graph/case_paths/{pair_id}.json` for selected mapped examples

Metrics include drug and disease mapping rates, both-mapped rate, path recovery
rate, mean shortest path length, mean graph connectivity score, graph support
grouped by repoDB `expected_label`, and status counts.

### Graph Benchmark Limitations

- Name matching is deterministic and conservative; synonym coverage depends on
  the local graph files.
- Short paths can reflect broad biological connectivity rather than a specific
  therapeutic mechanism.
- PrimeKG/PharmKG graph coverage and edge provenance must be reviewed before
  scientific interpretation.
- Graph connectivity may overlap with evidence sources used elsewhere in
  OrphanCure.

## Phase 4: Unified Baselines and Ablations

Phase 4 combines repoDB proxy labels, Open Targets support features, and
PrimeKG/graph connectivity features into one left-joined table. The unified
table preserves every repoDB `pair_id`. Missing Open Targets or graph features
are retained with availability flags and notes rather than silently dropped.

Inputs:

- repoDB labels: `data/benchmark/repodb_pairs.csv`
- repoDB split: `data/benchmark/repodb_split.csv`
- Open Targets features: `data/benchmark/opentargets_pair_features.csv`
- graph features: `data/benchmark/graph/graph_pair_features.csv`

Build the unified table:

```bash
python scripts/build_unified_benchmark_table.py \
  --repodb_pairs data/benchmark/repodb_pairs.csv \
  --opentargets_features data/benchmark/opentargets_pair_features.csv \
  --graph_features data/benchmark/graph/graph_pair_features.csv \
  --output data/benchmark/unified_benchmark_features.csv
```

Run a unified baseline:

```bash
python scripts/evaluate_benchmark.py \
  --benchmark unified \
  --mode heuristic_combined \
  --input data/benchmark/unified_benchmark_features.csv \
  --output_dir eval_results/unified
```

Run the current ablation suite:

```bash
python scripts/run_ablation_suite.py \
  --input data/benchmark/unified_benchmark_features.csv \
  --output_dir eval_results/unified
```

Outputs:

- `eval_results/unified/unified_per_pair_results.csv`
- `eval_results/unified/baseline_comparison.csv`
- `eval_results/unified/summary_metrics.json`
- `eval_results/unified/summary_table.md`
- `docs/figures/unified_baseline_comparison.png`
- `docs/figures/evidence_coverage_summary.png`
- `docs/figures/ot_vs_graph_score_scatter.png`

### Unified Scoring Modes

All Phase 4 scores are deterministic transparent baselines. They do not call
PubMed, Gemini, or any LLM.

- `opentargets_only`: uses `opentargets_support_score`.
- `graph_only`: uses `graph_connectivity_score`.
- `ot_plus_graph`: uses `0.6 * minmax(opentargets_support_score) + 0.4 *
  minmax(graph_connectivity_score)`.
- `heuristic_combined`: combines Open Targets support, target overlap, graph
  path availability, graph connectivity, and a small penalty when graph disease
  mapping is missing.
- `full_placeholder`: records `TODO_NOT_RUN` and does not fabricate full
  OrphanCure pipeline predictions.

Thresholds are selected on the `dev` split only when enough labeled dev rows
and both classes are available. If the dev split is missing or too small, fixed
documented thresholds are used. Test rows are never used for threshold tuning.

### Unified Metrics

For each completed mode, the evaluator reports:

- accuracy, precision, recall, F1
- ROC-AUC when both classes and numeric scores are available
- confusion matrix
- evaluated and skipped pair counts

The unified summary also reports evidence coverage:

- Open Targets availability rate
- graph availability rate
- both evidence layers available rate
- Open Targets disease resolution rate
- graph disease mapping rate
- target overlap rate
- graph path recovery rate

### Unified Limitations

- repoDB is a proxy approved/failed label benchmark. Failed, withdrawn, or
  terminated indications are not guaranteed biological negatives.
- Open Targets support is target evidence support, not clinical truth.
- PrimeKG graph connectivity is mechanism support, not proof of efficacy,
  safety, or clinical utility.
- Short graph paths can reflect broad biomedical connectivity rather than a
  specific therapeutic mechanism.
- Missing evidence is counted explicitly; rows are retained for audit.

## Phase 6B: PubMed-Only Baseline

Phase 6B adds a transparent PubMed co-mention retrieval baseline. This is not
the full OrphanCure agent pipeline and does not use an LLM. It constructs fixed
NCBI E-utilities queries for each drug-disease pair, retrieves PMIDs and article
metadata when API access is configured, caches all responses, and computes
simple literature-count features.

Query types:

- direct: `"{drug_name}" AND "{disease_name}"`
- title/abstract: `"{drug_name}"[Title/Abstract] AND "{disease_name}"[Title/Abstract]`
- clinical: direct query plus `(trial OR clinical OR patient OR therapy)`
- failure/negative: direct query plus `(failed OR failure OR ineffective OR toxicity OR adverse OR discontinued)`
- mechanism: direct query plus `(mechanism OR target OR pathway)`

Feature outputs:

- `data/benchmark/pubmed_pair_features.csv`
- `data/benchmark/pubmed_evidence.csv`

The pair-level score is a deterministic heuristic using `log1p(n_unique_pmids)`
with bonuses for clinical, title/abstract, and mechanism co-mentions, and a
small penalty for negative/failure keyword co-mentions. It is not trained and
does not classify evidence polarity.

Prepare PubMed features:

```bash
python scripts/prepare_pubmed_baseline.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --output data/benchmark/pubmed_pair_features.csv \
  --evidence_output data/benchmark/pubmed_evidence.csv \
  --cache_dir data/external/pubmed_cache \
  --max_pairs 20 \
  --max_results_per_query 20 \
  --email YOUR_EMAIL
```

Validate PubMed outputs:

```bash
python scripts/validate_benchmark_files.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --split data/benchmark/repodb_split.csv \
  --pubmed_features data/benchmark/pubmed_pair_features.csv \
  --pubmed_evidence data/benchmark/pubmed_evidence.csv
```

Evaluate PubMed only:

```bash
python scripts/evaluate_benchmark.py \
  --benchmark pubmed \
  --mode pubmed_only \
  --input data/benchmark/repodb_pairs.csv \
  --pubmed_features data/benchmark/pubmed_pair_features.csv \
  --output_dir eval_results/pubmed \
  --max_pairs 20
```

Current status: the PubMed module, CLI, validation, evaluation mode, unified
merge support, ablation handling, and tests are implemented. A real PubMed API
run was not executed because no `PUBMED_EMAIL` environment variable or email
argument was configured. PubMed results remain `TODO_NOT_RUN` until a real NCBI
run is completed.

### Phase 6B-B Real PubMed Smoke Results

A real PubMed smoke run was executed with the configured contact email provided
for the run. No NCBI API key was configured.

| Metric | Value |
|---|---:|
| repoDB pairs processed | 20 |
| PubMed pair feature rows | 20 |
| PubMed evidence rows | 874 |
| Global unique PMIDs retrieved | 461 |
| Pair rows with PubMed evidence | 17 |
| Pair rows with no PMIDs | 3 |
| Evidence availability rate | 0.85 |

Standalone PubMed-only evaluation, skipping zero-PMID rows:

| Metric | Value |
|---|---:|
| Accuracy | 0.5882352941176471 |
| Precision | 0.5333333333333333 |
| Recall | 1.0 |
| F1 | 0.6956521739130436 |
| ROC-AUC | 0.6527777777777778 |
| Evaluated pairs | 17 |
| Skipped pairs | 3 |

Mean PubMed features by repoDB proxy label:

| Label | Mean unique PMIDs | Mean PubMed evidence score |
|---|---:|---:|
| `negative_or_failed` | 20.6 | 0.6491371726165831 |
| `positive` | 25.5 | 0.6632584194797865 |

The unified ablation suite now includes `pubmed_only` and
`combined_structured_literature`. In unified mode, the 20 PubMed feature rows are
treated as available feature rows, including zero-PMID rows with zero scores.

Limitations:

- PubMed co-mention is not evidence of efficacy.
- Publication counts are biased by disease popularity, drug age, and research
  attention.
- Negative signals are keyword-based and weak.
- Abstracts may be missing.
- `pubmed_evidence_score` is a transparent heuristic, not a trained classifier.

## Phase 6C: Full OrphanCure Pipeline Evaluation

Phase 6C adds an evaluation harness for the full OrphanCure agent pipeline. This
is distinct from the evidence-only baselines:

- evidence-only baselines score prepared Open Targets, graph, or PubMed feature
  tables without generating reports;
- `pubmed_only` is a transparent literature co-mention baseline and does not use
  an LLM;
- the full OrphanCure agent is intended to combine PubMed retrieval, Open
  Targets target evidence, PrimeKG mechanism features, LLM synthesis, claim
  verification, a quality gate, and report generation.

The current app-level entry point is `app/orchestrator/pipeline.py::Pipeline`.
`Pipeline.run_full()` runs entity resolution and mechanism discovery followed by
literature retrieval, synthesis, claim verification, and quality gating. Phase
6C wraps that entry point with:

- `app/evaluation/full_pipeline_eval.py`
- `scripts/run_full_pipeline_eval.py`

Supported modes:

- `full`
- `no_verifier`
- `no_target_expansion`
- `no_graph_features`
- `pubmed_only_report`
- `structured_only_report`

Run the full-pipeline evaluation wrapper:

```bash
python scripts/run_full_pipeline_eval.py \
  --pairs data/benchmark/repodb_pairs.csv \
  --unified_features data/benchmark/unified_benchmark_features.csv \
  --output_dir eval_results/full_pipeline \
  --max_pairs 20 \
  --mode full \
  --use_cached \
  --skip_llm_if_missing
```

Summarize an existing full-pipeline result file:

```bash
python scripts/evaluate_benchmark.py \
  --benchmark full_pipeline \
  --mode full \
  --output_dir eval_results/full_pipeline
```

### Phase 6C-B Real Full-Agent Smoke Run

After configuring `GEMINI_API_KEY`, a real 5-pair full-agent smoke evaluation
was run. The evaluator selected pairs with maximum evidence availability first.

Full mode status:

| Metric | Value |
|---|---:|
| Selected pairs | 5 |
| Completed pairs | 4 |
| Failed pairs | 1 |
| Accuracy | 0.5 |
| Precision | 0.6666666666666666 |
| Recall | 0.6666666666666666 |
| F1 | 0.6666666666666666 |
| ROC-AUC | 0.0 |
| Mean runtime seconds | 18.4490972999949 |

Full mode report/verification metrics:

| Metric | Value |
|---|---:|
| Mean claims | 2.5 |
| Mean verified claims | 2.5 |
| Mean unsupported claims | 0.0 |
| Citation verified rate | 1.0 |
| Unsupported claim rate | 0.0 |
| Mean PMIDs used | 50.75 |
| Mean Open Targets evidence items | 3.0 |
| Mean graph paths used | 3.0 |

The failed pair was retained with `status=failed` and the recorded error message
`'NoneType' object has no attribute 'get'`. This is a pipeline robustness issue,
not a fabricated skip.

Full-agent ablation smoke runs were also executed on the same 5-pair selection:

| Mode | Completed | Failed | Accuracy | F1 | Citation Verified Rate | Unsupported Claim Rate |
|---|---:|---:|---:|---:|---:|---:|
| `full` | 4 | 1 | 0.5 | 0.6666666666666666 | 1.0 | 0.0 |
| `no_verifier` | 4 | 1 | 0.75 | 0.8571428571428571 | 0.0 | 1.0 |
| `no_target_expansion` | 4 | 1 | 0.5 | 0.6666666666666666 | 0.875 | 0.125 |
| `no_graph_features` | 4 | 1 | 0.5 | 0.6666666666666666 | 1.0 | 0.0 |

These results are a tiny smoke test, not a validated performance estimate. The
report-level metrics check generated-output behavior and citation provenance;
they are not clinical validation.

### Phase 6C-C Failure Fix And 20-Pair Scale-Up

The repeated failed pair was:

- `pair_id`: `repodb_0ee62470d8ffb2ae`
- Drug: Cisplatin
- Disease: Esophageal neoplasm metastatic

Root cause: Open Targets returned no drug details for this pair, leaving
`state.drug_data` as `None`. `MechanismAgent._extract_drug_targets()` called
`.get(...)` on that `None` value. The fix treats missing Open Targets details as
missing evidence, logs a warning, and continues with zero drug targets.

After the fix, the same 5-pair full-mode run completed all 5 pairs with no hard
failures.

The full-agent evaluation was then scaled to 20 selected pairs.

| Mode | Completed | Partial | Failed | Accuracy | F1 | ROC-AUC | Citation Verified | Unsupported Claims | Mean Runtime Seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full` | 16 | 4 | 0 | 0.4375 | 0.4 | 0.46825396825396826 | 0.78125 | 0.0625 | 26.606305390014313 |
| `no_verifier` | 16 | 4 | 0 | 0.375 | 0.375 | 0.40476190476190477 | 0.0 | 1.0 | 17.274045099987415 |
| `no_target_expansion` | 15 | 5 | 0 | 0.4666666666666667 | 0.5 | 0.4642857142857143 | 0.7708333333333333 | 0.14583333333333331 | 28.22638708499726 |
| `no_graph_features` | 16 | 4 | 0 | 0.5 | 0.5 | 0.5 | 0.75 | 0.08333333333333333 | 26.566079774999526 |

Interpretation: the most meaningful smoke-run signal remains report
faithfulness, not label accuracy. Compared with `no_verifier`, full mode greatly
reduced unsupported claims. Accuracy and ROC-AUC remain unstable on this small,
selected subset and must not be overinterpreted.

Full-pipeline outputs:

- `eval_results/full_pipeline/raw_outputs/{mode}/{pair_id}.json`
- `eval_results/full_pipeline/reports/{mode}/{pair_id}.md`
- `eval_results/full_pipeline/per_pair_results_{mode}.csv`
- `eval_results/full_pipeline/summary_metrics_{mode}.json`
- `eval_results/full_pipeline/claim_verification_summary.csv`

Full-pipeline metrics, when real reports exist, include:

- accuracy, precision, recall, F1, and ROC-AUC against repoDB proxy labels;
- mean claim counts and verified/unsupported claim counts;
- citation verification and unsupported-claim rates;
- mean PubMed, Open Targets, and graph evidence usage;
- runtime and status rates.

Limitations:

- full-agent reports depend on an LLM API key and may be sensitive to model
  behavior;
- the Phase 6C-B run covers only 5 selected pairs and one pair failed;
- report-level metrics are not clinical validation;
- verifier precision can be imperfect because it checks retrieved-paper
  provenance and quote support, not biomedical truth;
- generated reports require manual biomedical review before inclusion in case
  studies;
- TODO rows are intentionally retained and must not be interpreted as model
  failures or successes.

### Phase 6D Case-Study Review Artifacts

Phase 6D selected five representative outputs from the completed 20-pair
full-agent run and converted them into manually reviewable case-study files.
The artifacts are stored under `docs/case_studies/`:

- `case_inventory.csv`: all 20 full-mode rows with evidence availability,
  verification, and report-presence fields.
- `selected_cases.csv`: the five selected case studies.
- `case_01_correct_positive.md`
- `case_02_correct_negative_or_failed.md`
- `case_03_verifier_effect.md`
- `case_04_incorrect_but_informative.md`
- `case_05_partial_success_optional.md`
- `case_studies_en.md`
- `case_studies_zh.md`

The selected cases cover a correct positive, the closest available correct
`negative_or_failed` case, a verifier-effect case, an incorrect but informative
case, and a partial-success case. All remain marked `TODO_MANUAL_REVIEW`.
These files are meant to support human review of provenance and failure modes;
they are not clinical evidence and must not be presented as treatment
recommendations.

### Phase 6C-D Error Analysis, Calibration, And Triage

Phase 6C-D diagnoses the real 20-pair full-agent run without changing labels,
fabricating predictions, or tuning on the test set. The new diagnostics are
derived from `per_pair_results_full.csv` plus existing unified PubMed/Open
Targets/graph features.

Original full-mode confusion counts over evaluable completed rows:

| Category | Count |
|---|---:|
| TP | 3 |
| TN | 4 |
| FP | 3 |
| FN | 6 |
| partial/skipped | 4 |

The main reason F1 was low was recall loss: 6 false negatives versus 3 false
positives. Five false negatives had no PubMed, Open Targets, or graph evidence
used by the full run, and one was a conservative negative output despite a
positive repoDB proxy label. False positives were also informative: one was a
PubMed-heavy co-mention case with little structured/graph support, and two had
negative/failure PubMed signals, reinforcing that repoDB `negative_or_failed`
labels can be noisy proxies rather than clean biological negatives.

Threshold calibration used only dev rows, but only 3 completed dev rows were
evaluable, so all calibrated thresholds are marked exploratory. The best F1,
balanced-accuracy, high-precision, and high-recall threshold for the original
full confidence score was `0.55`. Applied to all 16 evaluable completed rows,
it produced accuracy `0.5`, precision `0.5714285714285714`, recall
`0.4444444444444444`, F1 `0.5`, and ROC-AUC `0.46825396825396826`. On the 13
test rows, F1 was `0.42857142857142855`.

Transparent alternative scores were added using only existing extracted
features. The best exploratory alternative was `safety_penalized_score`, with
threshold `0.06473928278103082`, accuracy `0.65`, precision `0.6`, recall
`0.9`, F1 `0.7200000000000001`, and ROC-AUC `0.72` over the 20 selected rows.
This is not a trained result; it is an evidence-feature scoring design that
should be validated on a larger dev/test split.

Optional triage classification was also added. Using fixed bands on
`clinical_support_score`, triage covered 13/20 rows, abstained on 7/20
(`uncertain_mixed`), and achieved accuracy `0.6153846153846154` on covered
cases. Triage improves reliability operationally by refusing to force every
case into a binary label, even though it is not a substitute for stronger
validation.

Phase 6C-D artifacts:

- `eval_results/full_pipeline/error_analysis_full.csv`
- `eval_results/full_pipeline/confusion_matrix_full.md`
- `eval_results/full_pipeline/threshold_calibration.csv`
- `eval_results/full_pipeline/best_thresholds.json`
- `eval_results/full_pipeline/alternative_score_comparison.csv`
- `eval_results/full_pipeline/triage_classification_full.csv`
- `eval_results/full_pipeline/triage_metrics_full.json`
- `eval_results/full_pipeline/diagnostic_summary_full.json`
- `docs/figures/full_pipeline_threshold_curve.png`

## Phase 6F Scaling Preparation

Phase 6F prepares the next scale step from the 20-pair full-agent run to 50 and
100 benchmark pairs. The goal is to test whether the Phase 6C-D finding holds:
raw full-agent confidence was poorly calibrated, while transparent
`safety_penalized_score` looked stronger on the small run.

The scale plan is documented in `docs/scale_to_50_100_plan.md`.

Scaled pair lists were generated deterministically:

| Cohort | Selected | Positive | Negative_or_failed | Dev | Test |
|---|---:|---:|---:|---:|---:|
| 50-pair | 50 | 25 | 25 | 10 | 40 |
| 100-pair | 100 | 50 | 50 | 20 | 80 |

Selection uses existing repoDB labels, split metadata, and unified evidence
availability. It ranks rows by PubMed, Open Targets, and graph availability
without conditioning on previous full-agent correctness.

In the current shell, `PUBMED_EMAIL` and `GEMINI_API_KEY` were not configured.
Therefore PubMed expansion and scaled real full-agent execution were not run.
The 50- and 100-pair scaled output directories contain explicit
`TODO_NOT_RUN` full-agent artifacts rather than generated predictions, reports,
claims, PMIDs, or metrics.

Phase 6F artifacts:

- `docs/scale_to_50_100_plan.md`
- `scripts/select_scaled_eval_pairs.py`
- `scripts/build_scaling_comparison.py`
- `eval_results/full_pipeline/scaled_selected_pairs_50.csv`
- `eval_results/full_pipeline/scaled_selected_pairs_100.csv`
- `eval_results/full_pipeline_scaled_50/`
- `eval_results/full_pipeline_scaled_100/`
- `eval_results/scaling_comparison/scaling_summary.csv`
- `eval_results/scaling_comparison/scaling_summary.md`
- `docs/figures/scaling_f1_comparison.png`
- `docs/figures/scaling_roc_auc_comparison.png`
- `docs/figures/scaling_triage_coverage_accuracy.png`
- `docs/figures/scaling_verifier_effect.png`

Current interpretation: the scaled cohorts are ready, but 50/100 performance
does not yet confirm or weaken the 20-pair `safety_penalized_score` finding
because no real scaled full-agent reports were generated in this environment.

## Phase 6F-B Real 50-Pair Scaled Run

Phase 6F-B executed the real 50-pair scaled evaluation. PubMed coverage was
expanded first, then the unified benchmark table and selected 50-pair cohort
were regenerated.

PubMed expansion:

| Metric | Value |
|---|---:|
| Pair feature rows | 50 |
| Evidence rows | 2149 |
| Summed pair unique PMIDs | 1058 |
| Evidence-available pairs | 37 |
| Evidence availability rate | 0.74 |

50-pair selected cohort:

| Metric | Value |
|---|---:|
| Selected pairs | 50 |
| Positive | 25 |
| Negative_or_failed | 25 |
| Dev | 10 |
| Test | 40 |
| PubMed available | 48 |
| Open Targets available | 48 |
| Graph available | 48 |

Real full mode:

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
| Mean runtime seconds | 28.299235321995802 |

Real `no_verifier` ablation:

| Metric | Value |
|---|---:|
| Completed | 41 |
| Partial success | 9 |
| Failed | 0 |
| F1 | 0.5531914893617021 |
| Citation verified rate | 0.0 |
| Unsupported claim rate | 1.0 |

The verifier effect held up at 50 pairs: full mode had unsupported-claim rate
`0.10897435897435898`, while `no_verifier` remained `1.0`.

Scaled diagnostics:

- original full-confidence F1 improved from `0.4` at 20 pairs to
  `0.5333333333333333` at 50 pairs;
- dev-selected original-confidence threshold remained `0.55`, but calibration
  is still marked exploratory because only 9 completed dev rows were evaluable;
- original-confidence test F1 at threshold `0.55` was `0.4864864864864865`;
- best alternative score was still `safety_penalized_score`, threshold
  `0.13312792223387354`, accuracy `0.66`, precision `0.625`, recall `0.8`,
  F1 `0.7017543859649122`, and ROC-AUC `0.6464`;
- triage covered 25/50 pairs, abstained on 25/50, and achieved covered-case
  accuracy `0.64` with covered-case F1 `0.39999999999999997`;
- error counts were TP `12`, TN `9`, FP `9`, FN `12`, partial `8`.

The `safety_penalized_score` finding is strengthened because it again
outperformed original full confidence on F1. It is still not clinical
validation: repoDB labels are proxy labels, calibration remains small-dev
exploratory, and generated reports require manual biomedical review.
