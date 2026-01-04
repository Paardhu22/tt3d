"""Stage 2: Generate world JSON from refined prompt with strict schema validation."""
import json
import logging
from typing import Final

from app.ai_client import openai_client
from app.schemas import WorldResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT: Final[str] = (
    "You are a 3D world generation planner. "
    "You must produce STRICT JSON that conforms to the provided schema. "
    "No markdown. No extra text. No comments. No code fences. "
    "Only output JSON."
)

SCHEMA_INSTRUCTIONS: Final[str] = (
    "Schema:\n"
    "{\n"
    "  \"world_plan\": {\n"
    "    \"environment\": string,\n"
    "    \"mood\": string,\n"
    "    \"style\": string,\n"
    "    \"scale\": one of [small, medium, large, huge, massive],\n"
    "    \"description\": string (detailed 200+ chars),\n"
    "    \"skybox\": string (describe sky, atmosphere, horizon, weather),\n"
    "    \"ambient_music\": string (music mood: epic, peaceful, mysterious, upbeat, etc)\n"
    "  },\n"
    "  \"objects\": [\n"
    "    {\n"
    "      \"name\": string,\n"
    "      \"description\": string (very detailed, 50+ chars),\n"
    "      \"position_hint\": one of [center, front, back, left, right, far_left, far_right, front_left, front_right, back_left, back_right],\n"
    "      \"scale_hint\": one of [small, medium, large, huge]\n"
    "    }\n"
    "  ],\n"
    "  \"lighting\": {\n"
    "    \"mood\": one of [bright, neutral, dark, warm, cool],\n"
    "    \"ambient_intensity\": number 0.0-2.0,\n"
    "    \"primary_light\": string\n"
    "  },\n"
    "  \"camera\": {\n"
    "    \"position\": [x,y,z],\n"
    "    \"target\": [x,y,z],\n"
    "    \"fov\": number 10-120\n"
    "  }\n"
    "}\n"
    "Requirements: 10-25 objects for rich, detailed worlds; descriptions must be vivid and specific; "
    "include skybox description for complete environment; suggest ambient music mood."
)


def generate_world(refined_prompt: str) -> WorldResponse:
    """Generate a world JSON and validate strictly against the schema."""
    if not refined_prompt or not refined_prompt.strip():
        raise ValueError("refined_prompt must be non-empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": SCHEMA_INSTRUCTIONS},
        {"role": "user", "content": refined_prompt.strip()},
    ]

    raw = openai_client.chat(
        messages,
        max_tokens=900,
        response_format={"type": "json_object"},
    )

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.exception("AI returned non-JSON payload")
        raise RuntimeError("Invalid JSON from AI") from exc

    try:
        world = WorldResponse.model_validate(payload)
    except Exception as exc:
        logger.exception("Schema validation failed")
        raise RuntimeError("AI output failed schema validation") from exc

    logger.info("World JSON generated and validated")
    return world
