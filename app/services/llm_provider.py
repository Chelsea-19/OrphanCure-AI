"""Unified LLM provider abstraction for Google Gemini."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai import types

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class GeminiProvider:
    """
    Reusable wrapper around the Google GenAI SDK.

    All agents call LLMs through this single provider, which handles:
    - model selection (default → fallback)
    - JSON-mode responses
    - timeout / error handling
    - temperature control
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: Optional[genai.Client] = None
        self.enabled = False

        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)
            self.enabled = True
            logger.info("GeminiProvider initialised (model=%s)", settings.default_model)
        else:
            logger.warning("GeminiProvider disabled — no GEMINI_API_KEY")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.2,
        use_fallback: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a prompt to Gemini and return the response.

        Returns:
            On success:  {"text": "..."} or parsed JSON dict if json_mode=True
            On failure:  {"error": "..."}
        """
        if not self.enabled:
            return {"error": "LLM provider not configured — set GEMINI_API_KEY"}

        model = self._settings.fallback_model if use_fallback else self._settings.default_model

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            )
            if json_mode:
                config.response_mime_type = "application/json"

            response = self._client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config,
            )

            content = response.text
            if json_mode:
                return json.loads(content)
            return {"text": content}

        except json.JSONDecodeError as exc:
            logger.error("JSON decode error from model %s: %s", model, exc)
            # Retry with fallback model if not already using it
            if not use_fallback:
                logger.info("Retrying with fallback model %s", self._settings.fallback_model)
                return self.generate(
                    system_prompt,
                    user_prompt,
                    json_mode=json_mode,
                    temperature=temperature,
                    use_fallback=True,
                )
            return {"error": f"JSON decode error: {exc}"}

        except Exception as exc:
            logger.error("Gemini call failed (model=%s): %s", model, exc)
            # Retry with fallback on first failure
            if not use_fallback:
                logger.info("Retrying with fallback model %s", self._settings.fallback_model)
                return self.generate(
                    system_prompt,
                    user_prompt,
                    json_mode=json_mode,
                    temperature=temperature,
                    use_fallback=True,
                )
            return {"error": str(exc)}
