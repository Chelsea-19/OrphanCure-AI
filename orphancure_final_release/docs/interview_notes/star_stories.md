# STAR Stories

## Story 1: Turning a demo into a benchmark-driven evaluation framework

**Situation:** The project initially resembled a biomedical report generation demo.  
**Task:** Make it measurable, reproducible, and interview-ready.  
**Action:** Added repoDB benchmark construction, PubMed/Open Targets/PrimeKG evidence layers, unified feature tables, and evaluation scripts.  
**Result:** The project became a benchmark-driven evaluation framework with documented metrics and safety boundaries.

## Story 2: Debugging full-agent pipeline failure

**Situation:** Full-agent runs produced partial_success rows and incomplete outputs.  
**Task:** Preserve auditability without overstating success.  
**Action:** Kept partial_success status, added error analysis, and reported completed / partial / failed counts.  
**Result:** The 50-pair run honestly reported 42 completed, 8 partial_success, and 0 failed rows.

## Story 3: Improving prediction diagnostics without fabricating results

**Situation:** Original full-agent F1 was modest.  
**Task:** Explain and improve diagnostics without inventing results.  
**Action:** Analyzed false negatives, partial rows, raw confidence calibration, and added safety_penalized_score.  
**Result:** The 50-pair safety_penalized_score reached F1 0.7018 and ROC-AUC 0.6464.

## Story 4: Verifier ablation and biomedical safety

**Situation:** LLM-generated biomedical reports risk unsupported claims.  
**Task:** Quantify whether verification actually helps.  
**Action:** Compared full mode against no_verifier on unsupported claim rate and citation verification.  
**Result:** The 50-pair unsupported claim rate was 0.1090 in full mode versus 1.0 in no_verifier mode.
