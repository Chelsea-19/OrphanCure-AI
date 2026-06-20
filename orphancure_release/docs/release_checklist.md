# OrphanCure Release Checklist

## Repository Safety

- [ ] No `.env` committed.
- [ ] No API keys committed.
- [ ] `.streamlit/secrets.toml` excluded.
- [ ] `data/external/` excluded or documented.
- [ ] Large generated graph data excluded from release package.
- [ ] Source metadata recorded for downloaded datasets.

## Tests And Validation

- [ ] Full tests pass.
- [ ] repoDB validation passes.
- [ ] Open Targets smoke/evaluation outputs are documented.
- [ ] Graph smoke/evaluation outputs are documented.
- [ ] Unified benchmark outputs are generated.
- [ ] Website demo compiles/imports without secrets.

## Documentation

- [ ] Root `README.md` updated.
- [ ] Release `README.md` created.
- [ ] English project report created.
- [ ] Chinese project report created.
- [ ] Implementation status file created.
- [ ] Evaluation documentation updated.
- [ ] Deployment documentation created.
- [ ] Limitations included.
- [ ] Medical disclaimer included.
- [ ] Reproducibility commands documented.

## Release Folder

- [ ] `orphancure_release/` created.
- [ ] No raw repoDB external file copied.
- [ ] No full PrimeKG graph copied.
- [ ] Sample outputs included only when small enough.
- [ ] `.env.example` contains placeholders only.
- [ ] `.streamlit/config.toml` contains no secrets.
- [ ] Case-study templates copied.
- [ ] Public-safe figures copied.
- [ ] Release folder checked before pushing.

## Project Readiness

- [ ] Project report updated.
- [ ] Final project summary generated.
- [ ] Website launches in demo mode.
- [ ] Streamlit Community Cloud deployment instructions included.
- [ ] Hugging Face Spaces optional deployment notes included.
- [ ] Manual biomedical review still clearly marked as pending.
