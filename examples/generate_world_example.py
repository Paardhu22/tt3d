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
            
            # Extract metadata from response
            metadata = result.get("metadata", {})
            design = metadata.get("design", {})
            schema = metadata.get("schema", {})
            layout = metadata.get("layout", {})
            
            # Print summary
            print("\n" + "=" * 70)
            print("✅ GENERATION COMPLETE!")
            print("=" * 70)
            
            print(f"\n📊 World Summary:")
            print(f"  Biome: {design.get('biome', 'N/A')}")
            print(f"  Terrain: {design.get('terrain_type', 'N/A')}")
            print(f"  Mood: {design.get('mood', 'N/A')}")
            print(f"  Time of Day: {design.get('time_of_day', 'N/A')}")
            print(f"  Scale: {design.get('scale_km', 0):.1f} km")
            print(f"  Objects: {len(layout.get('objects', []))}")
            print(f"  Vegetation: {layout.get('vegetation_count', 0)}")
            
            print(f"\n💾 Files Saved:")
            print(f"  World Directory: {result.get('world_path', 'N/A')}")
            print(f"  Preview Image: {result.get('preview_image', 'N/A')}")
            print(f"  Unity Import Script: {result.get('unity_import', 'N/A')}")
            
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
    exports_dir = Path("exports")
    
    if not exports_dir.exists():
        print("\nNo generated worlds found in exports directory.")
        return
    
    print("\n" + "=" * 70)
    print("📁 Generated Worlds")
    print("=" * 70)
    
    # Look for world directories
    world_dirs = sorted([d for d in exports_dir.glob("world_*") if d.is_dir()])
    
    if not world_dirs:
        print("\nNo generated worlds found.")
        return
    
    for world_dir in world_dirs:
        world_subdir = world_dir / "world"
        if not world_subdir.exists():
            continue
            
        print(f"\n📄 {world_dir.name}")
        
        # Check for world.json metadata
        metadata_file = world_subdir / "world.json"
        if metadata_file.exists():
            import json
            with open(metadata_file) as f:
                metadata = json.load(f)
                design = metadata.get("design", {})
                layout = metadata.get("layout", {})
                print(f"   🌍 Biome: {design.get('biome', 'N/A')}")
                print(f"   🏔️  Terrain: {design.get('terrain_type', 'N/A')}")
                print(f"   📏 Scale: {design.get('scale_km', 0):.1f} km")
                print(f"   🏗️  Objects: {len(layout.get('objects', []))}")
                print(f"   🌳 Vegetation: {layout.get('vegetation_count', 0)}")
        
        # Check for OBJ file
        obj_file = world_subdir / "world.obj"
        if obj_file.exists():
            size_mb = obj_file.stat().st_size / (1024 * 1024)
            print(f"   🎨 3D Model: world.obj ({size_mb:.2f} MB)")
        
        # Check for preview
        preview_file = world_subdir / "preview.png"
        if preview_file.exists():
            print(f"   🖼️  Preview: preview.png")


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
    print("✨ Done! Check exports/world_*/ for files")
    print("=" * 70)
