"""End-to-end world generation orchestrator."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.prompt_service import generate_design_spec
from app.schemas import (
    GenerateWorldRequest,
    GenerateWorldResponse,
    WorldMetadata,
)
from app.world_service import generate_world_schema
from core.mesh_exporter import MeshExporter
from core.procedural_engine import ProceduralEngine

logger = logging.getLogger(__name__)


class WorldGenerator:
    def __init__(self, export_root: Path | str = "exports") -> None:
        self.engine = ProceduralEngine()
        self.exporter = MeshExporter(export_root)

    def generate(self, request: GenerateWorldRequest) -> GenerateWorldResponse:
        seed = request.seed or int(datetime.utcnow().timestamp())
        design = generate_design_spec(request.description, seed=seed)
        schema = generate_world_schema(design, seed=seed)

        build = self.engine.build(schema, seed=seed)
        metadata = WorldMetadata(design=design, schema=schema, layout=build.layout)

        run_id = f"world_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        export = self.exporter.export(build, metadata, run_id)

        return GenerateWorldResponse(
            world_path=str(export.world_path),
            preview_image=str(export.preview_image),
            unity_import=str(export.unity_import),
            metadata=metadata,
        )


world_generator = WorldGenerator()
