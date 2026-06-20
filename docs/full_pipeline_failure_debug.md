# Full Pipeline Failure Debug Note

## Failed Pair

- `pair_id`: `repodb_0ee62470d8ffb2ae`
- Drug: Cisplatin
- Disease: Esophageal neoplasm metastatic
- repoDB proxy label: `negative_or_failed`

## Observed Error

During the Phase 6C-B 5-pair smoke run, this pair failed in `full`,
`no_verifier`, `no_target_expansion`, and `no_graph_features` modes with:

```text
'NoneType' object has no attribute 'get'
```

The row was retained with `status=failed`; it was not dropped.

## Root Cause

The 5-pair rerun after adding raw failure capture produced the real traceback:

```text
app/agents/mechanism.py::_extract_drug_targets
self.state.drug_data.get("mechanismsOfAction", {}).get("rows", [])
```

For this pair, Open Targets drug details returned `None`. `MechanismAgent`
assumed `state.drug_data` was always a dictionary and called `.get(...)` on
`None`, which caused the repeated crash during mechanism discovery.

This is a missing-evidence handling bug in the mechanism discovery step, not a
repoDB label issue and not a clinical interpretation.

## Fix

The primary fix is in `app/agents/mechanism.py`:

- `get_drug_details(...)` and `get_disease_details(...)` now fall back to `{}`;
- missing drug or disease details are logged as warnings;
- malformed `mechanismsOfAction.rows` and `associatedTargets.rows` fields return
  empty lists rather than crashing;
- malformed row or target entries are skipped.

Additional robustness was added in `app/agents/synthesis_critic.py`:

- non-dict top-level LLM responses become structured synthesis errors;
- null or non-dict claim items are skipped with warning logs;
- null or non-dict nested paper references are skipped;
- malformed target lists are normalized conservatively;
- non-numeric confidence values fall back to `0.0`.

The evaluation wrapper in `app/evaluation/full_pipeline_eval.py` now treats a
missing or error-bearing final report as `partial_success` when evidence exists
rather than crashing during normalization.

The CLI in `scripts/run_full_pipeline_eval.py` now writes raw failure JSON and a
markdown failure marker even for unexpected per-pair exceptions.

## Regression Test

Regression coverage:

- `tests/test_agents.py::TestBaseAgentContract::test_mechanism_handles_missing_opentargets_details`
- `tests/test_agents.py::TestBaseAgentContract::test_synthesis_skips_malformed_llm_claim_items`

## Interpretation

This fix does not fabricate claims or reports. If a pair still lacks valid
synthesis output, the evaluator should report `partial_success` or `failed` with
a clear error message and retained artifacts.

## Rerun Status

After the mechanism-discovery fix, the same 5-pair full-mode smoke run was
rerun.

| Metric | Value |
|---|---:|
| Selected pairs | 5 |
| Completed | 5 |
| Partial success | 0 |
| Failed | 0 |
| Accuracy | 0.6 |
| F1 | 0.7499999999999999 |
| Citation verified rate | 0.6666666666666667 |
| Unsupported claim rate | 0.2 |

The formerly failed Cisplatin / Esophageal neoplasm metastatic pair completed
after missing Open Targets drug details were handled as missing evidence.

The full-mode evaluation was then scaled to 20 selected pairs:

| Metric | Value |
|---|---:|
| Completed | 16 |
| Partial success | 4 |
| Failed | 0 |
| Accuracy | 0.4375 |
| F1 | 0.4 |
| ROC-AUC | 0.46825396825396826 |
| Citation verified rate | 0.78125 |
| Unsupported claim rate | 0.0625 |

The remaining `partial_success` rows completed without a final report object and
are retained for audit.
