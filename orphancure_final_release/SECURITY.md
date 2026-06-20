# Security Policy

## Supported Version

This release is `v0.1.0-research-demo`.

## Sensitive Data Policy

Do not commit:

- API keys or `.env` files.
- PubMed, Open Targets, or other API response caches.
- Full PrimeKG raw graph files.
- Raw external biomedical datasets.
- Personal or private clinical data.

The Streamlit app runs in demo mode by default and should not call live APIs
unless a future maintainer explicitly implements and documents that behavior.

## Reporting Issues

For public releases, report security issues through the GitHub repository's
private vulnerability reporting channel if enabled. Until then, open a private
maintainer channel before posting sensitive details publicly.
