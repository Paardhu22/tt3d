"""
Production-ready 3D VR World Generator - Main Entry Point
Converts text descriptions into complete 3D virtual reality worlds.
"""

import json
import os
import logging
from typing import Dict, Any, List
from user_profile import UserProfile
from tsuana import call_tsuana
from threed_generator import Tripo3DGenerator
from scene_composer import SceneComposer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ALLOWED_FIELDS = {"mood", "environment", "style", "scale"}


def position_hint_to_coordinates(hint: str, index: int, total: int) -> tuple:
    """Convert position hint to actual 3D coordinates."""
    positions = {
        "center": (0, 0, 0),
        "front": (0, 0, -5),
        "back": (0, 0, 5),
        "left": (-5, 0, 0),
        "right": (5, 0, 0),
        "far_left": (-10, 0, 0),
        "far_right": (10, 0, 0),
        "front_left": (-3, 0, -3),
        "front_right": (3, 0, -3),
        "back_left": (-3, 0, 3),
        "back_right": (3, 0, 3),
    }
    
    return positions.get(hint, (index * 3 - total * 1.5, 0, 0))


def scale_hint_to_value(hint: str) -> tuple:
    """Convert scale hint to scale multiplier."""
    scales = {
        "small": (0.5, 0.5, 0.5),
        "medium": (1.0, 1.0, 1.0),
        "large": (2.0, 2.0, 2.0),
        "huge": (3.0, 3.0, 3.0)
    }
    return scales.get(hint, (1.0, 1.0, 1.0))


def generate_3d_world(world_data: Dict[str, Any], output_dir: str = "output") -> None:
    """
    Generate a complete 3D world from the world plan.
    
    Args:
        world_data: World configuration from Tsuana
        output_dir: Directory to save all generated files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    world_plan = world_data["world_plan"]
    objects_config = world_data.get("objects", [])
    lighting_config = world_data.get("lighting", {})
    camera_config = world_data.get("camera", {})
    
    logger.info("=" * 50)
    logger.info(f"GENERATING 3D WORLD: {world_plan.get('environment', 'Unknown')}")
    logger.info("=" * 50)
    
    # Initialize generators
    generator = Tripo3DGenerator()
    composer = SceneComposer()
    
    # Generate each 3D object
    generated_models = []
    
    print(f"\n📦 Generating {len(objects_config)} 3D objects...\n")
    
    for i, obj_config in enumerate(objects_config):
        obj_name = obj_config["name"]
        obj_description = obj_config["description"]
        position_hint = obj_config.get("position_hint", "center")
        scale_hint = obj_config.get("scale_hint", "medium")
        
        print(f"[{i+1}/{len(objects_config)}] Generating: {obj_name}")
        print(f"    Description: {obj_description}")
        
        try:
            # Generate 3D model
            model_filename = f"{obj_name.replace(' ', '_')}.glb"
            model_path = os.path.join(output_dir, model_filename)
            
            result = generator.generate_from_text(
                prompt=obj_description,
                style=world_plan.get("style", "realistic")
            )
            
            # Download the model
            model_urls = result["model_urls"]
            glb_url = model_urls.get("glb") or model_urls.get("fbx") or model_urls.get("obj")
            
            if glb_url:
                generator.download_model(glb_url, model_path)
                
                # Add to scene
                position = position_hint_to_coordinates(position_hint, i, len(objects_config))
                scale = scale_hint_to_value(scale_hint)
                
                composer.add_object(
                    name=obj_name,
                    model_path=model_path,
                    position=position,
                    scale=scale
                )
                
                generated_models.append({
                    "name": obj_name,
                    "path": model_path,
                    "status": "success"
                })
                
                print(f"    ✅ Generated successfully: {model_filename}\n")
            else:
                print(f"    ⚠️  No downloadable model URL\n")
                generated_models.append({
                    "name": obj_name,
                    "status": "failed",
                    "reason": "No download URL"
                })
                
        except Exception as e:
            logger.error(f"Failed to generate {obj_name}: {e}")
            print(f"    ❌ Error: {e}\n")
            generated_models.append({
                "name": obj_name,
                "status": "failed",
                "reason": str(e)
            })
    
    # Setup lighting
    print("💡 Configuring lighting...")
    mood = lighting_config.get("mood", "neutral")
    composer.setup_default_lighting(mood)
    
    # Setup camera
    print("📷 Setting up camera...")
    camera_desc = camera_config.get("position", "front view")
    if "front" in camera_desc.lower():
        composer.set_camera((0, 1.6, 10))
    elif "top" in camera_desc.lower():
        composer.set_camera((0, 15, 0))
    elif "side" in camera_desc.lower():
        composer.set_camera((10, 1.6, 0))
    else:
        composer.set_camera((5, 3, 8))
    
    # Setup environment
    print("🌍 Configuring environment...")
    composer.set_environment(
        sky_color=(0.6, 0.8, 1.0),
        ambient_light=lighting_config.get("ambient_intensity", 0.4)
    )
    
    # Export scene data
    print("\n📄 Exporting scene files...")
    scene_json_path = os.path.join(output_dir, "scene_data.json")
    composer.export_scene_data(scene_json_path)
    
    # Generate VR viewer (A-Frame HTML)
    vr_html_path = os.path.join(output_dir, "vr_viewer.html")
    composer.generate_aframe_html(vr_html_path)
    
    # Generate Unity import script
    unity_script_path = os.path.join(output_dir, "ImportScene.cs")
    composer.generate_unity_import_script(unity_script_path)
    
    # Save generation report
    report = {
        "world_plan": world_plan,
        "generated_objects": generated_models,
        "total_objects": len(objects_config),
        "successful": sum(1 for m in generated_models if m["status"] == "success"),
        "failed": sum(1 for m in generated_models if m["status"] == "failed"),
        "output_directory": output_dir,
        "files": {
            "scene_data": scene_json_path,
            "vr_viewer": vr_html_path,
            "unity_script": unity_script_path
        }
    }
    
    report_path = os.path.join(output_dir, "generation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎉 3D WORLD GENERATION COMPLETE!")
    print("=" * 50)
    print(f"\n✅ Successfully generated: {report['successful']}/{report['total_objects']} objects")
    
    if report['failed'] > 0:
        print(f"⚠️  Failed: {report['failed']} objects")
    
    print(f"\n📁 Output directory: {output_dir}/")
    print(f"\n📋 Generated files:")
    print(f"   • Scene data: scene_data.json")
    print(f"   • VR Viewer: vr_viewer.html (Open in browser)")
    print(f"   • Unity import: ImportScene.cs")
    print(f"   • Generation report: generation_report.json")
    
    print(f"\n🌐 To view in VR:")
    print(f"   1. Open {vr_html_path} in a WebVR-compatible browser")
    print(f"   2. Use WASD to move, mouse to look around")
    print(f"   3. Click 'Enter VR' for immersive mode")
    
    print("\n" + "=" * 50)


def main():
    """Main entry point for the 3D world generator."""
    print("\n" + "=" * 50)
    print("    TSUANA: 3D VR WORLD GENERATOR")
    print("=" * 50)
    print("\nDescribe the 3D world you want to create.")
    print("(Type 'exit' to quit)\n")

    profile = UserProfile()
    last_target = None

    while True:
        user_input = input("\n💬 You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("\n👋 Exiting. Goodbye!")
            break

        # STEP 1 — Save previous answer
        if last_target:
            if last_target in ALLOWED_FIELDS and profile.is_valid_value(user_input):
                setattr(profile, last_target, user_input)
                print(f"✅ Saved {last_target}: {user_input}")
            else:
                print("⚠️  Input not saved. Clarification needed.")
            last_target = None

        # STEP 2 — Decide mode
        mode = "generation" if profile.is_complete() else "clarification"

        # STEP 3 — Call Tsuana
        print("\n🤔 Processing...")
        raw_response = call_tsuana(mode, user_input, profile.to_dict())

        try:
            data = json.loads(raw_response)

            # STEP 4 — Clarification
            if data["type"] == "question":
                print(f"\n🤖 Tsuana: {data['question']}")
                last_target = data.get("target_attribute")

            # STEP 5 — Final generation
            elif data["type"] == "final_prompt":
                print("\n✅ World plan generated!")
                
                # Save full world data
                with open("world_plan.json", "w") as f:
                    json.dump(data, f, indent=2)
                
                print("\n📋 World Plan Summary:")
                world_plan = data["world_plan"]
                print(f"   Environment: {world_plan['environment']}")
                print(f"   Mood: {world_plan['mood']}")
                print(f"   Style: {world_plan['style']}")
                print(f"   Scale: {world_plan['scale']}")
                print(f"   Objects to generate: {len(data.get('objects', []))}")
                
                # Ask for confirmation
                print("\n" + "-" * 50)
                confirm = input("\n🚀 Start 3D world generation? (yes/no): ").strip().lower()
                
                if confirm in {"yes", "y"}:
                    try:
                        generate_3d_world(data)
                    except Exception as e:
                        logger.error(f"World generation failed: {e}")
                        print(f"\n❌ Error during generation: {e}")
                else:
                    print("\n🚫 Generation cancelled.")
                
                break

            else:
                print("\n❌ Unknown response type from Tsuana.")
                break

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            print(f"\n❌ Invalid response from Tsuana: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n❌ System error: {e}")
            break


if __name__ == "__main__":
    main()
