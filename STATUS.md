# 🎯 Project Status - Tsuana Open Pipeline

## Current Snapshot
- ✅ Open-source only pipeline (no paid APIs)
- ✅ Three-stage flow: design spec → procedural schema → mesh synthesis
- ✅ Exports VR-ready OBJ/MTL with textures, semantic `world.json`, preview, Unity importer
- ✅ Deterministic seeds supported

## Key Components
- `app/ai_client.py` – local LLM client (Transformers/Ollama)
- `app/prompt_service.py` – Stage 1 prompt refinement to `WorldDesignSpec`
- `app/world_service.py` – Stage 2 schema generation (`WorldSchema`)
- `core/procedural_engine.py` – Stage 3 procedural terrain/structures/vegetation/roads/rivers
- `core/mesh_exporter.py` – OBJ/MTL/textures + metadata export
- `core/world_generator.py` – orchestrates end-to-end generation

## Output Layout
```
exports/world_YYYYMMDD_HHMMSS/world/
  geometry/world.obj
  world.mtl
  textures/*.png
  world.json
  preview.png
  unity_import.cs
```

## How to Run
```
pip install -r requirements.txt
cp .env.template .env  # set LOCAL_LLM_MODEL, LLM_PROVIDER
uvicorn app.api:app --reload
```

`POST /api/v1/world` with `{"description": "...", "seed": 123}` to generate a full world.
