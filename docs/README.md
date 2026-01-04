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
- Tripo3D API key ([Get one here](https://platform.tripo3d.ai/))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download this project**
   ```bash
   cd tsuana
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env and add your API keys
   # OPENAI_API_KEY=sk-...
   # TRIPO_API_KEY=tsk_...
   ```

4. **Run the generator**
   ```bash
   python main.py
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
| `OPENAI_API_KEY` | Yes | OpenAI API key for scene planning |
| `TRIPO_API_KEY` | Yes | Tripo3D API key for 3D generation |

### Customization

#### Modify Generation Settings
Edit `threed_generator.py`:
```python
result = generator.generate_from_text(
    prompt=prompt,
    model_version="v2.0-20240919",  # Change model version
    style="realistic",               # "realistic", "cartoon", "low-poly"
    timeout=300                      # Increase for complex objects
)
```

#### Adjust Scene Layout
Edit `scene_composer.py`:
```python
composer.auto_arrange_objects(layout="circle")  # or "grid", "random"
composer.setup_default_lighting("warm")         # or "bright", "dark", "cool"
```

## 📊 API Usage & Costs

### Tripo3D API
- **Text-to-3D**: ~$0.05-0.20 per object (varies by plan)
- **Generation Time**: 20-60 seconds per object
- **Free Tier**: Check [Tripo3D pricing](https://www.tripo3d.ai/pricing)

### OpenAI API
- **GPT-4**: ~$0.01-0.03 per scene plan
- **GPT-3.5-Turbo**: ~$0.001 per scene plan (edit `tsuana.py`)

**Estimated Cost per Scene**: $0.50 - $2.00 (5-10 objects)

## 🔍 Troubleshooting

### Common Issues

#### "TRIPO_API_KEY not found"
- Ensure `.env` file exists in project root
- Check API key is correctly formatted
- Verify no extra spaces or quotes

#### "Task timeout after 300s"
- Increase timeout in `threed_generator.py`
- Check Tripo3D API status
- Try simpler object descriptions

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

### Tripo3DGenerator

```python
from threed_generator import Tripo3DGenerator

generator = Tripo3DGenerator(api_key="your_key")

result = generator.generate_from_text(
    prompt="a medieval castle tower",
    model_version="default",
    style="realistic",
    max_retries=3,
    poll_interval=5,
    timeout=300
)

# Returns:
{
    "task_id": "abc123",
    "model_urls": {
        "glb": "https://...",
        "fbx": "https://...",
        "obj": "https://..."
    },
    "thumbnail": "https://...",
    "metadata": {...}
}
```

### SceneComposer

```python
from scene_composer import SceneComposer

composer = SceneComposer()

composer.add_object(
    name="tree",
    model_path="tree.glb",
    position=(3.0, 0.0, 0.0),
    rotation=(0.0, 45.0, 0.0),
    scale=(1.5, 1.5, 1.5)
)

composer.setup_default_lighting("warm")
composer.set_camera((0, 1.6, 8))

composer.export_scene_data("scene.json")
composer.generate_aframe_html("viewer.html")
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional 3D generation backends (Meshy, Rodin, local models)
- Advanced scene composition algorithms
- Real-time preview
- Texture customization
- Animation support

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Tripo3D**: Production-ready text-to-3D API
- **OpenAI**: GPT-4 for intelligent scene planning
- **A-Frame**: WebVR framework for instant previews

## 📞 Support

- **Issues**: Open a GitHub issue
- **Email**: support@example.com
- **Discord**: [Join our community](https://discord.gg/example)

---

**Built with ❤️ by the Tsuana Team**

*Transform imagination into immersive 3D worlds*
