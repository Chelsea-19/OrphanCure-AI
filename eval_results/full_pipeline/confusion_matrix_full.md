# Full Pipeline Confusion Matrix

| Category | Count | Examples |
|---|---:|---|
| TP | 3 | repodb_0557bc43eff59f45 (Theophylline / Asthma); repodb_0d57eaf7fcf55450 (Valproic Acid / Absence Epilepsy); repodb_0f3a4d1dcb0d3feb (Radium Ra 223 Dichloride / Malignant neoplasm of prostate) |
| TN | 4 | repodb_118c436e16e1ab51 (Paclitaxel / Testicular Germ Cell Tumor); repodb_019230a0310bf50c (Donepezil / Advanced cancer); repodb_0b6a9edc9d19946a (Tamoxifen / Breast cancer recurrent) |
| FP | 3 | repodb_04246cb3a1c31ef7 (Progesterone / Premature Birth); repodb_0ee62470d8ffb2ae (Cisplatin / Esophageal neoplasm metastatic); repodb_0b9f9f1795a16598 (Aminophylline / Malignant neoplasm of lung) |
| FN | 6 | repodb_130d9194853cab0c (Simeprevir / Hepatitis C, Chronic); repodb_0a65b90b3ed1bdce (Paclitaxel / Carcinoma breast stage IV); repodb_0f5d00f3cf88c277 (Prednisolone / Bacterial keratitis) |
| skipped/partial | 4 | repodb_04ab2c145755011f (Azacitidine / Myelofibrosis due to another disorder); repodb_04c33e977f1821df (Tacrolimus / recurrent adult diffuse mixed cell lymphoma); repodb_0cb807513ccfb28d (Amikacin / Meningitis due to Klebsiella mobilis) |
| skipped | 0 |  |

Partial and skipped rows are not counted as TP/TN/FP/FN in the original full-agent binary metrics.
