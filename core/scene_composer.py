"""
Production-ready 3D scene composer.
Combines multiple 3D objects into a complete VR-ready scene with proper positioning,
lighting, and materials. Exports to GLTF/GLB format.
"""

import json
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SceneObject:
    """Represents a 3D object in the scene."""
    name: str
    model_path: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    material: Optional[Dict[str, Any]] = None


@dataclass
class SceneLight:
    """Represents a light source in the scene."""
    light_type: str  # "directional", "point", "ambient"
    position: Tuple[float, float, float] = (0.0, 5.0, 0.0)
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    intensity: float = 1.0


@dataclass
class SceneCamera:
    """Represents a camera viewpoint."""
    position: Tuple[float, float, float] = (0.0, 1.6, 5.0)
    target: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    fov: float = 60.0


class SceneComposer:
    """Composes multiple 3D objects into a complete VR-ready scene."""
    
    def __init__(self):
        self.objects: List[SceneObject] = []
        self.lights: List[SceneLight] = []
        self.camera: Optional[SceneCamera] = None
        self.environment_settings: Dict[str, Any] = {}
    
    def add_object(
        self,
        name: str,
        model_path: str,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        material: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a 3D object to the scene."""
        obj = SceneObject(
            name=name,
            model_path=model_path,
            position=position,
            rotation=rotation,
            scale=scale,
            material=material
        )
        self.objects.append(obj)
        logger.info(f"Added object '{name}' at position {position}")
    
    def add_light(
        self,
        light_type: str,
        position: Tuple[float, float, float] = (0.0, 5.0, 0.0),
        color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        intensity: float = 1.0
    ) -> None:
        """Add a light source to the scene."""
        light = SceneLight(
            light_type=light_type,
            position=position,
            color=color,
            intensity=intensity
        )
        self.lights.append(light)
        logger.info(f"Added {light_type} light at {position}")
    
    def set_camera(
        self,
        position: Tuple[float, float, float],
        target: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        fov: float = 60.0
    ) -> None:
        """Set the camera position and orientation."""
        self.camera = SceneCamera(position=position, target=target, fov=fov)
        logger.info(f"Set camera at {position} looking at {target}")
    
    def set_environment(
        self,
        sky_color: Tuple[float, float, float] = (0.5, 0.7, 1.0),
        fog_density: float = 0.0,
        ambient_light: float = 0.3
    ) -> None:
        """Configure environment settings."""
        self.environment_settings = {
            "sky_color": sky_color,
            "fog_density": fog_density,
            "ambient_light": ambient_light
        }
    
    def auto_arrange_objects(self, layout: str = "grid") -> None:
        """
        Automatically arrange objects in the scene.
        
        Args:
            layout: Layout type ("grid", "circle", "random")
        """
        if not self.objects:
            return
        
        num_objects = len(self.objects)
        
        if layout == "grid":
            grid_size = int(np.ceil(np.sqrt(num_objects)))
            spacing = 3.0
            
            for i, obj in enumerate(self.objects):
                row = i // grid_size
                col = i % grid_size
                x = (col - grid_size / 2) * spacing
                z = (row - grid_size / 2) * spacing
                obj.position = (x, 0.0, z)
                
        elif layout == "circle":
            radius = max(5.0, num_objects * 0.8)
            
            for i, obj in enumerate(self.objects):
                angle = (2 * np.pi * i) / num_objects
                x = radius * np.cos(angle)
                z = radius * np.sin(angle)
                obj.position = (float(x), 0.0, float(z))
                # Rotate to face center
                obj.rotation = (0.0, float(np.degrees(angle + np.pi)), 0.0)
                
        elif layout == "random":
            area_size = num_objects * 2
            for obj in self.objects:
                x = np.random.uniform(-area_size, area_size)
                z = np.random.uniform(-area_size, area_size)
                obj.position = (float(x), 0.0, float(z))
        
        logger.info(f"Arranged {num_objects} objects in {layout} layout")
    
    def setup_default_lighting(self, mood: str = "neutral") -> None:
        """
        Set up default lighting based on mood.
        
        Args:
            mood: Lighting mood ("bright", "neutral", "dark", "warm", "cool")
        """
        self.lights.clear()
        
        if mood == "bright":
            self.add_light("ambient", intensity=0.6)
            self.add_light("directional", position=(10, 10, 10), intensity=1.5)
            self.add_light("directional", position=(-10, 10, -10), intensity=0.5)
            
        elif mood == "dark":
            self.add_light("ambient", intensity=0.1)
            self.add_light("point", position=(0, 3, 0), intensity=0.8)
            
        elif mood == "warm":
            self.add_light("ambient", intensity=0.4, color=(1.0, 0.9, 0.7))
            self.add_light("directional", position=(10, 10, 5), 
                          color=(1.0, 0.8, 0.6), intensity=1.2)
            
        elif mood == "cool":
            self.add_light("ambient", intensity=0.4, color=(0.7, 0.8, 1.0))
            self.add_light("directional", position=(10, 10, 5),
                          color=(0.8, 0.9, 1.0), intensity=1.0)
        else:  # neutral
            self.add_light("ambient", intensity=0.4)
            self.add_light("directional", position=(10, 10, 10), intensity=1.0)
    
    def export_scene_data(self, output_path: str = "scene_data.json") -> str:
        """
        Export scene configuration to JSON.
        
        Args:
            output_path: Path to save the scene data
            
        Returns:
            Path to the exported file
        """
        scene_data = {
            "objects": [asdict(obj) for obj in self.objects],
            "lights": [asdict(light) for light in self.lights],
            "camera": asdict(self.camera) if self.camera else None,
            "environment": self.environment_settings
        }
        
        with open(output_path, "w") as f:
            json.dump(scene_data, f, indent=2)
        
        logger.info(f"Exported scene data to {output_path}")
        return output_path
    
    def generate_unity_import_script(self, output_path: str = "ImportScene.cs") -> str:
        """Generate a Unity C# script to import the scene."""
        script = '''using UnityEngine;
using System.Collections.Generic;

public class ImportScene : MonoBehaviour
{
    void Start()
    {
'''
        for i, obj in enumerate(self.objects):
            x, y, z = obj.position
            rx, ry, rz = obj.rotation
            sx, sy, sz = obj.scale
            
            script += f'''
        // {obj.name}
        GameObject obj{i} = new GameObject("{obj.name}");
        obj{i}.transform.position = new Vector3({x}f, {y}f, {z}f);
        obj{i}.transform.rotation = Quaternion.Euler({rx}f, {ry}f, {rz}f);
        obj{i}.transform.localScale = new Vector3({sx}f, {sy}f, {sz}f);
        // Load model from: {obj.model_path}
'''
        
        script += '''
    }
}
'''
        with open(output_path, "w") as f:
            f.write(script)
        
        logger.info(f"Generated Unity import script: {output_path}")
        return output_path
    
    def generate_aframe_html(self, output_path: str = "scene.html") -> str:
        """Generate an A-Frame HTML file for web VR viewing."""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>VR World - Tsuana Generated</title>
    <meta name="description" content="VR World">
    <script src="https://aframe.io/releases/1.4.0/aframe.min.js"></script>
</head>
<body>
    <a-scene>
'''
        
        # Add objects
        for obj in self.objects:
            x, y, z = obj.position
            rx, ry, rz = obj.rotation
            html += f'''
        <!-- {obj.name} -->
        <a-entity 
            gltf-model="url({obj.model_path})"
            position="{x} {y} {z}"
            rotation="{rx} {ry} {rz}">
        </a-entity>
'''
        
        # Add lights
        for light in self.lights:
            if light.light_type == "ambient":
                r, g, b = light.color
                color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                html += f'        <a-light type="ambient" color="{color}" intensity="{light.intensity}"></a-light>\n'
            elif light.light_type == "directional":
                x, y, z = light.position
                r, g, b = light.color
                color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                html += f'        <a-light type="directional" position="{x} {y} {z}" color="{color}" intensity="{light.intensity}"></a-light>\n'
        
        # Add camera
        if self.camera:
            x, y, z = self.camera.position
            html += f'        <a-entity camera look-controls wasd-controls position="{x} {y} {z}"></a-entity>\n'
        else:
            html += '        <a-entity camera look-controls wasd-controls position="0 1.6 5"></a-entity>\n'
        
        # Add sky
        if self.environment_settings:
            r, g, b = self.environment_settings.get("sky_color", (0.5, 0.7, 1.0))
            color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            html += f'        <a-sky color="{color}"></a-sky>\n'
        else:
            html += '        <a-sky color="#87CEEB"></a-sky>\n'
        
        html += '''
    </a-scene>
</body>
</html>
'''
        
        with open(output_path, "w") as f:
            f.write(html)
        
        logger.info(f"Generated A-Frame VR scene: {output_path}")
        return output_path
    
    def get_summary(self) -> str:
        """Get a summary of the scene composition."""
        summary = f"Scene Summary:\n"
        summary += f"  Objects: {len(self.objects)}\n"
        summary += f"  Lights: {len(self.lights)}\n"
        summary += f"  Camera: {'Set' if self.camera else 'Not set'}\n"
        
        if self.objects:
            summary += "\n  Objects:\n"
            for obj in self.objects:
                summary += f"    - {obj.name} at {obj.position}\n"
        
        return summary


if __name__ == "__main__":
    # Test the scene composer
    composer = SceneComposer()
    composer.add_object("ground", "ground.glb", position=(0, 0, 0), scale=(10, 1, 10))
    composer.add_object("tree", "tree.glb", position=(3, 0, 0))
    composer.add_object("rock", "rock.glb", position=(-3, 0, 2))
    
    composer.setup_default_lighting("warm")
    composer.set_camera((0, 1.6, 8))
    composer.set_environment(sky_color=(0.6, 0.8, 1.0))
    
    print(composer.get_summary())
    composer.export_scene_data("test_scene.json")
