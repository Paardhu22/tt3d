"""
Example usage of Tsuana 3D World Generator API.
Demonstrates programmatic world generation without interactive prompts.
"""

raise SystemExit("Use FastAPI endpoint /api/v1/world instead of legacy examples.")

import json
from scene_composer import SceneComposer

def example_1_simple_scene():
    """Generate a simple 3-object scene programmatically."""
    print("\n" + "=" * 50)
    print("Example 1: Simple Scene (3 objects)")
    print("=" * 50)
    
    generator = Tripo3DGenerator()
    composer = SceneComposer()
    
    # Define objects to generate
    objects = [
        {
            "name": "medieval_cottage",
            "prompt": "small medieval cottage with thatched roof and wooden walls",
            "position": (0, 0, 0),
            "scale": (1, 1, 1)
        },
        {
            "name": "oak_tree",
            "prompt": "large oak tree with full foliage and thick trunk",
            "position": (5, 0, 3),
            "scale": (1.5, 1.5, 1.5)
        },
        {
            "name": "stone_well",
            "prompt": "old stone water well with wooden bucket",
            "position": (-4, 0, 2),
            "scale": (0.8, 0.8, 0.8)
        }
    ]
    
    # Generate each object
    for obj in objects:
        print(f"\nGenerating: {obj['name']}...")
        try:
            result = generator.generate_from_text(
                prompt=obj["prompt"],
                style="realistic"
            )
            
            model_url = result["model_urls"].get("glb")
            if model_url:
                model_path = f"examples/{obj['name']}.glb"
                generator.download_model(model_url, model_path)
                
                composer.add_object(
                    name=obj["name"],
                    model_path=model_path,
                    position=obj["position"],
                    scale=obj["scale"]
                )
                print(f"✅ Success: {model_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Setup scene
    composer.setup_default_lighting("warm")
    composer.set_camera((8, 3, 12))
    composer.set_environment(sky_color=(0.7, 0.8, 0.9))
    
    # Export
    composer.export_scene_data("examples/simple_scene.json")
    composer.generate_aframe_html("examples/simple_scene.html")
    
    print("\n✅ Scene complete! Open examples/simple_scene.html")


def example_2_cyberpunk_alley():
    """Generate a cyberpunk alley scene."""
    print("\n" + "=" * 50)
    print("Example 2: Cyberpunk Alley")
    print("=" * 50)
    
    scene_plan = {
        "objects": [
            {
                "name": "alley_ground",
                "description": "wet concrete ground with puddles and grime, urban texture",
                "position": (0, -0.1, 0),
                "scale": (10, 0.1, 20)
            },
            {
                "name": "neon_sign",
                "description": "glowing neon sign with Japanese characters, pink and blue lights",
                "position": (-3, 2, 0),
                "scale": (1, 1, 1)
            },
            {
                "name": "dumpster",
                "description": "rusty metal dumpster with graffiti, cyberpunk style",
                "position": (4, 0, -5),
                "scale": (1.2, 1, 1.2)
            },
            {
                "name": "vending_machine",
                "description": "futuristic vending machine with glowing display screen",
                "position": (-4, 0, 5),
                "scale": (0.8, 1.5, 0.6)
            }
        ],
        "lighting": {
            "mood": "dark",
            "colors": ["pink", "blue", "cyan"]
        }
    }
    
    print(f"\n📦 {len(scene_plan['objects'])} objects planned")
    print("🎨 Style: Cyberpunk")
    print("💡 Lighting: Dark with neon accents")
    print("\n⚠️  This example requires API calls")
    print("Run with: python examples.py")


def example_3_batch_generation():
    """Show how to batch generate similar objects."""
    print("\n" + "=" * 50)
    print("Example 3: Batch Generation")
    print("=" * 50)
    
    # Generate a forest with multiple trees
    tree_variations = [
        "tall pine tree with dense needles",
        "oak tree with spreading branches",
        "birch tree with white bark",
        "willow tree with drooping branches"
    ]
    
    print(f"\n🌲 Would generate {len(tree_variations)} tree variations")
    print("📍 Auto-arranged in circle pattern")
    print("💾 Reusable for multiple forest scenes")
    
    # In production, you'd loop through and generate each
    # for prompt in tree_variations:
    #     result = generator.generate_from_text(prompt)


def example_4_scene_composition():
    """Demonstrate advanced scene composition without generation."""
    print("\n" + "=" * 50)
    print("Example 4: Scene Composition (No API calls)")
    print("=" * 50)
    
    composer = SceneComposer()
    
    # Add placeholder objects
    for i in range(5):
        composer.add_object(
            name=f"object_{i}",
            model_path=f"placeholder_{i}.glb",
            position=(0, 0, 0)  # Will be auto-arranged
        )
    
    # Auto-arrange in different layouts
    layouts = ["grid", "circle", "random"]
    
    for layout in layouts:
        composer.auto_arrange_objects(layout=layout)
        print(f"\n📐 {layout.upper()} Layout:")
        for obj in composer.objects:
            x, y, z = obj.position
            print(f"   {obj.name}: ({x:.1f}, {y:.1f}, {z:.1f})")
    
    # Export just the layout
    composer.export_scene_data("examples/layout_demo.json")
    print("\n✅ Layout saved to examples/layout_demo.json")


def example_5_custom_prompts():
    """Show how to customize the AI prompts."""
    print("\n" + "=" * 50)
    print("Example 5: Custom AI Prompts")
    print("=" * 50)
    
    custom_prompt = """
You are a 3D scene architect specializing in [THEME].

When the user describes a scene, generate:
1. 5-8 core objects
2. Atmospheric elements (particles, lighting)
3. Ground/environment base
4. Interactive elements (if applicable)

Output JSON with detailed 3D-generation-ready descriptions.
"""
    
    themes = ["fantasy", "sci-fi", "horror", "steampunk"]
    
    print("\n🎨 Available themes:", ", ".join(themes))
    print("📝 Custom prompt structure defined")
    print("💡 Edit prompts.py to implement")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("     TSUANA 3D WORLD GENERATOR - EXAMPLES")
    print("=" * 60)
    
    print("\nAvailable examples:")
    print("  1. Simple Scene (3 objects) - Live generation")
    print("  2. Cyberpunk Alley - Scene plan demo")
    print("  3. Batch Generation - Multiple variations")
    print("  4. Scene Composition - Layout algorithms")
    print("  5. Custom Prompts - AI customization")
    
    print("\n⚠️  Example 1 requires API keys and will incur costs")
    print("    Examples 2-5 are demonstrations only")
    
    choice = input("\nRun example (1-5, or 'all' for demos only): ").strip()
    
    if choice == "1":
        import os
        if not os.getenv("TRIPO_API_KEY"):
            print("\n❌ TRIPO_API_KEY not found in environment")
            print("   Set up .env file first")
            return
        example_1_simple_scene()
    elif choice == "2":
        example_2_cyberpunk_alley()
    elif choice == "3":
        example_3_batch_generation()
    elif choice == "4":
        example_4_scene_composition()
    elif choice == "5":
        example_5_custom_prompts()
    elif choice == "all":
        # Run non-API examples
        example_2_cyberpunk_alley()
        example_3_batch_generation()
        example_4_scene_composition()
        example_5_custom_prompts()
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
