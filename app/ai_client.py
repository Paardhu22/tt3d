"""OpenAI client wrapper with deterministic settings and centralized error handling."""
import logging
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)


class OpenAIClient:
    """Encapsulates OpenAI chat completions with deterministic parameters."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._temperature = temperature

    def chat(self, messages: List[Dict[str, str]], *, max_tokens: int = 800, response_format: Dict[str, Any] | None = None) -> str:
        """Call OpenAI chat completions with strict, deterministic parameters."""
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=max_tokens,
                response_format=response_format,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - network failure paths
            logger.exception("OpenAI chat completion failed")
            raise RuntimeError("AI provider error") from exc


# Singleton instance for application use
openai_client = OpenAIClient()
