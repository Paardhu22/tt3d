"""
Production-ready 3D world generator using Stability AI.
Two-step process: Text-to-Image → Image-to-3D with optimized quality settings.
"""

import os
import time
import requests
import logging
import subprocess
import tempfile
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_IMAGE_BASE = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_3D_BASE = "https://api.stability.ai/v2beta/3d/stable-fast-3d"


class StabilityAIGenerator:
    """Production-ready 3D world generator using Stability AI with optimized settings."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or STABILITY_API_KEY
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
    
    def generate_from_text(
        self,
        prompt: str,
        texture_resolution: int = 2048,
        foreground_ratio: float = 0.85,
        remesh: str = "quad",
        image_quality: str = "high",
        max_retries: int = 3,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Generate a 3D world from text prompt using two-step process.
        
        Step 1: Generate high-quality image from text
        Step 2: Convert image to 3D model
        
        Args:
            prompt: Text description of the 3D world/scene
            texture_resolution: Texture quality (1024, 2048, 4096) - higher is better
            foreground_ratio: How much of frame the model occupies (0.5-1.0)
            remesh: Mesh quality ("none", "quad", "triangle") - quad is best
            image_quality: Image generation quality ("standard", "high", "ultra")
            max_retries: Maximum number of retry attempts
            timeout: Maximum wait time in seconds
            
        Returns:
            Dict containing model file data and metadata
            
        Raises:
            Exception: If generation fails or times out
        """
        logger.info(f"Generating 3D world from text: '{prompt[:100]}...'")
        
        # Step 1: Generate image from text
        image_data = self._generate_image(prompt, image_quality, max_retries, timeout)
        logger.info(f"Image generated: {len(image_data)} bytes")
        
        # Step 2: Convert image to 3D
        result = self._generate_3d_from_image(
            image_data, 
            texture_resolution, 
            foreground_ratio, 
            remesh, 
            max_retries,
            timeout
        )
        
        logger.info(f"Successfully generated 3D world")
        return result
    
    def _generate_image(
        self,
        prompt: str,
        quality: str,
        max_retries: int,
        timeout: int
    ) -> bytes:
        """Generate high-quality image from text using Stability AI Core."""
        
        # Optimize prompt for 3D-suitable images
        optimized_prompt = f"{prompt}, isometric view, clean background, well-lit, detailed, professional 3D render style"
        
        data = {
            "prompt": optimized_prompt,
            "negative_prompt": "blurry, low quality, distorted, artifacts, text, watermark",
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating image (attempt {attempt + 1}/{max_retries})...")
                response = requests.post(
                    STABILITY_IMAGE_BASE,
                    headers=self.headers,
                    files={"none": ""},
                    data=data,
                    timeout=timeout
                )
                response.raise_for_status()
                
                logger.info(f"Image generated successfully")
                return response.content
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate image after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
    
    def _generate_3d_from_image(
        self,
        image_data: bytes,
        texture_resolution: int,
        foreground_ratio: float,
        remesh: str,
        max_retries: int,
        timeout: int
    ) -> Dict[str, Any]:
        """Convert image to 3D model using Stability AI Fast 3D."""
        
        # Prepare multipart form data with optimized settings
        files = {
            "image": ("image.png", image_data, "image/png")
        }
        
        data = {
            "texture_resolution": str(texture_resolution),
            "foreground_ratio": str(foreground_ratio),
            "remesh": remesh,
        }
        
        headers_3d = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Converting to 3D (attempt {attempt + 1}/{max_retries})...")
                response = requests.post(
                    STABILITY_3D_BASE,
                    headers=headers_3d,
                    files=files,
                    data=data,
                    timeout=timeout
                )
                response.raise_for_status()
                
                logger.info(f"3D model generated: {len(response.content)} bytes")
                return {
                    "model_data": response.content,
                    "format": "glb",
                    "size_bytes": len(response.content),
                    "texture_resolution": texture_resolution
                }
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate 3D after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
    
    def save_model(
        self,
        model_data: bytes,
        output_path: str,
        export_obj: bool = True
    ) -> Tuple[str, Optional[str]]:
        """Save 3D model data to file and optionally convert to OBJ."""
        logger.info(f"Saving model to: {output_path}")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Save GLB file
        with open(output_path, "wb") as f:
            f.write(model_data)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"Saved GLB: {file_size / 1024:.2f} KB")
        
        # Convert to OBJ if requested
        obj_path = None
        if export_obj:
            obj_path = self._convert_glb_to_obj(output_path)
        
        return output_path, obj_path
    
    def _convert_glb_to_obj(self, glb_path: str) -> Optional[str]:
        """Convert GLB to OBJ format using internal converter."""
        try:
            import trimesh
            logger.info("Converting GLB to OBJ...")
            
            # Load GLB
            mesh = trimesh.load(glb_path)
            
            # Export as OBJ
            obj_path = glb_path.replace(".glb", ".obj")
            mesh.export(obj_path)
            
            logger.info(f"Converted to OBJ: {obj_path}")
            return obj_path
        except ImportError:
            logger.warning("trimesh not installed, skipping OBJ conversion")
            logger.info("Install with: pip install trimesh")
            return None
        except Exception as e:
            logger.error(f"Failed to convert to OBJ: {e}")
            return None


def generate_3d_world(
    prompt: str,
    output_path: str = "world.glb",
    texture_resolution: int = 2048,
    high_quality: bool = True
) -> str:
    """
    Convenience function to generate and save a 3D world.
    
    Args:
        prompt: Text description of the world/scene
        output_path: Where to save the GLB file
        texture_resolution: Texture quality (1024, 2048, 4096)
        high_quality: Use best quality settings
        
    Returns:
        Path to the saved model file
    """
    generator = StabilityAIGenerator()
    
    # Use optimized settings for best quality
    result = generator.generate_from_text(
        prompt=prompt,
        texture_resolution=texture_resolution,
        foreground_ratio=0.85,  # Optimized for full scenes
        remesh="quad" if high_quality else "triangle",
        image_quality="high" if high_quality else "standard"
    )
    
    # Save the model
    return generator.save_model(result["model_data"], output_path)


if __name__ == "__main__":
    # Test the generator
    test_prompt = "a cozy campfire scene with logs and stones in a forest clearing"
    try:
        model_path = generate_3d_world(test_prompt, "test_world.glb")
        print(f"✅ World generated successfully: {model_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
