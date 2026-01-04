# 🚀 Quick Start Guide - Tsuana 3D World Generator

## Step 1: Setup

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Configure Local LLM (Optional)
# Copy the template and edit if needed
cp .env.template .env

# The default configuration uses open-source models:
# LOCAL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
# LLM_PROVIDER=transformers

# 3. Verify setup
python scripts/setup_check.py
```

## Step 2: Start the API Server

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

## Step 3: Generate Your First World

### Using Python Example

```bash
python examples/generate_world_example.py
```

### Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/world \
  -H "Content-Type: application/json" \
  -d '{"description": "A magical forest clearing with glowing mushrooms"}'
```

### Example Output

```
======================================================================
🌍 Generating 3D World: A magical forest clearing with glowing mushrooms
======================================================================

📤 Sending request to API...

======================================================================
✅ GENERATION COMPLETE!
======================================================================

📊 World Summary:
  Biome: forest
  Terrain: rolling hills
  Mood: mysterious
  Time of Day: twilight
  Scale: 25.0 km
  Objects: 65
  Vegetation: 4000

💾 Files Saved:
  World Directory: exports/world_20260104_175925/world
  Preview Image: exports/world_20260104_175925/world/preview.png
  Unity Import Script: exports/world_20260104_175925/world/unity_import.cs

⏱️  Total Time: 104.77 seconds
```

## Step 4: View Your World

### Generated Files

The world is exported to `exports/world_YYYYMMDD_HHMMSS/world/`:
- `world.obj` - 3D model mesh (60+ MB)
- `world.mtl` - Material definitions
- `textures/` - Texture images
- `world.json` - Complete metadata
- `preview.png` - Heightmap preview
- `unity_import.cs` - Unity importer script

### In Blender
1. File → Import → Wavefront (.obj)
2. Select `world.obj` from exports directory
3. All meshes, materials and textures will be imported

### In Unity
1. Copy the entire `world/` directory into Unity's Assets folder
2. Unity will automatically import the .obj file
3. Or use the provided `unity_import.cs` script

### Preview the Heightmap
Open `preview.png` to see the terrain elevation map

## 💡 Tips

### For Better Results
- Be specific in descriptions (e.g., "cozy bedroom with a bed and nightstand")
- The system generates 60+ objects and 4000+ vegetation instances
- Each world includes terrain, roads, rivers, structures, and vegetation
- All generation uses procedural techniques - fully open source

### Performance
- Higher scale_km values generate larger worlds
- Generation time: 1-2 minutes for typical worlds
- Output size: 50-100 MB for detailed worlds

### Customization
- Edit `app/world_service.py` to adjust object counts and types
- Modify `core/procedural_engine.py` to change structure designs
- Tune terrain parameters in `app/schemas.py`

## 📚 Next Steps

- Read [README.md](../README.md) for full documentation
- Explore `core/world_generator.py` to understand the pipeline
- Customize `app/world_service.py` for different defaults
- Adjust `core/procedural_engine.py` for structure variety

## ❓ Need Help?

- Check the [README.md](../README.md)
- Review error messages in console
- Ensure Python 3.8+ is installed
- Verify dependencies are installed: `pip install -r requirements.txt`

---

**Happy World Building! 🌍✨**
