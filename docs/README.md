# TSUANA - Production-Ready 3D VR World Generator

![Status](https://img.shields.io/badge/status-production--ready-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

Transform natural language descriptions into complete, production-ready 3D virtual reality worlds.

## 🌟 Features

### Core Capabilities
- **Text-to-3D Generation**: Convert natural language into complete 3D scenes
- **AI Scene Planning**: Intelligent decomposition of worlds into constituent objects
- **Multi-Object Composition**: Automatic scene layout and object positioning
- **Production-Ready Output**: Export to industry-standard formats (GLB, GLTF)
- **VR-Ready**: WebVR viewer included for immediate testing
- **Unity Compatible**: Auto-generated import scripts for Unity engine

### Technical Highlights
- ✅ Production-grade error handling and retry logic
- ✅ Comprehensive logging and monitoring
- ✅ Async-ready architecture
- ✅ Modular, maintainable codebase
- ✅ Type hints and documentation
- ✅ Real 3D generation (no mock data)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Local LLM model for enhanced generation

### Installation

1. **Clone or download this project**
   ```bash
   cd tsuana
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env if you want to use custom LLM settings
   # LOCAL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   # LLM_PROVIDER=transformers
   ```

4. **Start the API server**
   ```bash
   uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Generate a world**
   ```bash
   # In another terminal
   python examples/generate_world_example.py
   ```

### First Generation

```
TSUANA: 3D VR WORLD GENERATOR

Describe the 3D world you want to create.

💬 You: I want a peaceful zen garden

🤖 Tsuana: What mood do you want? (calm, energetic, mysterious, etc.)

💬 You: calm and serene

🤖 Tsuana: What visual style? (realistic, cartoon, low-poly, etc.)

💬 You: realistic with Japanese aesthetics

🤖 Tsuana: How large should the world be? (small room, medium area, large landscape)

💬 You: medium area

✅ World plan generated!

📋 World Plan Summary:
   Environment: zen garden with rocks and sand
   Mood: calm and serene
   Style: realistic with Japanese aesthetics
   Scale: medium area
   Objects to generate: 7

🚀 Start 3D world generation? (yes/no): yes

📦 Generating 7 3D objects...

[1/7] Generating: stone_lantern
    Description: traditional Japanese stone lantern (ishidōrō) with carved details
    ✅ Generated successfully: stone_lantern.glb

[2/7] Generating: zen_rock
    Description: smooth river rock for zen garden arrangement
    ✅ Generated successfully: zen_rock.glb

...

🎉 3D WORLD GENERATION COMPLETE!

✅ Successfully generated: 7/7 objects

📁 Output directory: output/

🌐 To view in VR:
   1. Open output/vr_viewer.html in a WebVR-compatible browser
   2. Use WASD to move, mouse to look around
   3. Click 'Enter VR' for immersive mode
```

## 📁 Project Structure

```
tsuana/
├── app/                 # FastAPI + LLM orchestration
│   ├── api.py           # REST endpoints
│   ├── ai_client.py     # Local LLM wrapper (Transformers/Ollama)
│   ├── prompt_service.py# Stage 1: Design spec
│   ├── world_service.py # Stage 2: Schema generation
│   └── schemas.py       # Pydantic models
├── core/                # Procedural generation
│   ├── world_generator.py  # Orchestrator
│   ├── procedural_engine.py# Terrain/roads/structures/vegetation
│   ├── mesh_exporter.py    # OBJ/MTL/textures export
│   └── music_generator.py  # Procedural ambient audio
├── requirements.txt     # Python dependencies
├── .env.template        # Environment config template
├── .env                 # Local model config (gitignored)
├── .gitignore
└── README.md

exports/                 # Generated content (created at runtime)
└── world_YYYYMMDD_HHMMSS/world/
    ├── geometry/world.obj
    ├── world.mtl
    ├── textures/*.png
    ├── world.json
    ├── unity_import.cs
    └── preview.png
```

## 🔧 Architecture

### Pipeline Overview

```
User Input → Design Spec → Procedural Schema → Mesh Synthesis → Export
    ↓             ↓                 ↓                 ↓              ↓
  Natural    Structured        Heightmap +       Terrain + Roads   OBJ/MTL +
  Language    World Spec        Rules JSON        Vegetation       JSON/Preview
```

### Key Components

#### 1. **Design Spec Generator** (`app/prompt_service.py`)
- Converts raw text into `WorldDesignSpec` (biome, terrain, landmarks, mood, scale)
- Uses local open-source LLM (Transformers/Ollama)

#### 2. **World Schema Generator** (`app/world_service.py`)
- Produces strict `WorldSchema` JSON (noise params, splines, vegetation, lighting)
- Enforces schema validation (`extra="forbid"`)

#### 3. **Procedural Engine** (`core/procedural_engine.py`)
- Builds Perlin/Simplex heightmaps
- Generates spline-based roads/rivers, instanced vegetation, parametric structures
- Deterministic seeds for reproducibility

#### 4. **Exporter** (`core/mesh_exporter.py`)
- Combines meshes into OBJ/MTL with baked textures
- Writes `world.json` semantic layout and `preview.png`
- Generates Unity import helper script

## 🎮 Output Formats

### 1. GLB/GLTF Models
Industry-standard 3D model format compatible with:
- Unity
- Unreal Engine
- Blender
- Three.js
- Babylon.js
- WebXR/WebVR

### 2. WebVR Viewer (HTML)
Instant VR preview using A-Frame:
- Works in any modern browser
- VR headset support (optional)
- WASD + mouse controls
- Mobile-friendly

### 3. Unity Import Script
Auto-generated C# script:
```csharp
// Drop this in your Unity project
// Automatically positions all objects
GameObject obj1 = new GameObject("tree");
obj1.transform.position = new Vector3(3f, 0f, 0f);
// ...load GLB models via UnityGLTF or similar
```

### 4. Scene Data (JSON)
Complete scene configuration:
```json
{
  "objects": [...],
  "lights": [...],
  "camera": {...},
  "environment": {...}
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LOCAL_LLM_MODEL` | No | Local LLM model (default: mistralai/Mistral-7B-Instruct-v0.2) |
| `LLM_PROVIDER` | No | LLM provider (default: transformers, options: transformers/ollama) |
| `LLM_TEMPERATURE` | No | Temperature for LLM (default: 0.25) |
| `LLM_MAX_NEW_TOKENS` | No | Max tokens for LLM (default: 768) |

### Customization

#### Modify Generation Settings
Edit `app/world_service.py` to adjust world generation parameters:
```python
# Adjust object counts
object_rules: List[ObjectPlacementRule] = [
    ObjectPlacementRule(
        kind="tower",
        count=rng.randint(15, 35),  # Change counts
        scale_range=(0.8, 2.2),
        height_range=(30.0, 120.0),
        ...
    ),
    ...
]
```

#### Adjust Terrain Parameters
Edit `core/procedural_engine.py`:
```python
def __init__(self, grid_resolution: int = 220):  # Change resolution
    self.grid_resolution = grid_resolution
```

## 📊 Generation Performance

### Procedural Generation
- **World Creation**: 1-2 minutes for typical worlds
- **Objects Generated**: 60+ structures per world
- **Vegetation**: 4000+ instances
- **Output Size**: 50-100 MB .obj files
- **Cost**: Free - fully open source procedural generation
- **Local LLM**: Optional, runs on your hardware

## 🔍 Troubleshooting

### Common Issues

#### Server won't start
- Ensure dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)
- Verify port 8000 is not in use

#### Generation is slow
- The first run may be slower if downloading LLM models
- Subsequent runs use the fallback procedural generator
- Adjust `grid_resolution` in `procedural_engine.py` for faster generation

#### Out of memory
- Reduce `grid_resolution` in `core/procedural_engine.py`
- Decrease `MAX_VEGETATION_INSTANCES` 
- Use smaller `scale_km` values in requests

#### "Failed to generate X objects"
- Check `generation_report.json` for details
- Simplify object descriptions
- Ensure stable internet connection

### Debug Mode
Enable detailed logging:
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Production Deployment

### Performance Optimization
1. **Parallel Generation**: Modify `main.py` to generate objects concurrently
2. **Caching**: Store previously generated models
3. **CDN**: Host GLB files on CDN for faster loading

### Scaling Considerations
- Implement request queuing for high-volume usage
- Add database for tracking generations
- Consider self-hosting 3D generation (Shap-E, Point-E)
- Cache common objects (trees, rocks, etc.)

### Monitoring
```python
# Add to production environment
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")

# Track generation metrics
from prometheus_client import Counter
generations_counter = Counter('world_generations_total', 'Total worlds generated')
```

## 📖 API Reference

### REST API

**Generate World**
```bash
POST /api/v1/world
Content-Type: application/json

{
  "description": "A magical forest clearing with glowing mushrooms",
  "seed": 42  # Optional: for deterministic generation
}
```

**Response**
```json
{
  "world_path": "exports/world_20260104_175925/world",
  "preview_image": "exports/world_20260104_175925/world/preview.png",
  "unity_import": "exports/world_20260104_175925/world/unity_import.cs",
  "metadata": {
    "design": {
      "biome": "forest",
      "terrain_type": "rolling hills",
      "scale_km": 25.0,
      "mood": "mysterious",
      "time_of_day": "twilight",
      ...
    },
    "schema": {...},
    "layout": {
      "terrain_bounds_m": [25000, 25000],
      "objects": [...],
      "vegetation_count": 4000
    }
  }
}
```

### Python SDK

```python
from app.schemas import GenerateWorldRequest
from core.world_generator import world_generator

request = GenerateWorldRequest(
    description="A cozy bedroom with a bed and nightstand",
    seed=42  # Optional
)

response = world_generator.generate(request)
print(f"World saved to: {response.world_path}")
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional procedural structure types
- Advanced terrain generation algorithms
- Real-time preview capabilities
- Enhanced vegetation systems
- Animation support

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Trimesh**: For 3D mesh processing
- **NumPy & SciPy**: For mathematical operations
- **FastAPI**: For the REST API framework
- **Transformers**: For local LLM support

## 📞 Support

- **Issues**: Open a GitHub issue
- **Documentation**: Check docs/ directory for guides

---

**Built with ❤️ by the Tsuana Team**

*Transform imagination into immersive 3D worlds*
