# OrphanCure 项目说明：面试版技术报告

## 1. 项目一句话介绍

### 简历版，一句话

Built OrphanCure, a benchmark-driven biomedical AI evaluation framework that
integrates repoDB, Open Targets, and PrimeKG to assess rare-disease drug
repurposing evidence with transparent baselines and ablations.

### 面试开场版，30 秒

OrphanCure 是一个面向 rare-disease drug repurposing 的研究工程项目。它不是简单
让 LLM 直接生成药物推荐，而是先构建真实 benchmark：用 repoDB 作为 approved
/ failed proxy label，用 Open Targets 提供 target evidence，用 PrimeKG 提供
graph mechanism evidence，再把这些证据合并成 unified evaluation table，跑可解释
baseline 和 ablation。当前结果不是临床预测模型，而是一个严谨的 evaluation
framework。

### 深度技术版，1-2 分钟

这个项目的核心目标是把一个 demo-style biomedical agent 转成 benchmark-driven
research engineering repository。我完成了四层工作：第一，下载和清洗真实
repoDB，构建 200 个 balanced drug-disease pairs，并保留 metadata 和 SHA256；
第二，对其中 50 个 pair 调用 Open Targets API，做 drug/disease entity
resolution、target extraction 和 target overlap；第三，下载并标准化 PrimeKG，
处理 84,289 个 node 和 4,130,337 条 edge，提取 graph mapping、shortest paths
和 connectivity score；第四，把 repoDB、Open Targets 和 PrimeKG 左连接成
unified benchmark table，保证 pair_id 不丢失，并实现 deterministic baseline、
threshold selection、metric calculation 和 ablation tracking。这个项目强调可复现、
不编造结果、不把 mechanism support 误说成 clinical efficacy。

## 2. 项目背景与动机

Rare disease 的药物研发通常面临样本少、商业激励不足、文献分散、机制证据不完整
等问题。Drug repurposing 的想法是：已有药物可能对新的疾病有潜在机制相关性，
但这种假设必须经过系统证据评估，而不能直接当成治疗建议。

为什么需要 AI agent？因为 evidence 分散在多个来源：

- 文献里可能有 case report、preclinical mechanism 或 trial 线索。
- Open Targets 里有 disease-target association 和 drug mechanism。
- PrimeKG 这类 graph 里有 drug、gene、disease、pathway 等关系。
- repoDB 里有 approved 和 failed indication 的 proxy label。

为什么不能只让 LLM 直接回答？因为 LLM 很容易把不同强度的证据混在一起，甚至
生成没有 provenance 的结论。这个项目的设计原则是：先有 benchmark 和 evidence
table，再让 agent 做 retrieval、synthesis 和 verification。

为什么需要 repoDB、Open Targets、PrimeKG 三层 benchmark？

- repoDB 提供 label proxy，让我们至少可以计算 accuracy、F1、ROC-AUC。
- Open Targets 提供 target evidence，可以看 drug target 和 disease target 是否
  有 overlap。
- PrimeKG 提供 graph mechanism，可以看 drug 和 disease 是否通过短路径产生
  机制连接。

这三层互相补充，但都不是 clinical truth。

## 3. 项目整体架构

OrphanCure 当前的 evaluated pipeline 可以这样讲：

1. repoDB 作为 approved/failed proxy benchmark。
2. Open Targets 作为 target evidence layer。
3. PrimeKG 作为 graph mechanism layer。
4. 所有 feature 通过 `pair_id` 左连接成 unified benchmark table。
5. 对 unified table 跑 baseline 和 ablation。
6. 未来 full OrphanCure agent 会加入 PubMed retrieval、evidence synthesis、
   verifier 和 report generation。

最重要的工程点是：所有输出都保留 provenance，缺失 evidence 不丢 row，而是用
availability flag 和 notes 明确标记。

## 4. 和 DocReranker 项目的类比

如果用 DocReranker 类比：

- DocReranker 的核心是 retriever baseline + reranker + Recall@K。
- OrphanCure 的核心是 repoDB baseline + Open Targets / graph evidence layers
  + unified evaluation。
- DocReranker 解决文档排序问题，OrphanCure 解决 drug-disease evidence
  assessment。
- 两者共同点是都有 benchmark、baseline、evaluation、ablation 和 report。

不同点是 OrphanCure 的数据更复杂，因为 biomedical evidence 不是单一 relevance
label。一个 failed trial 仍然可能有 mechanism evidence；一个 approved pair 也不
一定在 Open Targets 里有很强 target overlap。所以 OrphanCure 的结果解释要比
retrieval project 更谨慎。

当前 OrphanCure 还缺的是 full agent pipeline evaluation，以及 PubMed/verifier
ablation。也就是说，evaluation framework 已经搭好，但 full agent 的实验还没有
完成。

## 5. 数据与 Benchmark 设计

### repoDB

repoDB 是真实 Figshare 数据源。当前项目中下载并记录了 source metadata 和
SHA256。原始 repoDB 约 10,800 rows，Phase 1 构建了 200 个 balanced pairs：
100 positive，100 negative_or_failed。

### Open Targets

Phase 2 对 50 个 repoDB pairs 调用真实 Open Targets API：

- successful: 33
- partial_success: 17
- failed: 0
- drug resolution rate: 1.0
- disease resolution rate: 0.82
- target overlap rate: 0.18
- mean support score: 0.058937472016996055

### PrimeKG

Phase 3 下载并标准化真实 PrimeKG：

- normalized nodes: 84,289
- normalized edges: 4,130,337
- graph pair mappings: 50 rows
- graph pair paths: 9 rows
- drug mapping rate: 0.98
- disease mapping rate: 0.16
- path recovery rate: 0.12

### Unified Table

Phase 4 构建了 200-row unified benchmark table：

- 50 both_available
- 150 missing_evidence
- Open Targets availability: 0.25
- graph availability: 0.25
- both evidence layers available: 0.25

## 6. 方法细节

### Label Mapping

Approved indications 被映射为 `positive`。Terminated、withdrawn、suspended、
failed、no development 等状态被映射为 `negative_or_failed`。不明确状态不强行
映射，避免制造 label。

### Entity Resolution

Open Targets 使用 drug 和 disease search 做 entity resolution。PrimeKG 使用
deterministic name matching 和 synonym matching。当前 disease mapping 是主要瓶颈。

### Target Overlap

Open Targets 中，如果 drug target 和 disease-associated target 有重叠，就标记
`has_target_overlap`，并根据 disease association score 计算 support。

### Graph Path Extraction

PrimeKG 中，如果 drug node 和 disease node 都能 map，就提取长度不超过 4 的短路
径。路径可以是 drug-gene-disease 这类机制线索，但不能被解释为临床疗效。

### Graph Connectivity Score

Graph score 基于 shortest path length 和 path type。更短、更像
drug-target-disease 的路径得分更高，但这只是 mechanism support。

### Unified Feature Construction

所有表按 `pair_id` left join。核心原则是不丢 pair：如果 OT 或 graph 缺失，就保留
row，并标记 `opentargets_available = false` 或 `graph_available = false`。

### Threshold Selection

阈值只用 dev split 选择，不用 test split 调参。如果 dev split 太小或者类别不全，
就用固定阈值。

### 为什么 no fabrication 很重要

Biomedical AI 项目最大的风险之一是把没有跑过的结果写成已经完成。这个项目明确把
PubMed-only、full-agent、verifier ablation 等标记为 `TODO_NOT_RUN`，这是可信度的一
部分。

## 7. 实验结果解读

当前 baseline 结果：

| Mode | Accuracy | F1 | ROC-AUC |
|---|---:|---:|---:|
| Open Targets only | 0.50 | 0.667 | 0.5216 |
| Graph only | 0.50 | 0.667 | 0.5432 |
| OT + Graph | 0.50 | 0.667 | 0.5664 |
| Heuristic combined | 0.50 | 0.667 | 0.5712 |

Phase 6B 新增了 PubMed-only baseline 的代码实现；Phase 6B-B 使用配置的 contact
email 进行了真实 NCBI PubMed smoke run。当前运行了 20 个 repoDB pairs，生成 20 行
pair-level features 和 874 行 PubMed evidence rows，全球去重后得到 461 个 PMIDs。
其中 17 个 pair 有 PubMed evidence，3 个 pair 没有检索到 PMID，evidence
availability rate 是 0.85。

为什么要补 PubMed-only baseline？因为 Open Targets 偏 structured target
evidence，PrimeKG 偏 graph mechanism evidence，而 PubMed 代表 literature
co-mention / publication attention。它可以补充“文献里是否有人讨论过这个
drug-disease pair”的信号。

PubMed-only 能证明什么？它能证明一个 pair 是否有文献共现、是否有 clinical /
mechanism / negative-keyword query 命中，以及这些简单信号和 repoDB proxy label
之间是否有 ranking signal。

PubMed-only 不能证明什么？文献共现不等于药物有效。一个药物和疾病一起出现在摘要
中，可能是因为失败试验、安全性问题、机制研究、综述背景，或者只是历史研究热点。
当前 PubMed baseline 不使用 LLM，也不做 SUPPORTS / CONTRADICTS polarity
classification。

面试中可以这样解释：我加入 PubMed-only baseline 是为了让 literature evidence
成为一个可单独 ablate 的 layer。它和 Open Targets、PrimeKG 互补，但它本身只是
transparent retrieval baseline，不是 full OrphanCure agent。

真实 PubMed-only standalone evaluation 的结果是：accuracy 0.588，precision
0.533，recall 1.0，F1 0.696，ROC-AUC 0.653。positive pairs 的 mean unique PMIDs
是 25.5，negative_or_failed pairs 是 20.6；mean PubMed score 分别是 0.663 和
0.649。这个结果比 OT/graph 单独 baseline 的 ROC-AUC 高一些，但仍然不能解释为
临床预测能力，因为 PubMed co-mention 不是 efficacy evidence。

为什么 accuracy = 0.50 不是简单失败？因为当前 evaluated subset 是 balanced 的 50
pairs，而 dev-selected threshold 产生了 all-positive prediction。也就是说，它更像
一个 sanity baseline，说明 evidence-only score 没有足够能力区分 approved 和
failed。

为什么会 all-positive？因为 OT target support 和 graph connectivity 是 mechanism
evidence。failed trial 也可能有 mechanism evidence；失败原因可能是安全性、剂量、
endpoint、样本设计、商业因素等，不一定是没有机制。

为什么 combined ROC-AUC 略有提升？Open Targets 和 PrimeKG 提供了不同类型的 evidence
signal。组合后 ROC-AUC 从 0.5216/0.5432 提升到 0.5664/0.5712，说明有微弱 ranking
signal，但还远远不能称为强预测模型。

当前结果证明了什么？证明了数据管线、benchmark、baseline、ablation、provenance 和
non-fabrication guardrail 已经搭起来。

当前结果不证明什么？不证明 OrphanCure 能预测临床成功，不证明某个 drug 对某个
disease 有疗效。

## 8. 当前项目完成度评分

| 维度 | 评分 | 说明 |
|---|---:|---|
| Engineering completeness | 8/10 | 数据管线、脚本、测试、release folder 和 demo 基本完整 |
| Benchmark completeness | 7/10 | repoDB 完整 200 pairs；OT/graph 当前覆盖 50 pairs |
| Research credibility | 8/10 | 明确 provenance、限制和 TODO_NOT_RUN，不夸大结果 |
| Deployment readiness | 7/10 | Streamlit demo mode 可运行，但真实 API demo 还需 secrets 和测试 |
| Gap to DocReranker-level polish | 2-3 weeks | 主要差 full agent evaluation、case study manual review 和线上部署 |

## 9. 面试时怎么讲这个项目

### 30 秒版本

我做了一个 rare-disease drug repurposing 的 benchmark-driven AI 项目。它不是直接
让 LLM 推荐药，而是先用 repoDB 建 approved/failed proxy benchmark，再接 Open
Targets 和 PrimeKG 两个 evidence layer，最后构建 unified evaluation 和 ablation。
目前结果显示 evidence-only baseline 只有弱 ranking signal，所以我把它定位成严谨的
evaluation framework，而不是 clinical prediction model。

### 2 分钟版本

这个项目从工程上解决了 biomedical agent 最容易出问题的地方：没有真实 benchmark、
没有 provenance、容易 overclaim。我先下载真实 repoDB，构建 200 个 balanced pairs；
然后用 Open Targets API 为 50 个 pairs 提取 target evidence；再处理 PrimeKG 的
4.1M 条 edge，构建 graph mapping 和 path features；最后把三层数据合成 unified
table，并实现 baseline comparison 和 ablation tracking。结果并不夸张，accuracy 是
0.50，但 ROC-AUC 在组合 evidence 后略有提升。这说明机制证据本身不足以预测临床
成功，也说明后续 full agent 和 PubMed/verifier ablation 很必要。

### 5 分钟版本

可以按“背景 - 数据 - 方法 - 结果 - 反思”讲。背景是 rare disease repurposing
evidence fragmented；数据是 repoDB、Open Targets、PrimeKG；方法是 label mapping、
entity resolution、target overlap、graph path extraction、unified table 和 dev-only
thresholding；结果是 50 evidence-covered pairs 上的 sanity baselines；反思是当前
baseline signal 弱，但项目价值在于真实 benchmark 和可扩展 evaluation framework。

### 如果问 “为什么结果只有 0.50 accuracy？”

我会说：这是一个很重要的发现，而不是要隐藏的失败。当前 baseline 是 evidence-only，
而 evidence support 和 clinical success 是不同概念。failed trial 也可能有 target
或 graph mechanism evidence，所以简单机制分数不能直接预测 approved/failed label。
这说明需要加入 PubMed evidence、trial context、verifier 和 full agent reasoning。

### 如果问 “和普通 LLM wrapper 有什么区别？”

普通 LLM wrapper 通常是输入 drug/disease，然后生成一段解释。OrphanCure 的区别是：
它先构建 benchmark 和 feature table，有真实数据源、有 provenance、有 evaluation、
有 ablation、有 TODO_NOT_RUN guardrail。LLM 只是未来 full pipeline 的一个模块，而不
是项目本身。

### 如果问 “为什么用 Open Targets 和 PrimeKG？”

Open Targets 提供 target-level evidence，适合评估 drug target 和 disease target 的
生物学相关性。PrimeKG 是 large biomedical knowledge graph，适合评估 graph-level
mechanism connectivity。两者一个偏 target evidence，一个偏 graph mechanism，互补。

### 如果问 “怎么进一步提升？”

我会先扩大 OT/graph 覆盖到全部 200 pairs，然后改进 disease normalization，用
MONDO/UMLS/MeSH/DO 做 synonym mapping。之后跑 PubMed-only baseline 和 full
OrphanCure pipeline，再做 verifier、target expansion、graph feature ablation。最后
人工 review 3-5 个 case studies。

## 10. 简历 Bullet Points

- Built a benchmark-driven biomedical AI evaluation framework for rare-disease drug repurposing, integrating repoDB proxy labels, Open Targets evidence, and PrimeKG graph features.
- Downloaded and normalized real repoDB data from Figshare, producing 200 balanced drug-disease benchmark pairs with provenance metadata and SHA256 tracking.
- Integrated the Open Targets GraphQL API to enrich 50 repoDB pairs with drug/disease resolution, target overlap, and support-score features.
- Normalized 84,289 PrimeKG nodes and 4.1M biomedical graph edges, extracting drug-disease mappings, short paths, and graph connectivity features.
- Designed a unified benchmark table preserving all `pair_id` rows and explicitly marking missing evidence instead of silently dropping pairs.
- Implemented deterministic baseline scoring, dev-only threshold selection, ROC-AUC/F1 evaluation, and ablation tracking across evidence layers.
- Created bilingual technical documentation, case-study templates, and a Streamlit demo package with research-use-only safety disclaimers.
- Maintained scientific rigor by marking PubMed/full-agent/verifier ablations as `TODO_NOT_RUN` until real experiments are executed.

## 11. STAR Interview Stories

### Story 1: Building a real benchmark instead of a toy demo

Situation: The original project risked being perceived as a demo without measurable evaluation.

Task: Turn it into a benchmark-driven research project.

Action: I integrated real repoDB data, normalized labels, created balanced pairs, split dev/test,
and added validation/tests.

Result: The project gained a reproducible benchmark foundation and avoided relying on toy examples.

### Story 2: Solving data integration and provenance issues

Situation: Open Targets, repoDB, and PrimeKG use different identifiers and data schemas.

Task: Combine them without losing rows or inventing matches.

Action: I used `pair_id` as the stable join key, added availability flags, retained missing rows,
and recorded provenance/status fields.

Result: The unified table preserved all 200 repoDB pairs and made coverage gaps explicit.

### Story 3: Interpreting weak baseline results honestly

Situation: The baseline accuracy was only 0.50.

Task: Explain the result without overclaiming or hiding it.

Action: I analyzed the all-positive threshold behavior and connected it to the difference between
mechanism evidence and clinical success.

Result: The project became more credible because it treated weak baselines as scientific signal and
motivated the next experiments.

## 12. 项目局限与下一步

当前局限：

- Disease normalization 还比较保守。
- OT/graph 只覆盖 50/200 pairs。
- PubMed-only baseline 没跑。
- Full OrphanCure pipeline 没跑。
- Verifier ablation 没跑。
- Website 还需要部署到 Streamlit Community Cloud。
- Case studies 还没有 manual biomedical review。

下一步：

- 扩展到 200 pairs。
- 加入 MONDO/UMLS/MeSH/DO normalization。
- 跑 PubMed-only baseline。
- 在 20-50 pairs 上跑 full agent。
- 跑 verifier 和 target-expansion ablation。
- 人工 review 3-5 个 case studies。
- 部署并测试 public demo。

## 13. 医学安全边界

OrphanCure 是 research support，不是 medical advice。它不能用于临床决策。

Open Targets target support 不等于临床证据。PrimeKG graph connectivity 不等于疗效
证明。repoDB 的 `negative_or_failed` 也是 proxy label，不代表一个药物在生物学上
完全无效。

面试时需要主动说明这个边界，这反而会增强项目可信度。
## Phase 6C 补充：Full OrphanCure Agent Evaluation

Phase 6C 的意义是把项目从“证据层 baseline evaluation”推进到“agent pipeline evaluation”。
前面的 `opentargets_only`、`graph_only`、`pubmed_only` 都是透明的 evidence-only baseline：
它们只使用结构化特征或文献共现分数，不生成研究报告，也不进行 LLM synthesis。

Full OrphanCure agent 则不同。它的目标是把 PubMed 文献、Open Targets target evidence、
PrimeKG graph mechanism evidence、LLM evidence synthesis、claim verifier、quality gate
和 final report generation 串成一个完整流程。当前代码中的入口是
`app/orchestrator/pipeline.py::Pipeline.run_full()`；Phase 6C 新增了
`app/evaluation/full_pipeline_eval.py` 和 `scripts/run_full_pipeline_eval.py`，用于把这个流程
接入 repoDB benchmark evaluation。

本阶段支持的 ablation modes 包括：

- `full`
- `no_verifier`
- `no_target_expansion`
- `no_graph_features`
- `pubmed_only_report`
- `structured_only_report`

当前真实 full-agent run 没有执行，因为本地环境没有配置 `GEMINI_API_KEY`。因此 Phase 6C
只生成了 20 个 selected pairs 的 `TODO_NOT_RUN` artifact，用来证明 evaluation harness
可以选择样本、保存 raw output、生成 normalized CSV、写 summary metrics，并且在缺少 LLM key
时不会伪造报告、PMID、claims、predictions 或 metrics。

面试中可以这样解释：Phase 6C 不是为了“硬跑一个看起来漂亮的 agent result”，而是为了建立
严谨的 full-agent evaluation protocol。只有在真实 API key 和真实 pipeline output 存在时，
才报告 full-agent accuracy、F1、claim verification rate、unsupported claim rate 和 runtime。
这体现了项目的科研可信度：能跑 baseline，也能诚实标记 TODO_NOT_RUN。
## Phase 6C-B 更新：真实 full-agent smoke run 已完成

在配置 `GEMINI_API_KEY` 后，Phase 6C-B 已经运行了真实的 full OrphanCure agent
smoke evaluation。为了控制成本和风险，本次只选择 evidence availability 最高的 5 个
repoDB pairs。

结果需要这样解释：

- selected pairs: 5
- full mode completed: 4
- failed: 1
- full mode accuracy: 0.5
- full mode F1: 0.6666666666666666
- full mode ROC-AUC: 0.0
- citation verified rate: 1.0
- unsupported claim rate: 0.0
- mean runtime: 18.4490972999949 seconds

同时也跑了三个 ablation：`no_verifier`、`no_target_expansion`、`no_graph_features`。
其中 `no_verifier` 的 unsupported claim rate 是 1.0，这很好地说明 verifier 的作用：
它不是为了让 accuracy 看起来更高，而是为了降低 unsupported claims，提升 report
faithfulness 和 provenance quality。

面试时要主动强调：这只是 5-pair smoke test，不是 clinical validation，也不是最终模型性能。
一个 pair 在所有 full-agent modes 中都失败，错误是 `'NoneType' object has no attribute 'get'`。
这个失败被保留下来，没有被删除或伪造结果。下一步应该先 debug 这个 failure mode，再把
full-agent evaluation 扩展到 20-50 pairs。
## Phase 6C-C 更新：修复失败 pair，并扩展到 20 pairs

Phase 6C-B 中反复失败的 pair 是：

- `repodb_0ee62470d8ffb2ae`
- Cisplatin / Esophageal neoplasm metastatic

真正的 root cause 在 mechanism discovery 阶段：Open Targets 对这个 drug 返回了
`None`，导致 `MechanismAgent._extract_drug_targets()` 对 `state.drug_data.get(...)`
调用时报错。修复后，missing Open Targets drug/disease details 会被当作 missing evidence，
记录 warning，并以 zero targets 继续运行，而不是 crash。

修复后重新跑同样的 5-pair full mode，结果是 5/5 completed，0 failed。之后扩展到
20 selected pairs：

- `full`: 16 completed, 4 partial_success, 0 failed, F1 = 0.4
- `no_verifier`: 16 completed, 4 partial_success, 0 failed, F1 = 0.375
- `no_target_expansion`: 15 completed, 5 partial_success, 0 failed, F1 = 0.5
- `no_graph_features`: 16 completed, 4 partial_success, 0 failed, F1 = 0.5

最重要的解释不是 full pipeline 的 accuracy 有多高，而是 verifier 的作用更清楚了：
`no_verifier` 的 unsupported claim rate 是 1.0，而 full mode 是 0.0625。也就是说，
verifier 对 report faithfulness / provenance quality 有明显作用。与此同时，label metrics
仍然较弱，说明 repoDB proxy label prediction 不是这个 smoke test 已经解决的问题。
## Phase 6D 补充：Case Study Analysis

Phase 6D 的目标不是把 OrphanCure 包装成“已经可以做临床预测”的系统，而是把 20-pair full-agent run 里真实产生的报告、证据和 verifier 输出整理成可以人工 review 的 case studies。这样面试时可以清楚说明：这个项目不仅有 benchmark 和 baseline，也有 agent report 的 provenance、failure mode 和 safety boundary。

本阶段选择了 5 个代表性案例：

| Case | pair_id | Drug | Disease | repoDB label | Full prediction | Case type | Review status |
|---|---|---|---|---|---|---|---|
| 1 | `repodb_0557bc43eff59f45` | Theophylline | Asthma | `positive` | `positive` | `correct_positive` | `TODO_MANUAL_REVIEW` |
| 2 | `repodb_118c436e16e1ab51` | Paclitaxel | Testicular Germ Cell Tumor | `negative_or_failed` | `negative_or_failed` | `correct_negative_or_failed` | `TODO_MANUAL_REVIEW` |
| 3 | `repodb_04246cb3a1c31ef7` | Progesterone | Premature Birth | `negative_or_failed` | `positive` | `verifier_effect` | `TODO_MANUAL_REVIEW` |
| 4 | `repodb_0ee62470d8ffb2ae` | Cisplatin | Esophageal neoplasm metastatic | `negative_or_failed` | `positive` | `incorrect_but_informative` | `TODO_MANUAL_REVIEW` |
| 5 | `repodb_04ab2c145755011f` | Azacitidine | Myelofibrosis due to another disorder | `negative_or_failed` | `unknown` | `partial_success_error_analysis` | `TODO_MANUAL_REVIEW` |

面试中可以这样解释这些 case：

- 30 秒版本：我从真实 full-agent 输出里挑了 5 个案例，不只展示成功案例，也展示 verifier effect、预测错误和 partial_success。每个案例都保留 pair_id、PubMed PMID、Open Targets feature、PrimeKG path、generated claims 和 verification status，目的是让结果可以被人工审查，而不是让 LLM 直接给结论。
- 2 分钟版本：这个阶段体现了 OrphanCure 和普通 LLM wrapper 的区别。普通 wrapper 往往只给自然语言答案；OrphanCure 会把 repoDB proxy label、PubMed retrieval、Open Targets target evidence、PrimeKG graph evidence 和 verifier 输出统一到同一个 case 文件里。即使 full pipeline 的 label metrics 不强，case studies 仍然能展示系统在 evidence grounding、citation checking、unsupported claim reduction 和 failure analysis 上的工程价值。

如果面试官问 “为什么 full pipeline accuracy 不高？” 可以回答：repoDB 的 `negative_or_failed` 是 proxy label，失败临床试验也可能有机制证据和文献共现；full agent 的主要目标不是在 20 个 selected pairs 上训练/调参出高 accuracy，而是生成可追溯的 biomedical evidence report。当前最有意义的信号是 verifier 把 unsupported claim rate 从 `no_verifier` 的 1.0 降到 full mode 的 0.0625。

如果面试官问 “为什么 verifier 更重要？” 可以回答：在 biomedical agent 里，安全边界和 provenance 比漂亮的自然语言更重要。Verifier 不保证医学真理，但它能把没有 citation support 的 claim 标出来，降低 report hallucination risk，让系统更适合作为 research-support tool。

这些案例仍然全部标记为 `TODO_MANUAL_REVIEW`。在人工检查 repoDB 原始行、PubMed abstracts、Open Targets mappings、PrimeKG paths、generated claims 和 citations 之前，不能把任何 case 写成确定性的医学结论。
