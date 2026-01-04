"""Stage 2: Generate strict procedural schema for the world."""
from __future__ import annotations

import json
import logging
import random
from typing import Final, List

from app.ai_client import open_source_llm
from app.schemas import (
    LightingConfig,
    ObjectPlacementRule,
    SkyConfig,
    TerrainNoise,
    VegetationRule,
    WorldDesignSpec,
    WorldSchema,
    SplineRule,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT: Final[str] = (
    "You are a procedural world-systems architect. Produce STRICT JSON that the generator will consume. "
    "Only output JSON, never prose."
)

SCHEMA_PROMPT: Final[str] = """
{
  "biome": "string",
  "terrain_type": "string",
  "scale_km": 30.0,
  "heightmap": {
    "seed": 42,
    "octaves": 6,
    "frequency": 0.45,
    "amplitude": 160.0,
    "lacunarity": 2.0,
    "persistence": 0.48,
    "elevation_scale": 520.0,
    "base_height": 24.0
  },
  "terrain_features": ["canyons", "plateaus"],
  "object_rules": [
    {
      "kind": "tower",
      "count": 18,
      "scale_range": [0.8, 1.6],
      "height_range": [20.0, 80.0],
      "scatter_radius": 420.0,
      "cluster": true
    }
  ],
  "splines": [
    {
      "name": "main_artery",
      "kind": "road",
      "control_points": [[0,0,0],[150,0,400],[420,0,900],[820,0,1200]],
      "width": 18.0,
      "depth": 1.8,
      "material": "asphalt"
    }
  ],
  "vegetation": {
    "density_per_km2": 380.0,
    "species": ["pine","birch","moss"],
    "max_height": 16.0
  },
  "lighting": {
    "sun_azimuth": 130.0,
    "sun_elevation": 35.0,
    "ambient_intensity": 0.45,
    "sky_color": [0.52,0.68,0.94],
    "fog_density": 0.015,
    "exposure": 1.05,
    "mood": "neutral"
  },
  "sky": {
    "type": "cloudy",
    "cloud_density": 0.35,
    "haze": 0.12
  }
}
"""

MAX_SEED_SPACE: Final[int] = 2**20


def _fallback_schema(design: WorldDesignSpec, seed: int | None) -> WorldSchema:
    rng = random.Random(seed or 42)

    base_seed = rng.randint(0, MAX_SEED_SPACE)
    octaves = rng.randint(4, 7)
    frequency = rng.uniform(0.3, 0.8)
    amplitude = rng.uniform(90, 210)

    object_rules: List[ObjectPlacementRule] = [
        ObjectPlacementRule(
            kind="tower",
            count=rng.randint(8, 22),
            scale_range=(0.9, 1.6),
            height_range=(24.0, 90.0),
            scatter_radius=design.scale_km * 25,
            cluster=True,
        ),
        ObjectPlacementRule(
            kind="bridge",
            count=max(2, int(design.scale_km // 5)),
            scale_range=(0.6, 1.3),
            height_range=(8.0, 22.0),
            scatter_radius=design.scale_km * 30,
            cluster=False,
        ),
    ]

    base_spline = [
        [0.0, 0.0, 0.0],
        [design.scale_km * 180, 0.0, design.scale_km * 260],
        [design.scale_km * 520, 0.0, design.scale_km * 720],
    ]

    return WorldSchema(
        biome=design.biome,
        terrain_type=design.terrain_type,
        scale_km=design.scale_km,
        heightmap=TerrainNoise(
            seed=base_seed,
            octaves=octaves,
            frequency=frequency,
            amplitude=amplitude,
            lacunarity=2.0,
            persistence=0.5,
            elevation_scale=design.scale_km * 20,
            base_height=12.0,
        ),
        terrain_features=["canyons", "plateaus", "river deltas"],
        object_rules=object_rules,
        splines=[
            SplineRule(
                name="arterial_route",
                kind="road",
                control_points=base_spline,
                width=max(12.0, design.scale_km * 0.4),
                depth=1.2,
                material="stone",
            ),
            SplineRule(
                name="primary_river",
                kind="river",
                control_points=[
                    [design.scale_km * 0.5, 0.0, -design.scale_km * 120],
                    [design.scale_km * 220, 0.0, design.scale_km * 110],
                    [design.scale_km * 520, 0.0, design.scale_km * 420],
                ],
                width=max(16.0, design.scale_km * 0.8),
                depth=5.0,
                material="water",
            ),
        ],
        vegetation=VegetationRule(
            density_per_km2=280.0,
            species=["oak", "pine", "bamboo"] if "forest" in design.biome.lower() else ["shrub", "grass"],
            max_height=18.0,
        ),
        lighting=LightingConfig(
            sun_azimuth=135.0,
            sun_elevation=32.0 if "night" not in design.time_of_day.lower() else 6.0,
            ambient_intensity=0.52 if "night" in design.time_of_day.lower() else 0.35,
            sky_color=[0.42, 0.52, 0.72],
            fog_density=0.02,
            exposure=1.1,
            mood=design.mood,
        ),
        sky=SkyConfig(
            type="stars" if "night" in design.time_of_day.lower() else "cloudy",
            cloud_density=0.25,
            haze=0.08,
        ),
    )


def generate_world_schema(design: WorldDesignSpec, *, seed: int | None = None) -> WorldSchema:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Schema: {SCHEMA_PROMPT}"},
        {"role": "user", "content": design.model_dump_json()},
    ]

    try:
        content = open_source_llm.chat(messages, max_tokens=900)
        data = json.loads(content)
        schema = WorldSchema.model_validate(data)
        logger.info("World schema generated via LLM")
        return schema
    except Exception as exc:
        logger.warning("LLM schema generation failed (%s); using deterministic fallback", exc)
        return _fallback_schema(design, seed)
