# Deployment

## Local Setup

```bash
cd orphancure_final_release
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app runs in demo mode by default and reads bundled summary artifacts.

## Streamlit Cloud

1. Push this folder to a GitHub repository.
2. Open Streamlit Cloud and create a new app.
3. Choose the GitHub repository.
4. Set the main file path to `app/streamlit_app.py`.
5. Deploy.

No secrets are needed for demo mode.

## Optional Secrets

Future live workflows may use:

```text
GEMINI_API_KEY=
PUBMED_EMAIL=
NCBI_API_KEY=
DEMO_MODE=true
```

The current release app does not call live APIs by default.

## Data Requirements

No raw data is needed for the demo. The app uses:

- `eval_results_sample/`
- `data_sample/benchmark/`
- `docs/case_studies/`
- `docs/figures/`

Do not upload raw external data, PubMed caches, Open Targets caches, or the full
PrimeKG graph to Streamlit Cloud.

## Troubleshooting

- If the app cannot find a table, confirm the release tree was uploaded intact.
- If image captions appear without plots, confirm `docs/figures/*.png` exists.
- If dependency installation fails, check that `requirements.txt` is unchanged.
- If Streamlit asks for secrets, confirm `DEMO_MODE=true` and no live workflow
  has been added.
