# Tsuana - 3D World Generator

**Production-ready Text/Voice → 3D World Generator with FastAPI backend**

## Project Structure

```
tsuana/
├── app/                    # FastAPI application layer
│   ├── api.py             # REST API endpoints
│   ├── ai_client.py       # OpenAI client wrapper
│   ├── prompt_service.py  # Stage 1: Prompt refinement
│   ├── world_service.py   # Stage 2: JSON world generation
│   └── schemas.py         # Pydantic validation models
│
├── core/                   # 3D generation services
│   ├── threed_generator.py # Tripo3D API client
│   └── scene_composer.py   # Scene assembly & export
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
# Edit .env and add:
# OPENAI_API_KEY=sk-...
# TRIPO_API_KEY=tsk-... (optional for 3D generation)
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

### Two-Stage AI Pipeline

**Stage 1: Prompt Generator** (`app/prompt_service.py`)
- Input: Raw user description (text/voice)
- Output: Refined world-building prompt (plain text)
- Deterministic (temperature=0)

**Stage 2: World Generator** (`app/world_service.py`)
- Input: Refined prompt
- Output: Strict JSON validated against Pydantic schema
- Enforced `response_format=json_object`
- No markdown, no extras

### API Endpoints

- `GET /health` - Health check
- `POST /api/v1/world` - Generate world JSON from description

### Schema Validation

All responses validated via Pydantic with `extra="forbid"`:
- `WorldResponse` - Complete world configuration
- `WorldPlan` - Environment, mood, style, scale
- `WorldObject[]` - 3-12 objects with positions
- `Lighting` - Mood-based lighting config
- `Camera` - Position, target, FOV

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
