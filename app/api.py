"""FastAPI application exposing the Text/Voice → 3D World generation pipeline."""
import logging
import json
import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List, Dict

from app.prompt_service import generate_prompt
from app.world_service import generate_world
from app.schemas import WorldResponse
from core.threed_generator import StabilityAIGenerator
from core.music_generator import generate_world_music

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Tsuana 3D World Generator", version="1.0.0")

# Ensure output directory exists
OUTPUT_DIR = Path("output/generated_worlds")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class GenerateWorldRequest(BaseModel):
    description: constr(min_length=3, max_length=2000)


class GenerateWorldResponse(BaseModel):
    world: WorldResponse
    saved_to: str
    music_path: str | None = None
    models: List[Dict[str, str]]  # List of {name, path, format}
    messages: list[str]
    status: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "message": "✅ API is running"}


@app.post("/api/v1/world", response_model=GenerateWorldResponse)
def create_world(body: GenerateWorldRequest):
    """Generate a complete 3D world from text description.
    
    Advanced pipeline: AI refinement -> large world JSON -> 3D model (GLB) -> ambient music.
    """
    messages = []
    generated_models = []
    music_path = None
    
    try:
        # Stage 1: Prompt refinement
        messages.append("🔄 Stage 1: Refining your description...")
        logger.info("Starting prompt refinement")
        refined_prompt = generate_prompt(body.description)
        messages.append(f"✅ Stage 1 Complete: Generated refined prompt ({len(refined_prompt)} chars)")
        
        # Stage 2: World generation
        messages.append(f"  📦 Generated {world.world_plan.scale} world with {len(world.objects)} objects")
        
        # Display world info
        if world.world_plan.skybox:
            messages.append(f"  🌌 Skybox: {world.world_plan.skybox[:60]}...")
        if world.world_plan.ambient_music:
            messages.append(f"  🎵 Music Style: {world.world_plan.ambient_music}")
        
        messages.append(f"✅ Stage 2 Complete: Generated world with {len(world.objects)} objects")
        
        # Stage 3: Save world JSON
        messages.append("🔄 Stage 3: Saving world JSON...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"world_{timestamp}.json"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(world.model_dump(), f, indent=2, ensure_ascii=False)
        
        messages.append(f"✅ Stage 3 Complete: Saved to {filepath}")
        
        # Stage 4: Generate complete 3D world with Stability AI
        messages.append("🔄 Stage 4: Generating complete 3D world with Stability AI...")
        logger.info("Starting 3D world generation")
        models_dir = OUTPUT_DIR / f"world_{timestamp}_models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            stability_generator = StabilityAIGenerator()
            
            # Build world prompt
            world_prompt = f"A {world.world_plan.style} {world.world_plan.environment} scene. "
            world_prompt += f"{world.world_plan.mood} atmosphere. "
            
            # Add skybox if present
            if world.world_plan.skybox:
                world_prompt += f"Sky: {world.world_plan.skybox[:100]}. "
            
            # Add key objects (limit to avoid prompt being too long)
            key_objects = world.objects[:5]  # Use first 5 objects
            world_prompt += "Contains: "
            world_prompt += ", ".join([f"{obj.name}" for obj in key_objects])
            world_prompt += ". " + world.world_plan.description[:200]
            
            messages.append(f"  🌍 Creating unified 3D world ({world.world_plan.scale} scaleh
            
            messages.append(f"  🌍 Creating unified 3D world scene ({len(world.objects)} objects)...")
            logger.info(f"World prompt: {world_prompt[:200]}...")
            
            try:
                # Generate single 3D world model with optimized settings
                result = stability_generator.generate_from_text(
                    prompt=world_prompt,
                    texture_resolution=2048,  # High quality textures
                    foreground_ratio=0.85,  # Optimized for complete scenes
                    remesh="quad",  # Best quality mesh
                    timeout=300
                )- returns (glb_path, obj_path)
                glb_path, obj_path = stability_generator.save_model(
                    result["model_data"], 
                    str(models_dir / "complete_world.glb"),
                    export_obj=True
                )
                world_model_path = Path(glb_path
                world_model_path = models_dir / "complete_world.glb"
                stability_generator.save_model(result["model_data"], str(world_model_path))
                
                if world_model_path.exists():
                    file_size_mb = world_model_path.stat().st_size / (1024 * 1024)
                    generated_models.append({
                    })
                    messages.append(f"  ✅ Generated: complete_world.glb ({file_size_mb:.2f} MB)")
                    logger.info(f"Generated complete 3D world: {world_model_path}")
                    
                    # Add OBJ if exported
                    if obj_path and Path(obj_path).exists():
                        obj_size_mb = Path(obj_path).stat().st_size / (1024 * 1024)
                        generated_models.append({
                            "name": "complete_world_obj",
                            "path": str(obj_path),
                            "format": "obj",
                            "size_mb": round(obj_size_mb, 2)
                        })
                        messages.append(f"  ✅ Exported: complete_world.obj ({obj_size_mb:.2f} MB)
                        "description": "Complete 3D world scene with high-quality textures"
                    })
                    messages.append(f"  ✅ Generated: complete_world.glb ({file_size_mb:.2f} MB)")
                    logger.info(f"Generated complete 3D world: {world_model_path}")
                else:
                    messages.append("  ⚠️ Model file not saved")
                    
        if generated_models:
            messages.append(f"✅ Stage 4 Complete: Generated {len(generated_models)} model(s)")
        else:
            
                # Check for specific error types
                if "403" in error_msg or "Forbidden" in error_msg:
                    messages.append(f"  💳 Check API Key: Verify at https://platform.stability.ai/")
                elif "401" in error_msg or "Unauthorized" in error_msg:
                    messages.append(f"  🔑 Invalid API Key: Update STABILITY_API_KEY in .env")
                elif "400" in error_msg:
                    messages.append(f"  ⚠️ Invalid Request: {error_msg[:80]}")
                else:
                    messages.append(f"  ❌ Failed: {error_msg[:100]}")
            
            if generated_models:
                messages.append(f"✅ Stage 4 Complete: Generated complete 3D world")
            else:
                messages.append(f"⚠️ Stage 4 Complete: No models generated")
            
        except ValueError as stability_error:
            # Stability API key not configured
            logger.warning(f"Stability AI not configured: {stability_error}")
            messages.append(f"⚠️ Stage 4 Skipped: STABILITY_API_KEY not configured in .env")
        
        messages.append("🎉 World generation complete!")
        logger.info(f"World saved to {filepath} with {len(generated_models)} models")
        
        return GenerateWorldResponse(
            world=world,
            saved_to=str(filepath),
            models=generated_models,
            music_path=music_path,
            messages=messages,
            status="success"
        )
        
    except ValueError as exc:
        logger.warning("Bad request: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Upstream error: %s", exc)
        raise HTTPException(status_code=502, detail="Upstream AI error") from exc
    except Exception as exc:  # pragma: no cover - unexpected
        logger.exception("Unexpected server error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
