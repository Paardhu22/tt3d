"""Pydantic schemas for world generation responses.
Strict validation ensures Unity only receives clean, contract-compliant JSON.
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, conlist, confloat, constr


class Camera(BaseModel):
    position: conlist(float, min_length=3, max_length=3)
    target: conlist(float, min_length=3, max_length=3)
    fov: confloat(ge=10, le=120) = 60.0

    class Config:
        extra = "forbid"


class Lighting(BaseModel):
    mood: Literal["bright", "neutral", "dark", "warm", "cool"] = "neutral"
    ambient_intensity: confloat(ge=0.0, le=2.0) = 0.4
    primary_light: constr(min_length=3, max_length=400) = "key light from front-left"

    class Config:
        extra = "forbid"


class WorldObject(BaseModel):
    name: constr(min_length=2, max_length=80)
    description: constr(min_length=10, max_length=800)
    position_hint: Literal[
        "center",
        "front",
        "back",
        "left",
        "right",
        "far_left",
        "far_right",
        "front_left",
        "front_right",
        "back_left",
        "back_right",
    ] = "center"
    scale_hint: Literal["small", "medium", "large", "huge"] = "medium"

    class Config:
        extra = "forbid"


class WorldPlan(BaseModel):
    environment: constr(min_length=3, max_length=200)
    mood: constr(min_length=3, max_length=100)
    style: constr(min_length=3, max_length=100)
    scale: constr(min_length=3, max_length=100)
    description: constr(min_length=10, max_length=800)

    class Config:
        extra = "forbid"


class WorldResponse(BaseModel):
    world_plan: WorldPlan
    objects: conlist(WorldObject, min_length=5, max_length=30)  # Increased for larger worlds
    lighting: Lighting
    camera: Camera

    class Config:
        extra = "forbid"
