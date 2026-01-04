"""
Complete example: Generate a 3D world with .obj files

This demonstrates the full pipeline from text description to 3D model files.
"""
import requests
import json
import time
from pathlib import Path

# API Configuration
API_BASE = "http://127.0.0.1:8000"


def generate_world_with_models(description: str):
    """
    Generate a complete 3D world with .obj model files.
    
    Args:
        description: Text description of the world you want to create
        
    Returns:
        dict: Complete response with world data and model paths
    """
    print("\n" + "=" * 70)
    print(f"🌍 Generating 3D World: {description}")
    print("=" * 70)
    
    # Send request
    payload = {"description": description}
    
    print("\n📤 Sending request to API...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/world",
            json=payload,
            timeout=300  # 5 minutes for 3D generation
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Print progress messages
            print("\n📋 Progress Messages:")
            print("-" * 70)
            for msg in result.get("messages", []):
                print(msg)
            
            # Print summary
            print("\n" + "=" * 70)
            print("✅ GENERATION COMPLETE!")
            print("=" * 70)
            
            world = result.get("world", {})
            world_plan = world.get("world_plan", {})
            
            print(f"\n📊 World Summary:")
            print(f"  Environment: {world_plan.get('environment')}")
            print(f"  Mood: {world_plan.get('mood')}")
            print(f"  Style: {world_plan.get('style')}")
            print(f"  Objects: {len(world.get('objects', []))}")
            
            print(f"\n💾 Files Saved:")
            print(f"  JSON: {result.get('saved_to')}")
            
            models = result.get("models", [])
            if models:
                print(f"  3D Models: {len(models)} .obj files")
                for model in models:
                    print(f"    ✓ {model['name']}: {model['path']}")
            else:
                print(f"  3D Models: None (Tripo3D not configured)")
            
            print(f"\n⏱️  Total Time: {elapsed:.2f} seconds")
            
            return result
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out. Try a simpler description.")
        return None
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API. Make sure the server is running:")
        print("   uvicorn app.api:app --host 127.0.0.1 --port 8000")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def list_generated_worlds():
    """List all generated worlds and their models."""
    output_dir = Path("output/generated_worlds")
    
    if not output_dir.exists():
        print("No generated worlds found.")
        return
    
    print("\n" + "=" * 70)
    print("📁 Generated Worlds")
    print("=" * 70)
    
    json_files = sorted(output_dir.glob("world_*.json"))
    
    for json_file in json_files:
        print(f"\n📄 {json_file.name}")
        
        # Check for corresponding models directory
        model_dir_name = json_file.stem + "_models"
        model_dir = output_dir / model_dir_name
        
        if model_dir.exists():
            obj_files = list(model_dir.glob("*.obj"))
            print(f"   🎨 3D Models: {len(obj_files)} .obj files")
            for obj_file in obj_files:
                size_kb = obj_file.stat().st_size / 1024
                print(f"      - {obj_file.name} ({size_kb:.1f} KB)")
        else:
            print(f"   🎨 3D Models: None")


if __name__ == "__main__":
    # Example 1: Simple object
    print("\n🧪 Test 1: Simple Scene")
    generate_world_with_models("A cozy bedroom with a bed and nightstand")
    
    # Example 2: More complex scene
    # print("\n🧪 Test 2: Complex Scene")
    # generate_world_with_models("A magical forest with glowing mushrooms and a small cottage")
    
    # List all generated worlds
    print("\n")
    list_generated_worlds()
    
    print("\n" + "=" * 70)
    print("✨ Done! Check output/generated_worlds/ for files")
    print("=" * 70)
