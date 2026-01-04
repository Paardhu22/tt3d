"""Stage 1: Generate a refined world-building prompt from raw user input."""
import logging
from typing import Final

from app.ai_client import openai_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT: Final[str] = (
    "You are a senior world-building prompt engineer. "
    "Given a raw user description, rewrite it into a concise, vivid, professional 3D world-building prompt. "
    "Do not add metadata, JSON, or any brackets. Do not add greetings. "
    "Keep it under 120 words."
)


def generate_prompt(raw_description: str) -> str:
    """Produce a refined prompt from user input (plain text only)."""
    if not raw_description or not raw_description.strip():
        raise ValueError("raw_description must be non-empty")

    logger.info(f"📝 Generating refined prompt from: '{raw_description[:50]}...'")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": raw_description.strip()},
    ]

    prompt = openai_client.chat(messages, max_tokens=400)

    if not prompt:
        raise RuntimeError("Empty prompt generated")

    logger.info(f"✅ Prompt generated successfully: '{prompt[:100]}...'")
    return prompt
