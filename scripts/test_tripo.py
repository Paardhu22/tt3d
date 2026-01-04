"""Test Stability AI complete pipeline: Text → Image → 3D Model."""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_IMAGE_BASE = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_3D_BASE = "https://api.stability.ai/v2beta/3d/stable-fast-3d"

def test_stability_pipeline():
    """Test complete Stability AI pipeline."""
    print("\n" + "=" * 60)
    print("Testing Stability AI Pipeline: Text → Image → 3D")
    print("=" * 60)
    
    if not STABILITY_API_KEY:
        print("❌ STABILITY_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key: {STABILITY_API_KEY[:10]}...{STABILITY_API_KEY[-4:]}")
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }
    
    # Step 1: Text to Image
    print("\n🎨 Step 1: Generating image from text...")
    try:
        response = requests.post(
            STABILITY_IMAGE_BASE,
            headers=headers,
            files={"none": ""},
            data={
                "prompt": "a simple wooden cube, isometric view, clean background",
                "aspect_ratio": "1:1",
                "output_format": "png"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            image_bytes = response.content
            print(f"✅ Image: {len(image_bytes) / 1024:.2f} KB")
            
            # Step 2: Image to 3D
            print("\n🌍 Step 2: Converting to 3D (2048px, quad mesh)...")
            response_3d = requests.post(
                STABILITY_3D_BASE,
                headers={"Authorization": f"Bearer {STABILITY_API_KEY}"},
                files={"image": ("image.png", image_bytes, "image/png")},
                data={"texture_resolution": "2048", "foreground_ratio": "0.85", "remesh": "quad"},
                timeout=60
            )
            
            if response_3d.status_code == 200:
                print(f"\n✅ SUCCESS! Pipeline working!")
                print(f"📦 GLB: {len(response_3d.content) / 1024:.2f} KB")
                with open("test_stability_world.glb", "wb") as f:
                    f.write(response_3d.content)
                print(f"💾 Saved: test_stability_world.glb")
                return True
            else:
                print(f"\n❌ 3D Failed: {response_3d.status_code}")
                print(response_3d.text[:500])
                return False
        else:
            print(f"\n❌ Image Failed: {response.status_code}")
            print(response.text[:500])
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_stability_pipeline()
