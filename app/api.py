"""FastAPI application exposing the open-source world generator."""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from app.schemas import GenerateWorldRequest, GenerateWorldResponse
from core.world_generator import world_generator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Tsuana 3D World Generator", version="2.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "message": "✅ API is running"}


@app.post("/api/v1/world", response_model=GenerateWorldResponse)
def create_world(request: GenerateWorldRequest) -> GenerateWorldResponse:
    try:
        return world_generator.generate(request)
    except ValueError as exc:
        logger.warning("Bad request: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="World generation failed") from exc
