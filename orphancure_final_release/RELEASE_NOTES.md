# Release Notes

## v0.1.0-research-demo

Release date: 2026-06-04

This release packages OrphanCure as a GitHub-ready and Streamlit
Cloud-deployable research demo.

Included:

- English technical report in LaTeX.
- English manuscript-style draft in LaTeX.
- Chinese interview-oriented Markdown notes.
- Demo-mode Streamlit app.
- Public-safe sample evaluation summaries.
- Selected case-study metadata and markdown packets.
- Deployment, contribution, security, citation, and audit files.

Key bundled results:

- repoDB benchmark: 200 balanced pairs, 100 positive and 100 negative_or_failed.
- PubMed feature run: 50 pair-feature rows and 37/50 evidence-available pairs.
- Open Targets feature run: 50 rows with earlier drug resolution rate 1.0 and
  disease resolution rate 0.82.
- PrimeKG feature run: 50 rows with earlier drug mapping rate 0.98 and disease
  mapping rate 0.16.
- 50-pair full-agent run: 42 completed, 8 partial_success, 0 failed.
- 50-pair original full-agent F1: 0.5333.
- 50-pair safety_penalized_score F1: 0.7018.
- 50-pair full unsupported claim rate: 0.1090.
- 50-pair no_verifier unsupported claim rate: 1.0.

Not included:

- API keys.
- `.env` files.
- raw external data.
- full PubMed cache.
- Open Targets cache.
- full PrimeKG raw graph.

All biomedical case studies remain `TODO_MANUAL_REVIEW`.
