"""Legacy FastAPI app (deprecated)."""
raise SystemExit("Use app.api:app for the open-source pipeline.")

import logging
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List, Dict

from app.prompt_service import generate_prompt
from app.world_service import generate_world
from app.schemas import WorldResponse

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
    models: List[Dict[str, str]]
    messages: list[str]
    status: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "message": "✅ API is running"}


@app.post("/api/v1/world", response_model=GenerateWorldResponse)
def create_world(body: GenerateWorldRequest):
    """Generate a complete 3D world from text description."""
    messages = []
    generated_models = []
    
    try:
        # Stage 1: Prompt refinement
        messages.append("🔄 Stage 1: Refining your description...")
        logger.info("Starting prompt refinement")
        refined_prompt = generate_prompt(body.description)
        messages.append(f"✅ Stage 1 Complete: Generated refined prompt ({len(refined_prompt)} chars)")
        
        # Stage 2: World generation
        messages.append("🔄 Stage 2: Generating world JSON with AI...")
        logger.info("Starting world generation")
        world = generate_world(refined_prompt)
        messages.append(f"✅ Stage 2 Complete: Generated {world.world_plan.scale} world with {len(world.objects)} objects")
        
        # Stage 3: Save world JSON
        messages.append("🔄 Stage 3: Saving world JSON...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"world_{timestamp}.json"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(world.model_dump(), f, indent=2, ensure_ascii=False)
        
        messages.append(f"✅ Stage 3 Complete: Saved to {filepath}")
        
        # Stage 4: Generate 3D world with Stability AI
        messages.append("🔄 Stage 4: Generating 3D world with Stability AI...")
        logger.info("Starting 3D world generation")
        
        models_dir = OUTPUT_DIR / f"world_{timestamp}_models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            stability_generator = StabilityAIGenerator()
            
            # Build world prompt
            world_prompt = f"A {world.world_plan.style} {world.world_plan.environment} scene. "
            world_prompt += f"{world.world_plan.mood} atmosphere. "
            
            if world.world_plan.skybox:
                world_prompt += f"Sky: {world.world_plan.skybox[:100]}. "
            
            key_objects = world.objects[:5]
            world_prompt += "Contains: " + ", ".join([f"{obj.name}" for obj in key_objects])
            world_prompt += ". " + world.world_plan.description[:200]
            
            messages.append(f"  🌍 Creating 3D world ({world.world_plan.scale} scale)...")
            logger.info(f"World prompt: {world_prompt[:200]}...")
            
            # Generate 3D model
            result = stability_generator.generate_from_text(
                prompt=world_prompt,
                texture_resolution=2048,
                foreground_ratio=0.85,
                remesh="quad",
                timeout=300
            )
            
            # Save model - returns (glb_path, obj_path)
            glb_path, obj_path = stability_generator.save_model(
                result["model_data"], 
                str(models_dir / "complete_world.glb"),
                export_obj=True
            )
            
            world_model_path = Path(glb_path)
            
            if world_model_path.exists():
                file_size_mb = world_model_path.stat().st_size / (1024 * 1024)
                generated_models.append({
                    "name": "complete_world",
                    "path": str(world_model_path),
                    "format": "glb",
                    "size_mb": round(file_size_mb, 2)
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
                    messages.append(f"  ✅ Exported: complete_world.obj ({obj_size_mb:.2f} MB)")
            else:
                messages.append("  ⚠️ Model file not saved")
                    
        except Exception as model_error:
            error_msg = str(model_error)
            logger.error(f"Failed to generate 3D world: {error_msg}")
            
            if "403" in error_msg or "Forbidden" in error_msg:
                messages.append(f"  💳 Check API Key: Verify at https://platform.stability.ai/")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                messages.append(f"  🔑 Invalid API Key: Update STABILITY_API_KEY in .env")
            elif "400" in error_msg:
                messages.append(f"  ⚠️ Invalid Request: {error_msg[:80]}")
            else:
                messages.append(f"  ❌ Failed: {error_msg[:100]}")
        
        if generated_models:
            messages.append(f"✅ Stage 4 Complete: Generated {len(generated_models)} model(s)")
        else:
            messages.append(f"⚠️ Stage 4 Complete: No models generated")
        
        messages.append("🎉 World generation complete!")
        logger.info(f"World saved to {filepath} with {len(generated_models)} models")
        
        return GenerateWorldResponse(
            world=world,
            saved_to=str(filepath),
            models=generated_models,
            messages=messages,
            status="success"
        )
        
    except ValueError as exc:
        logger.warning("Bad request: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Upstream error: %s", exc)
        raise HTTPException(status_code=502, detail="Upstream AI error") from exc
    except Exception as exc:
        logger.exception("Unexpected server error")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
