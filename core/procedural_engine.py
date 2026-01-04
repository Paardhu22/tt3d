"""Procedural world builder (Stage 3)."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import trimesh
from noise import pnoise2
from shapely.geometry import LineString, Point

from app.schemas import (
    ObjectPlacementRule,
    SplineRule,
    WorldLayout,
    WorldLayoutObject,
    WorldSchema,
)


@dataclass
class MeshAsset:
    name: str
    mesh: trimesh.Trimesh
    material: str
    kind: str


@dataclass
class WorldBuildResult:
    meshes: List[MeshAsset]
    heightmap: np.ndarray
    layout: WorldLayout


class ProceduralEngine:
    """Build a VR-ready world using procedural techniques only."""

    def __init__(self, grid_resolution: int = 180):
        self.grid_resolution = grid_resolution

    def _generate_heightmap(self, schema: WorldSchema) -> np.ndarray:
        noise_cfg = schema.heightmap
        size = schema.scale_km * 1000
        step = size / (self.grid_resolution - 1)
        hm = np.zeros((self.grid_resolution, self.grid_resolution), dtype=np.float32)
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                x = (i * step) / size
                y = (j * step) / size
                elevation = 0.0
                freq = noise_cfg.frequency
                amp = noise_cfg.amplitude
                for _ in range(noise_cfg.octaves):
                    elevation += pnoise2(
                        x * freq,
                        y * freq,
                        repeatx=1024,
                        repeaty=1024,
                        base=noise_cfg.seed,
                    ) * amp
                    freq *= noise_cfg.lacunarity
                    amp *= noise_cfg.persistence
                hm[i, j] = elevation
        hm = (hm - hm.min()) / (hm.max() - hm.min() + 1e-6)
        hm = hm * noise_cfg.elevation_scale + noise_cfg.base_height
        return hm

    @staticmethod
    def _carve_spline(heightmap: np.ndarray, schema: WorldSchema, spline: SplineRule) -> None:
        size = schema.scale_km * 1000
        step = size / (heightmap.shape[0] - 1)
        line = LineString([(p[0], p[2]) for p in spline.control_points])
        buffer = line.buffer(spline.width, cap_style=2, join_style=2)
        depth = spline.depth
        for i in range(heightmap.shape[0]):
            for j in range(heightmap.shape[1]):
                x = i * step
                y = j * step
                if buffer.contains(Point(x, y)):
                    if spline.kind == "river":
                        heightmap[i, j] -= depth
                    else:
                        heightmap[i, j] -= depth * 0.3

    def _build_terrain_mesh(self, heightmap: np.ndarray, schema: WorldSchema) -> trimesh.Trimesh:
        resolution = heightmap.shape[0]
        size = schema.scale_km * 1000
        step = size / (resolution - 1)
        vertices: List[Tuple[float, float, float]] = []
        for i in range(resolution):
            for j in range(resolution):
                vertices.append((i * step, heightmap[i, j], j * step))

        faces: List[Tuple[int, int, int]] = []
        for i in range(resolution - 1):
            for j in range(resolution - 1):
                a = i * resolution + j
                b = a + 1
                c = a + resolution
                d = c + 1
                faces.append((a, c, b))
                faces.append((b, c, d))

        terrain = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=False)
        terrain.visual.vertex_colors = [122, 104, 80, 255]
        return terrain

    @staticmethod
    def _place_object(rule: ObjectPlacementRule, size_m: float, rng: random.Random) -> Tuple[np.ndarray, np.ndarray]:
        theta = rng.uniform(0, 2 * math.pi)
        radius = rng.uniform(rule.scatter_radius * 0.4, rule.scatter_radius)
        x = size_m / 2 + math.cos(theta) * radius
        z = size_m / 2 + math.sin(theta) * radius
        scale = rng.uniform(*rule.scale_range)
        height = rng.uniform(*rule.height_range)
        return np.array([x, 0.0, z], dtype=np.float32), np.array([scale, height / 10.0, scale], dtype=np.float32)

    def _make_structure(self, rule: ObjectPlacementRule, position: np.ndarray, scale: np.ndarray, idx: int) -> MeshAsset:
        kind = rule.kind
        if kind in {"tower", "spire"}:
            mesh = trimesh.creation.cylinder(radius=6 * scale[0], height=scale[1] * 10)
        elif kind == "bridge":
            mesh = trimesh.creation.box(extents=(scale[0] * 40, scale[1] * 2.5, scale[0] * 12))
        elif kind == "dome":
            mesh = trimesh.creation.icosphere(subdivisions=3, radius=scale[0] * 12)
        else:
            mesh = trimesh.creation.box(extents=(scale[0] * 12, scale[1] * 4, scale[0] * 12))

        mesh.apply_translation(position + np.array([0.0, mesh.extents[1] * 0.5, 0.0]))
        material = "metal" if kind in {"tower", "spire"} else "concrete"
        mesh.visual.vertex_colors = [180, 185, 190, 255]
        return MeshAsset(name=f"{kind}_{idx}", mesh=mesh, material=material, kind=kind)

    def _scatter_vegetation(self, schema: WorldSchema, heightmap: np.ndarray, rng: random.Random) -> List[MeshAsset]:
        count = int(schema.vegetation.density_per_km2 * max(schema.scale_km, 1))
        count = min(count, 4000)  # avoid excessive meshes
        size_m = schema.scale_km * 1000
        assets: List[MeshAsset] = []
        base_mesh = trimesh.creation.cone(radius=1.1, height=4.5, sections=12)

        hm_res = heightmap.shape[0]
        step = size_m / (hm_res - 1)
        for i in range(count):
            x = rng.uniform(0, size_m)
            z = rng.uniform(0, size_m)
            xi = min(int(x / step), hm_res - 2)
            zi = min(int(z / step), hm_res - 2)
            h = float(heightmap[xi, zi])
            instance = base_mesh.copy()
            scale = rng.uniform(0.4, min(schema.vegetation.max_height / 4.5, 2.5))
            instance.apply_scale([scale, scale, scale])
            instance.apply_translation([x, h, z])
            instance.visual.vertex_colors = [34, 120, 72, 255]
            assets.append(MeshAsset(name=f"veg_{i}", mesh=instance, material="foliage", kind="vegetation"))
        return assets

    def _build_spline_mesh(self, spline: SplineRule, schema: WorldSchema) -> MeshAsset:
        line = LineString([(p[0], p[2]) for p in spline.control_points])
        length = line.length
        samples = max(12, int(length / 6))
        vertices: List[Tuple[float, float, float]] = []
        width = spline.width * 0.5

        coords = [line.interpolate(float(i) / samples, normalized=True).coords[0] for i in range(samples + 1)]
        for idx, (x, z) in enumerate(coords):
            if idx == 0:
                nx, nz = coords[idx + 1][0] - x, coords[idx + 1][1] - z
            else:
                nx, nz = x - coords[idx - 1][0], z - coords[idx - 1][1]
            length_vec = math.sqrt(nx * nx + nz * nz) + 1e-6
            nx, nz = -nz / length_vec, nx / length_vec  # perpendicular
            left = (x + nx * width, 0.0, z + nz * width)
            right = (x - nx * width, 0.0, z - nz * width)
            vertices.append(left)
            vertices.append(right)

        faces: List[Tuple[int, int, int]] = []
        for i in range(0, len(vertices) - 2, 2):
            faces.append((i, i + 1, i + 2))
            faces.append((i + 1, i + 3, i + 2))

        mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=False)
        mesh.visual.vertex_colors = [50, 50, 50, 255] if spline.kind == "road" else [32, 80, 160, 220]
        return MeshAsset(name=spline.name, mesh=mesh, material=spline.material, kind=spline.kind)

    def build(self, schema: WorldSchema, *, seed: int | None = None) -> WorldBuildResult:
        rng = random.Random(seed or schema.heightmap.seed)
        heightmap = self._generate_heightmap(schema)
        for spline in schema.splines:
            self._carve_spline(heightmap, schema, spline)

        terrain_mesh = self._build_terrain_mesh(heightmap, schema)
        meshes: List[MeshAsset] = [MeshAsset(name="terrain", mesh=terrain_mesh, material="terrain", kind="terrain")]

        size_m = schema.scale_km * 1000
        layout_objects: List[WorldLayoutObject] = []
        object_idx = 0
        for rule in schema.object_rules:
            for _ in range(rule.count):
                pos, scale = self._place_object(rule, size_m, rng)
                asset = self._make_structure(rule, pos, scale, object_idx)
                meshes.append(asset)
                layout_objects.append(
                    WorldLayoutObject(
                        name=asset.name,
                        position=(float(pos[0]), float(pos[1]), float(pos[2])),
                        scale=(float(scale[0]), float(scale[1]), float(scale[2])),
                        kind=asset.kind,
                        material=asset.material,
                    )
                )
                object_idx += 1

        spline_meshes = [self._build_spline_mesh(spline, schema) for spline in schema.splines]
        meshes.extend(spline_meshes)

        vegetation_assets = self._scatter_vegetation(schema, heightmap, rng)
        meshes.extend(vegetation_assets)

        layout = WorldLayout(
            terrain_bounds_m=(size_m, size_m),
            objects=layout_objects,
            splines=schema.splines,
            vegetation_count=len(vegetation_assets),
        )

        return WorldBuildResult(meshes=meshes, heightmap=heightmap, layout=layout)
