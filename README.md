# Tsuana - 3D World Generator

**Production-ready Text/Voice → 3D World Generator with FastAPI backend**

## Project Structure

```
tsuana/
├── app/                    # FastAPI application layer
│   ├── api.py             # REST API endpoints
│   ├── ai_client.py       # Local LLM client (Transformers/Ollama)
│   ├── prompt_service.py  # Stage 1: Prompt refinement → design spec
│   ├── world_service.py   # Stage 2: Procedural schema generation
│   └── schemas.py         # Pydantic validation models
│
├── core/                   # 3D generation services
│   ├── world_generator.py  # Orchestrator
│   ├── procedural_engine.py# Procedural mesh synthesis
│   ├── mesh_exporter.py    # OBJ/MTL/JSON export
│   └── scene_composer.py   # Scene assembly helpers
│
├── domain/                 # Domain models
│   └── user_profile.py    # User preference models
│
├── scripts/               # Utility scripts
│   ├── setup_check.py    # Installation verification
│   ├── install.ps1       # Windows installer
│   └── install.sh        # Unix installer
│
├── docs/                  # Documentation
│   ├── README.md         # Main documentation
│   ├── QUICKSTART.md     # Quick start guide
│   └── PROJECT_SUMMARY.md # Project overview
│
├── examples/              # Usage examples
│   └── examples.py       # API usage demos
│
├── tests/                 # Test suite (future)
│
├── legacy/                # Old CLI implementation
│   ├── main.py           # Original CLI interface
│   ├── tsuana.py         # Legacy AI engine
│   └── prompts.py        # Old prompt templates
│
├── .env                   # Environment variables (gitignored)
├── .env.template         # Env template
├── requirements.txt      # Python dependencies
└── .gitignore           # Git ignore rules
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.template .env
# Edit .env and set a local model checkpoint (Transformers or Ollama)
# Example:
# LOCAL_LLM_MODEL=TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# LLM_PROVIDER=transformers
```

### 3. Run API Server
```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/world \
  -H "Content-Type: application/json" \
  -d '{"description": "a peaceful zen garden with stone lanterns"}'
```

## Architecture

### Three-Stage AI/Procedural Pipeline

**Stage 1: Prompt Refinement** (`app/prompt_service.py`)
- Input: Raw user description
- Output: Structured `WorldDesignSpec` (biome, terrain, mood, scale, landmarks)

**Stage 2: World Schema Generation** (`app/world_service.py`)
- Input: World design spec
- Output: Strict `WorldSchema` JSON (heightmap noise, splines, vegetation, lighting)

**Stage 3: Procedural Builder** (`core/procedural_engine.py`)
- Input: World schema
- Output: VR-ready meshes (terrain, roads, rivers, vegetation, structures) with deterministic seed

### API Endpoints

- `GET /health` - Health check
- `POST /api/v1/world` - Generate a complete OBJ world from description

### Outputs
- `/world/geometry/world.obj` + `world.mtl`
- `/world/textures/*.png`
- `/world/world.json` semantic layout
- `/world/preview.png` heightmap preview
- `/world/unity_import.cs` Unity importer

## Development

### Project Principles
- ✅ No mock logic or fake data
- ✅ Strict schema validation
- ✅ Clean architecture (separation of concerns)
- ✅ Deterministic AI responses
- ✅ Production-ready error handling
- ✅ Environment-based configuration

### Running in Development
```bash
# With auto-reload
uvicorn app.api:app --reload

# With custom port
uvicorn app.api:app --port 3000

# Production mode
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing
```bash
# Verify installation
python scripts/setup_check.py

# Run examples
python examples/examples.py
```

## Unity Integration

Unity consumes only the validated JSON from `/api/v1/world`:
```csharp
[System.Serializable]
public class WorldResponse {
    public WorldPlan world_plan;
    public WorldObject[] objects;
    public Lighting lighting;
    public Camera camera;
}
```

No raw AI text reaches Unity - all responses are schema-validated.

## Documentation

- [docs/README.md](docs/README.md) - Full documentation
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Quick setup guide
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) - Project overview

## License

MIT License
