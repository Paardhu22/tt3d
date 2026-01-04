"""Export procedural world into OBJ/MTL plus metadata."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import trimesh
from PIL import Image

from app.schemas import WorldMetadata
from core.procedural_engine import MeshAsset, WorldBuildResult


@dataclass
class WorldExport:
    world_path: Path
    preview_image: Path
    unity_import: Path
    metadata_path: Path


class MeshExporter:
    def __init__(self, root: Path | str = "exports"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _write_materials(self, materials_dir: Path, materials: Dict[str, List[int]]) -> Dict[str, Path]:
        texture_paths: Dict[str, Path] = {}
        materials_dir.mkdir(parents=True, exist_ok=True)
        for name, color in materials.items():
            texture = Image.new("RGB", (256, 256), tuple(color))
            texture_path = materials_dir / f"{name}.png"
            texture.save(texture_path)
            texture_paths[name] = texture_path
        return texture_paths

    def _write_mtl(self, mtl_path: Path, texture_paths: Dict[str, Path]) -> None:
        lines = []
        for name, tex_path in texture_paths.items():
            r, g, b = Image.open(tex_path).convert("RGB").getpixel((0, 0))
            lines.append(f"newmtl {name}")
            lines.append(f"Kd {r/255:.4f} {g/255:.4f} {b/255:.4f}")
            lines.append("Ka 0.2 0.2 0.2")
            lines.append("Ks 0.0 0.0 0.0")
            lines.append("d 1.0")
            lines.append(f"map_Kd textures/{tex_path.name}")
            lines.append("")
        mtl_path.write_text("\n".join(lines))

    @staticmethod
    def _export_meshes(geometry_dir: Path, meshes: List[MeshAsset], mtl_name: str) -> Path:
        geometry_dir.mkdir(parents=True, exist_ok=True)
        scene = trimesh.Scene()
        for asset in meshes:
            mesh = asset.mesh.copy()
            material = getattr(mesh.visual, "material", None)
            if material is None or not hasattr(material, "name"):
                mesh.visual.material = trimesh.visual.material.SimpleMaterial(name=asset.material)
            else:
                mesh.visual.material.name = asset.material
            scene.add_geometry(mesh, node_name=asset.name)
        world_obj = geometry_dir.parent / "world.obj"
        scene.export(world_obj, file_type="obj", include_normals=True, include_color=True, mtl_name=mtl_name)
        return world_obj

    @staticmethod
    def _write_preview(preview_path: Path, heightmap: np.ndarray) -> None:
        normalized = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min() + 1e-6)
        img = (normalized * 255).astype(np.uint8)
        image = Image.fromarray(img, mode="L").convert("RGB")
        image.save(preview_path)

    @staticmethod
    def _write_unity_script(path: Path, world_obj_relative: str) -> None:
        script = f"""using UnityEngine;
using UnityEditor;
public class TsuanaWorldImporter : MonoBehaviour
{{
    [MenuItem("Tsuana/Import World")]
    static void ImportWorld()
    {{
        var path = "{world_obj_relative}";
        var obj = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (obj == null) {{
            Debug.LogError("World OBJ not found at " + path);
            return;
        }}
        var instance = Instantiate(obj);
        instance.transform.position = Vector3.zero;
        Selection.activeGameObject = instance;
    }}
}}
"""
        path.write_text(script)

    def export(self, build: WorldBuildResult, metadata: WorldMetadata, run_id: str) -> WorldExport:
        world_dir = self.root / run_id / "world"
        geometry_dir = world_dir / "geometry"
        textures_dir = world_dir / "textures"
        materials_dir = world_dir / "materials"
        world_dir.mkdir(parents=True, exist_ok=True)

        materials = {
            "terrain": [118, 102, 83],
            "metal": [180, 185, 190],
            "concrete": [160, 160, 160],
            "asphalt": [38, 38, 38],
            "water": [25, 95, 150],
            "foliage": [34, 120, 72],
        }
        texture_paths = self._write_materials(textures_dir, materials)
        mtl_path = world_dir / "world.mtl"
        self._write_mtl(mtl_path, texture_paths)

        world_obj_path = self._export_meshes(geometry_dir, build.meshes, mtl_name=mtl_path.name)
        preview_path = world_dir / "preview.png"
        self._write_preview(preview_path, build.heightmap)

        metadata_path = world_dir / "world.json"
        metadata.layout = build.layout  # ensure updated layout is persisted
        metadata_dict = metadata.model_dump()
        metadata_path.write_text(json.dumps(metadata_dict, indent=2))

        unity_script = world_dir / "unity_import.cs"
        rel_obj = os.path.relpath(world_obj_path, world_dir)
        self._write_unity_script(unity_script, rel_obj.replace("\\", "/"))

        return WorldExport(
            world_path=world_dir,
            preview_image=preview_path,
            unity_import=unity_script,
            metadata_path=metadata_path,
        )
