from __future__ import annotations

import bpy

from ..constant import LOG
from ..resources.image_buffer import ImageBuffer
from .bvh_high_poly import HighPolyBVHService
from .cage_projection import CageProjectionService
from .cage_surface import CageSurfaceSampler
from .projection_ray import ProjectionRayBuilder
from .uv_mesh import UvMeshExtractor
from .uv_rasterizer import UvRasterization, UvRasterizer
from .uv_surface import UvSurfaceSampler


class ProjectionBakeService:
    def __init__(self) -> None:
        self._uv_mesh_extractor = UvMeshExtractor()
        self._uv_rasterizer = UvRasterizer()
        self._cage_projection = CageProjectionService()
        self._projection_ray = ProjectionRayBuilder()

    def bake(
        self,
        *,
        target: bpy.types.Object,
        cage: bpy.types.Object,
        sources: list[bpy.types.Object],
        uv_layer_name: str,
        width: int,
        height: int,
        max_ray_distance: float,
        depsgraph: bpy.types.Depsgraph,
    ) -> ImageBuffer:

        if not sources:
            raise ValueError("Projection baking requires at least one source object.")

        # --------------------------------------------------------------
        # Target UV representation
        # --------------------------------------------------------------

        target_evaluated = target.evaluated_get(depsgraph)
        target_mesh = target_evaluated.to_mesh()

        try:
            uv_mesh = self._uv_mesh_extractor.extract(
                target_mesh,
                uv_layer_name,
            )

            rasterization = self._uv_rasterizer.rasterize(
                uv_mesh,
                width,
                height,
            )

            target_sampler = UvSurfaceSampler(
                mesh=target_mesh,
                uv_mesh=uv_mesh,
                matrix_world=target_evaluated.matrix_world,
            )

            # ----------------------------------------------------------
            # Cage
            # ----------------------------------------------------------

            cage_evaluated = cage.evaluated_get(depsgraph)
            cage_mesh = cage_evaluated.to_mesh()

            try:
                cage_sampler = CageSurfaceSampler(
                    mesh=cage_mesh,
                    uv_mesh=uv_mesh,
                    matrix_world=cage_evaluated.matrix_world,
                )

                # ------------------------------------------------------
                # Build source BVHs.
                # ------------------------------------------------------

                bvh_services = []

                for source in sources:
                    bvh = HighPolyBVHService()
                    bvh.build(
                        source,
                        depsgraph,
                    )
                    bvh_services.append(bvh)

                try:
                    return self._rasterize_projection(
                        rasterization=rasterization,
                        target_sampler=target_sampler,
                        cage_sampler=cage_sampler,
                        bvh_services=bvh_services,
                        max_ray_distance=max_ray_distance,
                        width=width,
                        height=height,
                    )

                finally:
                    for bvh in bvh_services:
                        bvh.clear()

            finally:
                cage_evaluated.to_mesh_clear()

        finally:
            target_evaluated.to_mesh_clear()

    def _rasterize_projection(
        self,
        *,
        rasterization: UvRasterization,
        target_sampler: UvSurfaceSampler,
        cage_sampler: CageSurfaceSampler,
        bvh_services: list[HighPolyBVHService],
        max_ray_distance: float,
        width: int,
        height: int,
    ) -> ImageBuffer:

        buffer = ImageBuffer.empty(
            width=width,
            height=height,
            channels=4,
            name="Projection Diagnostic",
        )

        pixels = buffer.pixels

        projection_service = self._cage_projection
        ray_builder = self._projection_ray

        for y in range(height):
            for x in range(width):
                target_sample = target_sampler.sample(
                    rasterization,
                    x,
                    y,
                )

                if target_sample is None:
                    continue

                cage_position = cage_sampler.sample(
                    rasterization,
                    x,
                    y,
                )

                if cage_position is None:
                    continue

                projection = projection_service.create_projection(
                    target_sample,
                    cage_position,
                )

                ray = ray_builder.build(
                    projection,
                    max_distance=max_ray_distance,
                    reverse=False,
                )

                hit = None
                LOG.info(
                    "RAY DEBUG\n"
                    f"  origin       = {ray.origin}\n"
                    f"  direction    = {ray.direction}\n"
                    f"  max_distance = {ray.max_distance}\n"
                    f"  target       = {projection.target_position}\n"
                    f"  cage         = {projection.cage_distance}\n"
                    f"  cage_dir     = {projection.cage_direction}\n"
                )
                ray_end = ray.origin + ray.direction * (ray.max_distance if ray.max_distance > 0 else 1.0)

                LOG.info(f"  ray_end      = {ray_end}")

                for bvh in bvh_services:
                    hit = bvh.ray_cast(
                        ray.origin,
                        ray.direction,
                        ray.max_distance,
                    )

                    if hit is not None:
                        break

                pixel = pixels[y, x]

                if hit is None:
                    # Miss = transparent black.
                    pixel[0] = 0.0
                    pixel[1] = 0.0
                    pixel[2] = 0.0
                    pixel[3] = 0.0
                    continue

                # Arbitrary diagnostic normalization for now.
                distance = hit.distance
                distance_value = min(
                    distance
                    / max(
                        projection.cage_distance,
                        1e-6,
                    ),
                    1.0,
                )
                pixel[0] = distance_value
                pixel[1] = hit.normal.x * 0.5 + 0.5
                pixel[2] = hit.normal.z * 0.5 + 0.5
                pixel[3] = 1.0

                if x == width // 2 and y == height // 2:
                    LOG.debug(
                        f"Projection test:"
                        f" pixel=({x}, {y})"
                        f" target={target_sample.position}"
                        f" cage={cage_position}"
                        f" direction={ray.direction}"
                        f" max_distance={ray.max_distance}"
                        f" hit={hit.position if hit else None}"
                    )

        return buffer
