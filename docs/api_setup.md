# API Setup Guide

## Google AI Studio / Gemini API

OrphanCure-AI Pro uses Google's Gemini models for LLM-powered analysis.

### Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API key**
3. Copy the key

### Setting the Key

**Option A: Environment variable (recommended)**
```bash
# Linux/Mac
export GEMINI_API_KEY=your_key_here

# Windows (PowerShell)
$env:GEMINI_API_KEY = "your_key_here"
```

**Option B: .env file**
```bash
# Create .env from the template
cp .env.example .env

# Edit .env and fill in your key
GEMINI_API_KEY=your_key_here
```

### Models Used

| Model | Role | Tier |
|-------|------|------|
| `gemini-2.5-flash-lite` | Default (all agents) | Free tier friendly |
| `gemini-2.5-flash` | Fallback on error | Free tier friendly |

Models are configurable via environment variables:
```
ORPHANCURE_DEFAULT_MODEL=gemini-2.5-flash-lite
ORPHANCURE_FALLBACK_MODEL=gemini-2.5-flash
```

### Rate Limits

The system includes built-in rate limiting for external APIs:
- PubMed: ~3 requests/second
- OpenTargets: ~5 requests/second
- Gemini: Managed by the SDK

### Security

- API keys are **never** logged, printed, or committed
- The `.env` file is in `.gitignore`
- The sidebar shows key status (loaded/missing) without displaying the key
