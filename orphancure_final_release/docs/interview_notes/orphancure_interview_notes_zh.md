# 项目简介

## 简历写法

Built **OrphanCure**, a benchmark-driven biomedical AI agent evaluation framework for drug-disease evidence assessment, integrating repoDB, PubMed, Open Targets, PrimeKG, LLM synthesis, verifier ablation, safety-penalized scoring, scaling diagnostics, and Streamlit deployment.

## 项目名称

OrphanCure

## 时间

2026.03 - 2026.06

## 工作职责

| 模块 | 我的工作 |
|---|---|
| Benchmark | 构建 200 条 balanced repoDB drug-disease benchmark，包含 dev/test split |
| Evidence | 接入 PubMed、Open Targets、PrimeKG，生成统一 feature table |
| Agent | 组织 full-agent synthesis、mechanism discovery、claim verification、quality gate |
| Evaluation | 完成 20-pair diagnostic run、50-pair scaled run、ablation、triage、error analysis |
| Release | 打包 GitHub-ready / Streamlit Cloud-ready research demo |

## 项目背景

Rare disease drug repurposing 的难点是证据高度分散：文献里可能只有 case report 或机制线索，Open Targets 里可能有 disease-target association，PrimeKG 里可能有 graph path，而 repoDB 提供的是 approved / failed indication 的 proxy label。直接让 LLM 生成结论风险很高，因为它可能把 co-mention、机制支持和临床疗效混在一起。

## 项目目标

把一个 biomedical AI agent 从“能生成报告的 demo”升级成“可评估、可解释、可审计、可部署”的 research engineering project。

## 项目结果

| 项目 | 结果 |
|---|---:|
| repoDB benchmark | 200 balanced pairs |
| PubMed evidence availability | 37/50 |
| Open Targets rows | 50 |
| PrimeKG graph feature rows | 50 |
| 20-pair full run | 16 completed / 4 partial / 0 failed |
| 50-pair full run | 42 completed / 8 partial / 0 failed |
| 50-pair original F1 | 0.5333 |
| 50-pair safety_penalized_score F1 | 0.7018 |
| 50-pair full unsupported claim rate | 0.1090 |
| 50-pair no_verifier unsupported claim rate | 1.0000 |

## 项目定位

OrphanCure 是 research-support / education project，不是临床验证，不是 medical advice，也不推荐治疗方案。它的价值是构建 benchmark-driven biomedical AI evaluation framework。

## 技术栈

| 类型 | 技术 |
|---|---|
| Language | Python, Markdown, LaTeX |
| Data | pandas, CSV/JSON summary artifacts |
| Biomedical sources | repoDB, PubMed, Open Targets, PrimeKG |
| Evaluation | scikit-learn metrics, ablation, threshold calibration, triage |
| App | Streamlit |
| Release | GitHub-ready folder, Streamlit Cloud demo mode |

# 1. 数据来源

| 数据源 | 在 OrphanCure 中的作用 | 关键限制 |
|---|---|---|
| repoDB | approved / failed drug indication proxy label | 不是 clinical truth |
| PubMed | literature retrieval、PMID evidence、co-mention feature | co-mention 不等于有效 |
| Open Targets | drug target、disease target、target overlap | mechanism support，不是疗效证明 |
| PrimeKG | drug-gene-disease graph path、connectivity feature | graph path 只是机制线索 |

# 2. 数据处理流程

| 步骤 | 输入 | 输出 | 说明 |
|---|---|---|---|
| repoDB construction | repoDB raw indication data | 200 balanced pairs | 100 positive / 100 negative_or_failed |
| PubMed feature extraction | drug-disease query | 50 pair-feature rows | 2,149 evidence rows，1,058 unique PMIDs |
| Open Targets enrichment | drug/disease names | 50 rows | drug resolution 1.0，disease resolution 0.82 |
| PrimeKG normalization | raw graph | compact graph features | 4,130,337 edges、84,289 nodes in source repo |
| Unified table | benchmark + evidence | unified feature table | 按 pair_id left join，不丢失 row |

工程重点：缺失 evidence 不删除样本，而是保留 availability flags。这样 evaluation 可以区分“预测错了”和“证据缺失/partial success”。

# 3. Agent 系统设计

| 模块 | 功能 |
|---|---|
| Entity resolution | 解析 drug 和 disease 到外部数据库实体 |
| Mechanism discovery | 从 Open Targets / PrimeKG 找 target 和 graph path |
| Literature retrieval | PubMed 检索相关 PMID 和 co-mention signal |
| Synthesis | LLM 根据 structured evidence 和 literature 生成研究报告 |
| Verifier | 检查 claim 是否有 citation 支持 |
| Quality gate | 标记 completed / partial_success / failed |
| Report generation | 输出可人工 review 的 case report |

面试讲法：我没有把 LLM 当成最终答案机器，而是把它放进一个有 benchmark、有 evidence provenance、有 verifier、有 ablation 的评估系统里。

# 4. Baseline 与 Ablation 设计

| Mode | 目的 |
|---|---|
| PubMed-only | 看 literature signal 单独能否区分 proxy label |
| OpenTargets-only | 看 target overlap / disease target support |
| Graph-only | 看 PrimeKG graph connectivity |
| combined structured baseline | 合并 structured evidence |
| full agent | 完整 retrieval + synthesis + verifier |
| no_verifier | 测 verifier 对 unsupported claims 的影响 |
| no_target_expansion | 测 target expansion 的贡献 |
| no_graph_features | 测 graph feature 的贡献 |

# 5. Prediction Diagnostics

原始 full-agent accuracy / F1 不高，主要原因不是系统完全无效，而是 raw LLM confidence 没有被校准、false negatives 较多、partial_success rows 影响了 forced binary prediction。50-pair error analysis 中 TP=12、TN=9、FP=9、FN=12、partial=8，说明 recall loss 是核心问题。

`safety_penalized_score` 的思路是：如果一个报告的 evidence strong 但 unsupported claims 多，或者输出质量不完整，就降低分数。它不是临床评分，而是 benchmark diagnostics 中更稳健的 exploratory score。

| Score | 50-pair F1 | ROC-AUC | 解释 |
|---|---:|---:|---|
| original full confidence | 0.5333 | 0.5174 | raw confidence 校准较差 |
| safety_penalized_score | 0.7018 | 0.6464 | 加入 safety / evidence penalty 后更稳定 |

Triage classification 的价值是允许 abstention。医学证据不确定时，不强行二分类比硬给 positive/negative 更合理。

# 6. 系统测评

## 20-pair run

| 指标 | 数值 |
|---|---:|
| selected | 20 |
| completed | 16 |
| partial_success | 4 |
| failed | 0 |
| original F1 | 0.4000 |
| original ROC-AUC | 0.4683 |
| full unsupported claim rate | 0.0625 |
| no_verifier unsupported claim rate | 1.0000 |

## 50-pair run

| 指标 | 数值 |
|---|---:|
| selected cohort | 50 |
| labels | 25 positive / 25 negative_or_failed |
| split | 10 dev / 40 test |
| completed / partial / failed | 42 / 8 / 0 |
| original accuracy | 0.5000 |
| original precision | 0.5714 |
| original recall | 0.5000 |
| original F1 | 0.5333 |
| original ROC-AUC | 0.5174 |
| mean runtime seconds | 28.2992 |

## Verifier ablation

| Run | full unsupported claim rate | no_verifier unsupported claim rate |
|---|---:|---:|
| 20-pair | 0.0625 | 1.0000 |
| 50-pair | 0.1090 | 1.0000 |

解释：no_verifier 有时 prediction F1 不一定更差，但 biomedical safety 明显更差，因为 unsupported claims 上升到 1.0。

## Triage

| Run | coverage | abstention | accuracy_on_covered | F1_on_covered |
|---|---:|---:|---:|---:|
| 20-pair | 0.65 | 0.35 | 0.6154 | - |
| 50-pair | 0.50 | 0.50 | 0.6400 | 0.4000 |

# 7. Case Study 分析

| Pair | Drug | Disease | Case type | 面试讲法 |
|---|---|---|---|---|
| repodb_0557bc43eff59f45 | Theophylline | Asthma | correct_positive | 展示系统能在 evidence-rich case 上输出正确 proxy label |
| repodb_118c436e16e1ab51 | Paclitaxel | Testicular Germ Cell Tumor | correct_negative_or_failed | 展示 negative_or_failed 不是简单“没有机制”，而是 label 需要谨慎解释 |
| repodb_04246cb3a1c31ef7 | Progesterone | Premature Birth | verifier_effect | 展示 verifier 如何降低 unsupported claims |
| repodb_0ee62470d8ffb2ae | Cisplatin | Esophageal neoplasm metastatic | incorrect_but_informative | 展示错误样本仍能帮助定位 calibration / label ambiguity |
| repodb_04ab2c145755011f | Azacitidine | Myelofibrosis due to another disorder | partial_success_error_analysis | 展示 partial_success 不能假装成 completed |

所有 case 都保持 `TODO_MANUAL_REVIEW`，不能说已经完成专家审核。

# 8. 项目亮点

- 不是只套 LLM，而是 benchmark-driven evaluation framework。
- 使用真实 biomedical sources：repoDB / PubMed / Open Targets / PrimeKG。
- 同时评估 prediction metrics 和 faithfulness metrics。
- 做了 no_verifier ablation，证明 verifier 对 unsupported claims 很关键。
- 用 safety_penalized_score 改善了 exploratory benchmark performance。
- 用 triage + abstention 处理医学证据不确定性。
- 最终打包成 GitHub-ready / Streamlit-ready release。

# 9. 项目局限

- 不是临床验证。
- repoDB label 是 proxy，不是 clinical truth。
- PubMed co-mention 不等于疗效证据。
- Open Targets / PrimeKG coverage 不完整。
- selected cohorts 仍然较小。
- LLM output 依赖模型和 prompt。
- 所有 generated biomedical case studies 都需要 expert manual review。

# 10. 面试讲法

## 30 秒版本

OrphanCure 是一个 biomedical AI agent evaluation framework。我用 repoDB 构建 200 条 balanced drug-disease benchmark，再接入 PubMed、Open Targets 和 PrimeKG 作为 evidence layers，评估 full-agent synthesis、verifier、ablation、safety-penalized scoring 和 triage。它不是 medical advice，而是研究型 benchmark 和 evidence-grounded reporting 系统。

## 2 分钟版本

这个项目解决的是 biomedical agent 不能只看生成效果的问题。LLM 可以写 drug repurposing report，但如果没有 benchmark、evidence provenance 和 verifier，很容易产生 unsupported biomedical claims。我先用 repoDB 构建 proxy label benchmark，再把 PubMed literature、Open Targets target evidence、PrimeKG graph mechanisms 合成 unified feature table。然后跑 full-agent evaluation 和 ablation，比较 no_verifier、no_graph_features、no_target_expansion。结果上，50-pair full run 原始 F1 是 0.5333，但 safety_penalized_score F1 到 0.7018；verifier 把 unsupported claim rate 从 no_verifier 的 1.0 降到 full mode 的 0.1090。

## 5 分钟版本

可以按“问题 - 系统 - 评估 - 结果 - 安全边界”讲。问题是 rare disease drug repurposing evidence 很分散，LLM 容易过度总结。系统上我做了 benchmark layer、evidence layer、agent synthesis layer、claim verification layer、diagnostics layer 和 deployment layer。评估上不仅看 accuracy/F1/ROC-AUC，还看 unsupported claim rate、citation verified rate、triage coverage 和 partial_success。结果上，原始 confidence 校准不理想，false negatives 较多；但 safety_penalized_score 更稳，verifier effect 很强。最后强调这不是 clinical validation，所有 case 都要 manual review。

# 11. 面试问答

**1. 这个项目是不是 LLM wrapper？**  
不是。LLM 只是 synthesis 模块，外面有 repoDB benchmark、PubMed/OT/PrimeKG evidence、verifier、ablation、threshold calibration 和 Streamlit release。

**2. 为什么 full-agent 原始 F1 不高？**  
主要是 false negatives / recall loss、raw confidence 校准不好，以及 8 个 partial_success rows 影响 forced binary evaluation。

**3. 为什么 safety_penalized_score 更好？**  
它把 evidence strength 和 safety signal 结合起来，对 unsupported claims 和 incomplete outputs 做 penalty，所以比 raw confidence 更适合作为 exploratory benchmark score。

**4. 为什么 verifier 重要？**  
因为 biomedical report 的安全风险主要来自 unsupported claims。50-pair 中 no_verifier unsupported claim rate 是 1.0，full mode 是 0.1090。

**5. 为什么 no_verifier 有时 F1 接近或者更高？**  
Prediction F1 和 claim faithfulness 是不同指标。一个模型可以大胆猜对 label，但同时生成不可靠 biomedical claims。

**6. 为什么 repoDB negative_or_failed 不等于严格 negative？**  
失败可能来自 safety、trial design、endpoint、商业原因或样本问题，不一定说明机制完全无效。

**7. 为什么 triage 比 forced binary prediction 更合理？**  
医学证据常常不完整。允许 abstention 可以避免在 uncertain middle band 强行输出 positive/negative。

**8. 如果继续优化，你会怎么做？**  
扩大 cohort、改进 entity resolution、加入 better literature polarity extraction、做专家 review、校准 confidence，并把 verifier 做成更细粒度的 claim-level evaluator。

**9. 这个项目和 DocReranker 有什么相似点？**  
都有 benchmark、baseline、ablation、metric-driven evaluation 和工程化 release。

**10. 这个项目和 DocReranker 有什么不同？**  
DocReranker 是 retrieval/reranking，指标类似 Recall@K；OrphanCure 是 biomedical evidence assessment，指标包括 F1、ROC-AUC、unsupported claim rate、triage coverage 和 manual review status。

# 12. 可写进简历的英文 bullets

- Built OrphanCure, a benchmark-driven biomedical AI agent evaluation framework integrating repoDB, PubMed, Open Targets, and PrimeKG for drug-disease evidence assessment.
- Constructed a balanced 200-pair repoDB benchmark and unified evidence table with PubMed literature, target evidence, and graph mechanism features.
- Evaluated 20-pair and 50-pair full-agent runs with ablations, verifier diagnostics, safety-penalized scoring, triage classification, and case-study review packets.
- Demonstrated strong verifier effect, reducing unsupported claim rate from 1.0 in no-verifier mode to 0.1090 in the 50-pair full-agent run.
- Packaged the project into a GitHub-ready and Streamlit Cloud-deployable research demo with safety documentation and public-safe sample outputs.

# 13. STAR Stories

## Story 1: turning a demo into a benchmark-driven evaluation framework

Situation: 项目一开始更像一个 biomedical report demo。  
Task: 需要让它变成可评估、可复现的工程项目。  
Action: 我引入 repoDB benchmark、evidence layers、unified feature table 和 metrics。  
Result: 项目从“能生成”升级为“能被系统评估”。

## Story 2: debugging full-agent pipeline failure

Situation: full-agent run 出现 partial_success 和 incomplete outputs。  
Task: 不能把失败样本删掉或假装成功。  
Action: 保留 partial_success status，加入 diagnostics 和 error analysis。  
Result: 50-pair run 清楚报告 42 completed / 8 partial / 0 failed。

## Story 3: improving prediction diagnostics without fabricating results

Situation: original full-agent F1 不高。  
Task: 需要解释问题而不是美化结果。  
Action: 分析 false negatives、partial rows、raw confidence calibration，并加入 safety_penalized_score。  
Result: 在 50-pair diagnostics 中 safety_penalized_score F1 达到 0.7018。

## Story 4: verifier ablation and biomedical safety

Situation: LLM 生成 biomedical claims 有 unsupported risk。  
Task: 需要量化 verifier 的价值。  
Action: 对比 full 和 no_verifier 的 unsupported claim rate。  
Result: 50-pair no_verifier unsupported claim rate 为 1.0，full mode 为 0.1090，说明 verifier 对安全和可信度非常关键。
