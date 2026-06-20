# Interview Q&A

## 1. Is OrphanCure just an LLM wrapper?

No. The LLM is only the synthesis layer. The project includes a repoDB benchmark, PubMed/Open Targets/PrimeKG evidence layers, unified feature tables, verifier ablation, calibration diagnostics, triage, and release packaging.

## 2. Why was original full-agent F1 modest?

The main causes were false negatives, recall loss, raw confidence calibration, and partial-success rows. The 50-pair error analysis counted TP 12, TN 9, FP 9, FN 12, and 8 partial rows.

## 3. Why did safety_penalized_score perform better?

It penalizes unsupported claims and incomplete outputs while preserving evidence strength, so it better matched the benchmark diagnostics than raw LLM confidence.

## 4. Why is the verifier important?

It measures faithfulness, not just prediction. On the 50-pair run, unsupported claim rate was 0.1090 in full mode and 1.0 in no-verifier mode.

## 5. Why can no_verifier have similar or better F1 sometimes?

A model can make bolder predictions and sometimes match proxy labels while generating unsupported biomedical claims. F1 and safety are different axes.

## 6. Why is repoDB negative_or_failed not a strict negative label?

Failed or discontinued indications can reflect trial design, endpoints, safety, funding, or operational issues. It is a proxy label, not a mechanistic truth label.

## 7. Why is triage better than forced binary prediction?

Biomedical evidence is often incomplete. Triage allows abstention in uncertain score bands instead of forcing a positive/negative decision.

## 8. What would you improve next?

Scale the cohort, improve entity resolution, add literature polarity extraction, perform expert manual review, calibrate confidence, and make claim verification more granular.

## 9. How is this similar to DocReranker?

Both projects use benchmark construction, baselines, ablations, metrics, and engineering-oriented documentation.

## 10. How is this different from DocReranker?

DocReranker evaluates retrieval/reranking with metrics such as Recall@K. OrphanCure evaluates biomedical evidence assessment with F1, ROC-AUC, unsupported claim rate, triage coverage, and manual review status.
