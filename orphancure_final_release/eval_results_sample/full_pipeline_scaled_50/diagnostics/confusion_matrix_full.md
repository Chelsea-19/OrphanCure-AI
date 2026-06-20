# Full Pipeline Confusion Matrix

| Category | Count | Examples |
|---|---:|---|
| TP | 12 | repodb_0557bc43eff59f45 (Theophylline / Asthma); repodb_1ec6c8c3ab8e153d (Famotidine / Duodenal Ulcer); repodb_0d57eaf7fcf55450 (Valproic Acid / Absence Epilepsy) |
| TN | 9 | repodb_04246cb3a1c31ef7 (Progesterone / Premature Birth); repodb_3ab2a1d014ffd529 (Cisplatin / Non-Small Cell Lung Carcinoma); repodb_019230a0310bf50c (Donepezil / Advanced cancer) |
| FP | 9 | repodb_2df019ef279bf716 (Finasteride / Benign Prostatic Hyperplasia); repodb_0ee62470d8ffb2ae (Cisplatin / Esophageal neoplasm metastatic); repodb_2d0e801613852c62 (Cyclosporine / Myeloid Leukemia) |
| FN | 12 | repodb_130d9194853cab0c (Simeprevir / Hepatitis C, Chronic); repodb_2436d79d27a90f1c (Aztreonam / Escherichia coli Infections); repodb_0a65b90b3ed1bdce (Paclitaxel / Carcinoma breast stage IV) |
| skipped/partial | 8 | repodb_1f67590639394d16 (Doxorubicin / stage IV adult diffuse large cell lymphoma); repodb_04ab2c145755011f (Azacitidine / Myelofibrosis due to another disorder); repodb_04c33e977f1821df (Tacrolimus / recurrent adult diffuse mixed cell lymphoma) |
| skipped | 0 |  |

Partial and skipped rows are not counted as TP/TN/FP/FN in the original full-agent binary metrics.
