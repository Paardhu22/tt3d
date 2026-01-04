# 🗺️ Tsuana - Open 3D World Generator (Summary)

## Pipeline Overview
```
Text → LLM Design Spec → Procedural Schema → Procedural Meshes → OBJ/MTL + JSON
```

### Stage 1: Prompt Refinement
- File: `app/prompt_service.py`
- Produces `WorldDesignSpec` with biome, terrain type, scale (km), structures, mood, time of day, landmarks, sky/weather.
- Uses local open-source LLM (Transformers or Ollama).

### Stage 2: World Schema
- File: `app/world_service.py`
- Generates strict `WorldSchema` JSON:
  - Heightmap noise params
  - Terrain features
  - Roads/rivers splines
  - Object placement rules
  - Vegetation density/species
  - Lighting + sky config

### Stage 3: Procedural Builder
- File: `core/procedural_engine.py`
- Builds Perlin/Simplex terrain, splines, parametric structures, instanced vegetation, sky dome.
- Deterministic seeds for reproducibility and VR-ready scale (meters, Y-up).

### Export
- File: `core/mesh_exporter.py`
- Outputs:
  - `/world/geometry/world.obj` + `world.mtl`
  - `/world/textures/*.png`
  - `/world/world.json` (semantic layout)
  - `/world/preview.png`
  - `/world/unity_import.cs`

## Key Guarantees
- ✅ Fully offline after model download (no paid APIs)
- ✅ Deterministic seeds
- ✅ Large, connected terrain (no single-object outputs)
- ✅ VR-ready scale and Unity-friendly orientation

## Run
```
pip install -r requirements.txt
cp .env.template .env  # set LOCAL_LLM_MODEL / LLM_PROVIDER
uvicorn app.api:app --reload

curl -X POST http://localhost:8000/api/v1/world \
  -H "Content-Type: application/json" \
  -d '{"description": "Epic cyberpunk floating city with neon rivers and rain", "seed": 1234}'
```
