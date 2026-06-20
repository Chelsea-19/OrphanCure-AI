# Release Audit

Audit date: 2026-06-04

## Safety Scope

This release is a research and educational demo. It is not clinical validation,
not medical advice, and not a treatment recommendation system.

## Included Public-Safe Artifacts

- Summary metrics, compact per-pair result tables, diagnostics tables, and
  selected case-study metadata.
- Compact benchmark sample files needed by the demo.
- Figures generated from existing project outputs.
- Documentation, reports, deployment files, and Streamlit demo code.

## Excluded Artifacts

- `.env` files and API keys.
- `GEMINI_API_KEY`, `PUBMED_EMAIL`, and `NCBI_API_KEY` values.
- raw `data/external/`.
- full PubMed cache.
- Open Targets cache.
- full PrimeKG raw graph edges/nodes.
- Python cache files.
- case review export packet.

## Case Review Status

All selected cases remain `TODO_MANUAL_REVIEW`. No biomedical expert review is
claimed.

## Result Integrity

The release uses existing results supplied by the project. No expensive API
reruns were performed during packaging, and no missing performance values were
fabricated.

## Remaining Audit Items

- Replace placeholder citation author.
- Verify manuscript citations before publication.
- Add final screenshots after Streamlit deployment.
- Re-run release checks after any further edits.
