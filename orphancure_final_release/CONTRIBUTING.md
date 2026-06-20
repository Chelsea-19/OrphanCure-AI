# Contributing

Thank you for considering contributions to OrphanCure.

This repository is a research-demo release. Contributions should preserve the
project's safety framing:

- Do not add treatment recommendations.
- Do not present repoDB proxy labels as clinical truth.
- Do not treat PubMed co-mentions as evidence of efficacy.
- Do not commit API keys, `.env` files, caches, or raw external datasets.
- Mark generated biomedical case studies as requiring expert manual review.

Useful contribution areas:

- Documentation corrections.
- Additional public-safe summary visualizations.
- Better demo-mode robustness.
- Reproducibility scripts that avoid bundling raw external data.
- Evaluation diagnostics and calibration improvements.

Before opening a pull request, run:

```bash
python -m pytest -q -p no:cacheprovider
python -m py_compile app/streamlit_app.py
```

If you add LaTeX changes, compile the affected document or update the relevant
`COMPILE_NOTES.md`.
