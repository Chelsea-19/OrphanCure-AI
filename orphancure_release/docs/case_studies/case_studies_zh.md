# OrphanCure Case Studies 中文面试说明

## 为什么选择这些案例

这些案例来自 20-pair full-agent run，覆盖 correct positive、correct negative_or_failed、
verifier effect、incorrect but informative，以及 partial_success error analysis。它们的目的
不是证明药物有效，而是展示系统如何保留证据、claims、PMID、Open Targets/PrimeKG 特征和
verification status。

## 选中案例

- `repodb_0557bc43eff59f45`：Theophylline / Asthma，类型 `correct_positive`，状态 `completed`。
- `repodb_118c436e16e1ab51`：Paclitaxel / Testicular Germ Cell Tumor，类型 `correct_negative_or_failed`，状态 `completed`。
- `repodb_04246cb3a1c31ef7`：Progesterone / Premature Birth，类型 `verifier_effect`，状态 `completed`。
- `repodb_0ee62470d8ffb2ae`：Cisplatin / Esophageal neoplasm metastatic，类型 `incorrect_but_informative`，状态 `completed`。
- `repodb_04ab2c145755011f`：Azacitidine / Myelofibrosis due to another disorder，类型 `partial_success_error_analysis`，状态 `partial_success`。

## 面试中怎么讲 verifier effect

可以说：`no_verifier` 的 unsupported claim rate 明显更高，而 full mode 会把 claim 和
retrieved PubMed abstracts 做 citation verification。这个模块不一定提高 repoDB label
accuracy，但可以提高 report faithfulness，降低 unsupported claims。

## 为什么 full pipeline accuracy 不高

repoDB label 是 approved/failed proxy label，不等于机制证据真假。失败试验也可能有机制证据，
approved indication 也可能缺少 Open Targets overlap 或图路径。因此 full pipeline 当前更像
evidence-grounded report generator，而不是 validated clinical predictor。

## 这个项目是不是 LLM wrapper?

不是。LLM 只是 synthesis/report 组件。项目核心是 benchmark、真实数据集成、PubMed/OT/PrimeKG
多证据层、ablation、verifier、failure accounting 和 manual review workflow。

## 医学安全边界

This case study is for research and educational purposes only. It is not medical advice and must not be used for clinical decision-making.

所有 case 的 biomedical expert review 默认仍是未完成状态。
