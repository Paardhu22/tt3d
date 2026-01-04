"""Local LLM client that runs fully on open-source models."""
from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Thin wrapper around a local Transformers or Ollama model."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        provider: str | None = None,
    ) -> None:
        self.model = model or os.getenv("LOCAL_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0.25"))
        self.provider = (provider or os.getenv("LLM_PROVIDER", "transformers")).lower()
        self.max_new_tokens = int(os.getenv("LLM_MAX_NEW_TOKENS", "768"))
        self._pipeline = None
        self._lock = threading.Lock()

    def _ensure_pipeline(self):
        if self.provider == "ollama":
            return

        if self._pipeline is not None:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            import torch
        except ImportError as exc:  # pragma: no cover - runtime dependency
            raise RuntimeError(
                "Transformers is required for local LLM usage. Install with `pip install transformers torch`."
            ) from exc

        with self._lock:
            if self._pipeline is not None:
                return
            logger.info("Loading local LLM model '%s' with provider transformers", self.model)
            tokenizer = AutoTokenizer.from_pretrained(self.model)
            model = AutoModelForCausalLM.from_pretrained(
                self.model,
                device_map="auto",
                torch_dtype="auto",
            )
            self._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
            )
            torch.manual_seed(int(os.getenv("LLM_SEED", "42")))

    def chat(self, messages: List[Dict[str, str]], *, max_tokens: int | None = None) -> str:
        """Generate a completion for a chat-style prompt."""
        max_tokens = max_tokens or self.max_new_tokens
        prompt = self._format_messages(messages)

        if self.provider == "ollama":
            return self._ollama_chat(messages, max_tokens=max_tokens)

        self._ensure_pipeline()
        assert self._pipeline is not None  # for type checkers

        result = self._pipeline(
            prompt,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=self.temperature,
            top_p=0.9,
            repetition_penalty=1.05,
            num_return_sequences=1,
            pad_token_id=self._pipeline.tokenizer.eos_token_id,
        )[0]["generated_text"]

        return result[len(prompt) :].strip()

    def _ollama_chat(self, messages: List[Dict[str, str]], *, max_tokens: int) -> str:
        try:
            import ollama  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install `ollama` Python package to use the Ollama provider.") from exc

        client = ollama.Client()
        logger.info("Sending chat to local Ollama model '%s'", self.model)
        response = client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature, "num_predict": max_tokens},
        )
        return response["message"]["content"].strip()

    @staticmethod
    def _format_messages(messages: List[Dict[str, str]]) -> str:
        parts: List[str] = []
        for message in messages:
            role = message.get("role", "user")
            parts.append(f"<|{role}|>\n{message.get('content','').strip()}\n")
        parts.append("<|assistant|>\n")
        return "\n".join(parts)


open_source_llm = LocalLLMClient()
