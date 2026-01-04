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
    # Enhanced terrain parameters for more dramatic landscapes
    octaves = rng.randint(6, 9)  # More detail layers
    frequency = rng.uniform(0.35, 0.65)  # Better mountain formation
    amplitude = rng.uniform(150, 280)  # More dramatic height variations

    # Increased object density and variety for richer scenes
    object_rules: List[ObjectPlacementRule] = [
        ObjectPlacementRule(
            kind="tower",
            count=rng.randint(15, 35),  # More towers
            scale_range=(0.8, 2.2),  # Wider variety
            height_range=(30.0, 120.0),  # Taller structures
            scatter_radius=design.scale_km * 30,
            cluster=True,
        ),
        ObjectPlacementRule(
            kind="spire",
            count=rng.randint(10, 25),  # Add spires
            scale_range=(0.7, 1.8),
            height_range=(40.0, 100.0),
            scatter_radius=design.scale_km * 35,
            cluster=True,
        ),
        ObjectPlacementRule(
            kind="dome",
            count=rng.randint(8, 18),  # Add domes for variety
            scale_range=(1.0, 2.5),
            height_range=(20.0, 50.0),
            scatter_radius=design.scale_km * 28,
            cluster=False,
        ),
        ObjectPlacementRule(
            kind="bridge",
            count=max(4, int(design.scale_km // 4)),  # More bridges
            scale_range=(0.8, 1.6),
            height_range=(12.0, 30.0),
            scatter_radius=design.scale_km * 32,
            cluster=False,
        ),
    ]

    # Create more interesting spline paths with curves
    base_spline = [
        [0.0, 0.0, 0.0],
        [design.scale_km * 120, 0.0, design.scale_km * 180],
        [design.scale_km * 280, 0.0, design.scale_km * 420],
        [design.scale_km * 450, 0.0, design.scale_km * 680],
        [design.scale_km * 580, 0.0, design.scale_km * 850],
    ]
    
    river_spline = [
        [design.scale_km * 0.2, 0.0, -design.scale_km * 150],
        [design.scale_km * 180, 0.0, design.scale_km * 80],
        [design.scale_km * 350, 0.0, design.scale_km * 320],
        [design.scale_km * 520, 0.0, design.scale_km * 550],
        [design.scale_km * 650, 0.0, design.scale_km * 780],
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
            lacunarity=2.2,  # More dramatic terrain features
            persistence=0.52,  # Better detail preservation
            elevation_scale=design.scale_km * 28,  # More elevation range
            base_height=15.0,
        ),
        terrain_features=["dramatic canyons", "soaring plateaus", "river valleys", "mountain peaks"],
        object_rules=object_rules,
        splines=[
            SplineRule(
                name="main_highway",
                kind="road",
                control_points=base_spline,
                width=max(14.0, design.scale_km * 0.5),
                depth=1.5,
                material="asphalt",
            ),
            SplineRule(
                name="scenic_river",
                kind="river",
                control_points=river_spline,
                width=max(20.0, design.scale_km * 1.0),  # Wider river
                depth=6.0,  # Deeper river
                material="water",
            ),
        ],
        vegetation=VegetationRule(
            density_per_km2=450.0,  # Denser vegetation
            species=["oak", "pine", "birch", "willow"] if "forest" in design.biome.lower() else ["palm", "cactus", "shrub"],
            max_height=22.0,  # Taller vegetation
        ),
        lighting=LightingConfig(
            sun_azimuth=145.0,
            sun_elevation=42.0 if "night" not in design.time_of_day.lower() else 8.0,
            ambient_intensity=0.42 if "night" in design.time_of_day.lower() else 0.38,
            sky_color=[0.35, 0.55, 0.85] if "night" in design.time_of_day.lower() else [0.52, 0.70, 0.95],
            fog_density=0.015,  # Subtle atmospheric fog
            exposure=1.15,  # Brighter, more vibrant
            mood=design.mood,
        ),
        sky=SkyConfig(
            type="stars" if "night" in design.time_of_day.lower() else "cloudy",
            cloud_density=0.35,  # More dramatic clouds
            haze=0.12,  # Enhanced atmospheric haze
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
