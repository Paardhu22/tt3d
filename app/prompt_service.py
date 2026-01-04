"""Stage 1: Convert raw user description into a structured world design spec."""
from __future__ import annotations

import json
import logging
import random
from typing import Final

from app.ai_client import open_source_llm
from app.schemas import WorldDesignSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT: Final[str] = (
    "You are a senior world architect. Convert the raw description into a concise world design spec. "
    "Respond ONLY with JSON following the schema. Use immersive, VR-scale assumptions."
)

SCHEMA: Final[str] = """
{
  "biome": "string biome name",
  "terrain_type": "string terrain archetype",
  "scale_km": 25.0,
  "structures": ["primary structures and architectural motifs"],
  "sky_weather": "sky and weather description",
  "mood": "emotional tone",
  "time_of_day": "time of day",
  "landmarks": ["major landmarks to anchor navigation"]
}
"""


def _fallback_spec(description: str, seed: int | None) -> WorldDesignSpec:
    random.seed(seed or 42)
    terrains = ["mountainous", "archipelago", "rolling hills", "canyon", "mesa plateau", "coastal cliffs"]
    weathers = ["overcast with distant storms", "crisp blue sky", "misty horizon", "twilight haze", "aurora filled night"]
    moods = ["mysterious", "epic", "serene", "hopeful", "ominous"]
    times = ["golden hour", "midnight", "dawn", "dusk"]
    scale = random.choice([12, 18, 25, 40, 60])

    description_lower = description.lower()
    biome = "forest" if "forest" in description_lower else "desert" if "desert" in description_lower else "mixed biomes"

    return WorldDesignSpec(
        biome=biome,
        terrain_type=random.choice(terrains),
        scale_km=float(scale),
        structures=["floating platforms", "bridges", "modular towers"],
        sky_weather=random.choice(weathers),
        mood=random.choice(moods),
        time_of_day=random.choice(times),
        landmarks=["central hub", "northern ridge", "eastern river delta"],
    )


def generate_design_spec(raw_description: str, *, seed: int | None = None) -> WorldDesignSpec:
    if not raw_description or not raw_description.strip():
        raise ValueError("description must be non-empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Schema: {SCHEMA}"},
        {"role": "user", "content": raw_description.strip()},
    ]

    try:
        content = open_source_llm.chat(messages, max_tokens=600)
        data = json.loads(content)
        spec = WorldDesignSpec.model_validate(data)
        logger.info("World design spec generated via LLM")
        return spec
    except Exception as exc:
        logger.warning("LLM design spec generation failed (%s); using deterministic fallback", exc)
        return _fallback_spec(raw_description, seed)
