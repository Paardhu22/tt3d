"""Pydantic schemas describing the world-generation contract."""
from __future__ import annotations

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, conlist, confloat, conint


class WorldDesignSpec(BaseModel):
    """High-level world intent derived from the user's description (Stage 1)."""

    biome: str = Field(..., min_length=3, description="Primary biome such as tundra, desert, forest.")
    terrain_type: str = Field(..., min_length=3, description="Terrain archetype (mountainous, archipelago, mesas).")
    scale_km: confloat(gt=0.1, le=200.0) = Field(..., description="Playable world diameter in kilometers.")
    structures: List[str] = Field(default_factory=list, description="List of key structures or architectural motifs.")
    sky_weather: str = Field(..., min_length=3, description="Sky, weather, atmosphere.")
    mood: str = Field(..., min_length=3, description="Overall tone or emotion.")
    time_of_day: str = Field(..., min_length=3, description="Time of day or lighting condition.")
    landmarks: List[str] = Field(default_factory=list, description="Named landmarks that should appear.")

    class Config:
        extra = "forbid"


class TerrainNoise(BaseModel):
    seed: conint(ge=0, le=2**31 - 1) = 42
    octaves: conint(ge=1, le=10) = 5
    frequency: confloat(gt=0.0001, lt=5.0) = 0.6
    amplitude: confloat(gt=0.0, le=500.0) = 120.0
    lacunarity: confloat(gt=0.1, le=4.0) = 2.1
    persistence: confloat(gt=0.1, le=1.5) = 0.45
    elevation_scale: confloat(gt=0.1, le=2000.0) = 480.0
    base_height: confloat(ge=-500.0, le=1500.0) = 35.0

    class Config:
        extra = "forbid"


class SplineRule(BaseModel):
    name: str = "arterial_road"
    kind: Literal["road", "river"] = "road"
    control_points: List[conlist(float, min_length=3, max_length=3)] = Field(
        ..., description="XYZ control points forming a Catmull-Rom spline."
    )
    width: confloat(gt=0.5, le=200.0) = 12.0
    depth: confloat(ge=0.0, le=80.0) = 2.0
    material: str = "asphalt"

    class Config:
        extra = "forbid"


class ObjectPlacementRule(BaseModel):
    kind: Literal["tower", "hub", "farm", "outpost", "bridge", "spire", "hangar", "dome"] = "tower"
    count: conint(ge=1, le=200) = 12
    scale_range: Tuple[float, float] = (0.8, 1.8)
    height_range: Tuple[float, float] = (12.0, 90.0)
    scatter_radius: confloat(gt=10.0, le=2000.0) = 320.0
    cluster: bool = True

    class Config:
        extra = "forbid"


class VegetationRule(BaseModel):
    density_per_km2: confloat(ge=0.0, le=5000.0) = 320.0
    species: List[str] = Field(default_factory=lambda: ["conifer", "broadleaf", "shrub"])
    max_height: confloat(gt=0.5, le=60.0) = 12.0

    class Config:
        extra = "forbid"


class LightingConfig(BaseModel):
    sun_azimuth: confloat(ge=0.0, le=360.0) = 135.0
    sun_elevation: confloat(ge=-5.0, le=90.0) = 38.0
    ambient_intensity: confloat(gt=0.0, le=3.0) = 0.45
    sky_color: conlist(float, min_length=3, max_length=3) = [0.48, 0.68, 0.96]
    fog_density: confloat(ge=0.0, le=0.2) = 0.02
    exposure: confloat(gt=0.01, le=5.0) = 1.0
    mood: str = "neutral"

    class Config:
        extra = "forbid"


class SkyConfig(BaseModel):
    type: Literal["clear", "cloudy", "storm", "aurora", "stars"] = "clear"
    cloud_density: confloat(ge=0.0, le=1.0) = 0.25
    haze: confloat(ge=0.0, le=1.0) = 0.1

    class Config:
        extra = "forbid"


class WorldSchema(BaseModel):
    """Procedural parameters the engine consumes (Stage 2)."""

    biome: str
    terrain_type: str
    scale_km: confloat(gt=0.1, le=200.0)
    heightmap: TerrainNoise
    terrain_features: List[str] = Field(default_factory=list)
    object_rules: List[ObjectPlacementRule] = Field(default_factory=list)
    splines: List[SplineRule] = Field(default_factory=list)
    vegetation: VegetationRule
    lighting: LightingConfig
    sky: SkyConfig

    class Config:
        extra = "forbid"


class WorldLayoutObject(BaseModel):
    name: str
    position: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    kind: str
    material: str


class WorldLayout(BaseModel):
    terrain_bounds_m: Tuple[float, float]
    objects: List[WorldLayoutObject]
    splines: List[SplineRule]
    vegetation_count: int


class WorldMetadata(BaseModel):
    design: WorldDesignSpec
    schema: WorldSchema
    layout: WorldLayout
    generator: str = "Tsuana Open Pipeline"


class GenerateWorldRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=4000)
    seed: Optional[int] = Field(default=None, description="Deterministic seed for world generation.")


class GenerateWorldResponse(BaseModel):
    world_path: str
    preview_image: str
    unity_import: str
    metadata: WorldMetadata

