# OrphanCure Case Studies

These case studies were selected from the completed 20-pair full-agent run.
They are manually reviewable research artifacts, not clinical recommendations.

## Selected Cases

| pair_id | Drug | Disease | Case Type | Status | Manual Review |
|---|---|---|---|---|---|
| `repodb_0557bc43eff59f45` | Theophylline | Asthma | `correct_positive` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `correct_negative_or_failed` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `verifier_effect` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `incorrect_but_informative` | `completed` | `TODO_MANUAL_REVIEW` |
| `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `partial_success_error_analysis` | `partial_success` | `TODO_MANUAL_REVIEW` |

## What These Cases Demonstrate

- Evidence provenance can be inspected across PubMed, Open Targets, PrimeKG, and generated claims.
- The verifier reduces unsupported claims compared with `no_verifier`.
- Incorrect and partial-success cases are useful for understanding limitations.

## What These Cases Do Not Demonstrate

- They do not prove drug efficacy.
- They do not validate clinical use.
- They do not replace biomedical expert review.

## Safety Disclaimer

This case study is for research and educational purposes only. It is not medical advice and must not be used for clinical decision-making.
