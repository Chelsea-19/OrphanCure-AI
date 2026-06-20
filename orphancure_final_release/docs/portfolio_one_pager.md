# OrphanCure Portfolio One-Pager

**Project:** OrphanCure  
**Positioning:** Benchmark-driven biomedical AI agent evaluation framework for
drug-disease evidence assessment.  
**Status:** Research demo, not medical advice.

## Summary

OrphanCure turns a biomedical agent demo into a benchmark-driven evaluation
system. It combines repoDB proxy labels, PubMed literature features, Open
Targets target evidence, PrimeKG graph mechanism features, LLM synthesis, claim
verification, ablation analysis, scaling diagnostics, and manually reviewable
case studies.

## My Engineering Contribution

- Built a balanced repoDB benchmark with 200 drug-disease pairs.
- Integrated PubMed, Open Targets, and PrimeKG evidence layers.
- Created unified feature tables and reproducible evaluation scripts.
- Added full-agent diagnostics, verifier ablation, alternative scoring, and
  triage analysis.
- Packaged a GitHub-ready and Streamlit Cloud-ready demo release.

## Key Results

| Item | Result |
|---|---:|
| repoDB benchmark | 200 balanced pairs |
| 50-pair full run | 42 completed / 8 partial / 0 failed |
| 50-pair original F1 | 0.5333 |
| 50-pair safety_penalized_score F1 | 0.7018 |
| 50-pair full unsupported claim rate | 0.1090 |
| 50-pair no_verifier unsupported claim rate | 1.0000 |

## Interview Talking Point

The main value is not claiming clinical prediction performance. The value is
showing how to evaluate a biomedical AI agent with benchmark labels, provenance,
evidence coverage, verifier behavior, ablations, calibration diagnostics, and
clear safety constraints.

## Safety

This project does not recommend treatments. repoDB labels are proxy labels,
PubMed co-mention is not efficacy evidence, and generated biomedical reports
require expert manual review.
