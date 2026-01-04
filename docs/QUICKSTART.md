# 🚀 Quick Start Guide - Tsuana 3D World Generator

## Step 1: Get Your API Keys

### Tripo3D API Key (Required)
1. Visit https://platform.tripo3d.ai/
2. Sign up for a free account
3. Go to API settings: https://platform.tripo3d.ai/api-keys
4. Create a new API key
5. Copy the key (starts with `tsk-`)

### OpenAI API Key (Required)
1. Visit https://platform.openai.com/
2. Sign up or log in
3. Go to API keys: https://platform.openai.com/api-keys
4. Create a new API key
5. Copy the key (starts with `sk-`)

## Step 2: Setup

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Configure API keys
# Edit the .env file and replace the placeholder values:
OPENAI_API_KEY=sk-your-actual-key-here
TRIPO_API_KEY=tsk-your-actual-key-here

# 3. Verify setup
python setup_check.py
```

## Step 3: Generate Your First World

```bash
python main.py
```

### Example Session

```
💬 You: A magical forest clearing with glowing mushrooms

🤖 Tsuana: What mood do you want?
💬 You: mysterious and enchanting

🤖 Tsuana: What visual style?
💬 You: fantasy realistic

🤖 Tsuana: How large should the world be?
💬 You: small intimate area

✅ World plan generated!

Objects to generate: 6
- forest_ground
- large_tree
- glowing_mushrooms
- moss_covered_rock
- fireflies_swarm
- ancient_stump

🚀 Start generation? yes

[Generates 3D models...]

🎉 Complete! Open output/vr_viewer.html
```

## Step 4: View Your World

### In Browser (WebVR)
1. Open `output/vr_viewer.html` in Chrome, Firefox, or Edge
2. Use WASD to move, mouse to look around
3. Press F to enter fullscreen
4. Click "Enter VR" if you have a VR headset

### In Unity
1. Create new Unity project
2. Install UnityGLTF or GLTFUtility from Package Manager
3. Drag `output/ImportScene.cs` into your project
4. Import the `.glb` files from `output/`
5. Attach script to an empty GameObject
6. Press Play

### In Blender
1. File → Import → glTF 2.0 (.glb/.gltf)
2. Select files from `output/`
3. All models will be imported with correct positions

## 💡 Tips

### For Better Results
- Be specific in descriptions (e.g., "weathered stone cottage" vs "house")
- Start with simple scenes (3-5 objects)
- Use consistent art styles (all realistic or all cartoon)

### Cost Optimization
- Each object costs ~$0.05-0.20 to generate
- Reuse common objects (save generated models)
- Start with smaller scenes to test

### Troubleshooting
- Check `generation_report.json` for details
- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
- Ensure your local LLM checkpoint is configured in `.env`
- Use an offline-capable model to avoid network dependency

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Explore `core/world_generator.py` to customize the pipeline
- Tune `app/world_service.py` for schema defaults and seeds
- Adjust `core/procedural_engine.py` for terrain/road/vegetation density

## ❓ Need Help?

- Check the [README.md](README.md)
- Review error messages in console
- Verify API quotas haven't been exceeded
- Ensure Python 3.8+ is installed

---

**Happy World Building! 🌍✨**
