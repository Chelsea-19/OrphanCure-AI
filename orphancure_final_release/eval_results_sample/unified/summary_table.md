# Unified Evaluation Summary

## Evidence Coverage

| Metric | Value |
|---|---|
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

## Baseline Comparison

| Mode | Status | Accuracy | Precision | Recall | F1 | ROC-AUC | Evaluated | Skipped |
|---|---|---|---|---|---|---|---|---|
| combined_structured_literature | completed | 0.5500 | 0.5455 | 0.6000 | 0.5714 | 0.5600 | 20.0000 | 180.0000 |
| full | completed | 0.4375 | 0.5000 | 0.3333 | 0.4000 | 0.4683 | 16.0000 | 4.0000 |
| graph_only | completed | 0.5000 | 0.5000 | 1.0000 | 0.6667 | 0.5432 | 50.0000 | 150.0000 |
| heuristic_combined | completed | 0.5000 | 0.5000 | 1.0000 | 0.6667 | 0.5712 | 50.0000 | 150.0000 |
| no_graph_features | completed | 0.5000 | 0.5714 | 0.4444 | 0.5000 | 0.5000 | 16.0000 | 4.0000 |
| no_target_expansion | completed | 0.4667 | 0.5000 | 0.5000 | 0.5000 | 0.4643 | 15.0000 | 5.0000 |
| no_verifier | completed | 0.3750 | 0.4286 | 0.3333 | 0.3750 | 0.4048 | 16.0000 | 4.0000 |
| opentargets_only | completed | 0.5000 | 0.5000 | 1.0000 | 0.6667 | 0.5216 | 50.0000 | 150.0000 |
| ot_plus_graph | completed | 0.5000 | 0.5000 | 1.0000 | 0.6667 | 0.5664 | 50.0000 | 150.0000 |
| pubmed_only | completed | 0.5500 | 0.5333 | 0.8000 | 0.6400 | 0.5600 | 20.0000 | 180.0000 |
| pubmed_only_report | TODO_NOT_RUN |  |  |  |  |  | 0.0000 | 200.0000 |
| structured_only_report | TODO_NOT_RUN |  |  |  |  |  | 0.0000 | 200.0000 |

These baselines compare transparent evidence scores against repoDB proxy labels only.
