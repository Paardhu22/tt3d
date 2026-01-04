"""Procedural ambient audio generator (no external APIs)."""
from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Optional

import numpy as np


def _brownian_noise(length: int, rng: np.random.Generator) -> np.ndarray:
    steps = rng.normal(scale=0.02, size=length)
    return np.cumsum(steps)


def generate_ambient_music(mood: str, output_dir: str | Path, duration_seconds: int = 45) -> Optional[str]:
    sample_rate = 22050
    length = duration_seconds * sample_rate
    rng = np.random.default_rng(42)
    base = _brownian_noise(length, rng)

    mood = mood.lower()
    harmonics = [0.25, 0.5, 0.75] if "calm" in mood or "serene" in mood else [0.3, 0.6, 0.9]
    carrier_freq = 110 if "dark" in mood else 220
    time = np.arange(length) / sample_rate
    signal = np.zeros_like(base)
    for h in harmonics:
        signal += np.sin(2 * math.pi * (carrier_freq * h) * time)
    signal = signal * 0.2 + base * 0.05
    signal = np.clip(signal, -1.0, 1.0)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ambient_music.wav"

    audio = (signal * 32767).astype(np.int16)
    with wave.open(str(output_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return str(output_path)
