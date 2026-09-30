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

LOG_SCOPE = "Projection Bake"


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

        with LOG.scope(LOG_SCOPE):
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
                        bvh.isolated_test(source)

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
                    reverse_direction=True,
                )

                hit = None

                for bvh in bvh_services:
                    if x == width // 2 and y == height // 2:
                        nearest_position, nearest_normal, nearest_index, nearest_distance = bvh._bvh.find_nearest(
                            ray.origin,
                            ray.max_distance if ray.max_distance > 0 else float("inf"),
                        )

                        LOG.info(
                            "NEAREST DEBUG\n"
                            f"  origin   = {ray.origin}\n"
                            f"  nearest  = {nearest_position}\n"
                            f"  normal   = {nearest_normal}\n"
                            f"  distance = {nearest_distance}\n"
                        )
                        to_nearest = (nearest_position - ray.origin).normalized()

                        dot = ray.direction.dot(to_nearest)

                        LOG.info(f"Ray alignment with nearest geometry: {dot:.4f}")

                        print(bvh.diagnose_ray(ray))

                    hit = bvh.ray_cast(
                        ray.origin,
                        ray.direction,
                        ray.max_distance,
                    )

                    if hit is not None and hit.distance is not None:
                        break

                if x == width // 2 and y == height // 2:
                    ray_end = ray.origin + ray.direction * (ray.max_distance if ray.max_distance > 0 else 1.0)
                    LOG.debug(
                        f"Projection test:"
                        f"  pixel           = ({x}, {y})\n"
                        f"  cage_position   = {cage_position}\n"
                        f"  ray_origin      = {ray.origin}\n"
                        f"  ray_direction   = {ray.direction}\n"
                        f"  ray_max_distance= {ray.max_distance}\n"
                        f"  hit_position    = {hit.position if hit else None}\n"
                        f"  target_position = {projection.target_position}\n"
                        f"  cage_distance   = {projection.cage_distance}\n"
                        f"  cage_dir        = {projection.cage_direction}\n"
                        f"  ray_end         = {ray_end}"
                    )

                pixel = pixels[y, x]

                if hit is None or hit.distance is None:
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

        return buffer
