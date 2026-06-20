# OrphanCure Deployment Guide

## A. Streamlit Community Cloud

1. Create a new GitHub repository from the `orphancure_release/` folder.
2. Push the release folder contents to GitHub.
3. In Streamlit Community Cloud, create a new app from that repository.
4. Set the main file path to:

```text
app/streamlit_app.py
```

5. Use demo mode by default. No secrets are required for the public demo:

```text
DEMO_MODE=true
```

6. If future live API features are added, configure secrets in Streamlit Cloud
   rather than committing them.

Example optional secrets:

```toml
DEMO_MODE = "false"
OPENTARGETS_API_URL = "https://api.platform.opentargets.org/api/v4/graphql"
PUBMED_EMAIL = "your-email@example.com"
NCBI_API_KEY = "optional"
GEMINI_API_KEY = "optional"
```

The current demo does not require these values.

The PubMed tab also runs in demo mode. It does not call NCBI unless future
developers explicitly add and configure live retrieval behavior.

## B. Local Deployment

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app loads sample outputs if present and falls back to embedded summary
values if sample files are missing.

## C. Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `DEMO_MODE` | No | Defaults to `true`; keeps the app in sample-output mode |
| `OPENTARGETS_API_URL` | No | Future live Open Targets API endpoint |
| `PUBMED_EMAIL` | No | Future PubMed/NCBI contact email |
| `NCBI_API_KEY` | No | Future NCBI API key |
| `GEMINI_API_KEY` | No | Future LLM-backed synthesis key |

Do not commit `.env` or Streamlit secrets.

## D. Data Limitations

The release package does not include:

- full `data/external/repodb.csv`,
- Open Targets cache files,
- the full PrimeKG graph,
- the 4.1M-edge normalized graph CSV,
- API keys or local secrets.

Users can reproduce the benchmark by downloading repoDB and PrimeKG themselves
and running the scripts in `scripts/`.

## E. Hugging Face Spaces Optional Deployment

Hugging Face Spaces can also host Streamlit apps:

1. Create a new Space with the Streamlit SDK.
2. Upload the release folder contents.
3. Keep `app/streamlit_app.py` as the main app file.
4. Add secrets through the Space settings only if future live API features are
   enabled.

## F. Safety Disclaimer

This demo is for research and educational purposes only. It is not medical
advice and must not be used for clinical decision-making.
