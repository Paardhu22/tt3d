"""
Music generation service using Stability AI.
Generates ambient music/soundscapes for 3D worlds.
"""

import os
import time
import requests
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_AUDIO_BASE = "https://api.stability.ai/v2beta/sound-generation/generate"


class MusicGenerator:
    """Generate ambient music for 3D worlds using Stability AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or STABILITY_API_KEY
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY required for music generation")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def generate_ambient_music(
        self,
        description: str,
        duration: int = 30,
        output_path: str = "ambient_music.mp3"
    ) -> Optional[str]:
        """
        Generate ambient music/soundscape.
        
        Args:
            description: Music mood/style description
            duration: Length in seconds (max 30)
            output_path: Where to save the audio file
            
        Returns:
            Path to saved audio file or None if failed
        """
        try:
            logger.info(f"Generating ambient music: {description}")
            
            # Optimize prompt for ambient music
            music_prompt = f"ambient {description} music, atmospheric, looping, no vocals, instrumental"
            
            data = {
                "prompt": music_prompt,
                "duration": min(duration, 30),  # API limit
                "output_format": "mp3"
            }
            
            response = requests.post(
                STABILITY_AUDIO_BASE,
                headers=self.headers,
                files={"none": ""},
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                # Save audio file
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024
                logger.info(f"Music generated: {output_path} ({file_size:.2f} KB)")
                return output_path
            else:
                logger.warning(f"Music generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Music generation error: {e}")
            return None


def generate_world_music(
    world_mood: str,
    environment: str,
    output_dir: str = "."
) -> Optional[str]:
    """Generate appropriate ambient music for a world."""
    try:
        generator = MusicGenerator()
        description = f"{world_mood} {environment}"
        output_path = os.path.join(output_dir, "ambient_music.mp3")
        return generator.generate_ambient_music(description, output_path=output_path)
    except ValueError:
        logger.warning("Music generation not available (API key missing)")
        return None
    except Exception as e:
        logger.error(f"Failed to generate music: {e}")
        return None
