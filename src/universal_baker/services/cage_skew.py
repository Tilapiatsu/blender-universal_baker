from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass

import bpy
import numpy as np
from mathutils import Matrix, Vector

from ..constant import LOG
from .skew_field import SkewField
from .temp_object import TempObject

LOG_SCOPE = "Custom Cage Builder"


@dataclass(slots=True)
class CustomCagePair:
    proxy: TempObject
    cage: TempObject


@dataclass(slots=True)
class _CornerMesh:
    positions: np.ndarray
    polygons: list[list[int]]
    uv_layers: dict[str, np.ndarray]

    # Evaluated corner/shading normals.
    corner_normals: np.ndarray

    # Geometric polygon normals, expanded once per loop.
    face_normals: np.ndarray

    material_indices: list[int]
    use_smooth: list[bool]


class SkewCageBuilder:
    """
    Builds a loop-expanded proxy/cage pair.

    Every original mesh loop becomes one independent vertex. This gives each
    face corner its own cage position, allowing a face-specific projection
    direction even when the original low-poly mesh has shared vertices.

    The generated cage geometry encodes the desired ray direction. Blender's
    native custom-cage bake then performs the actual ray casting and shader
    evaluation.
    """

    def build(
        self,
        target_object: bpy.types.Object,
        cage_object: bpy.types.Object,
        skew_image: bpy.types.Image,
        uv_layer_name: str,
        cage_extrusion: float,
    ) -> CustomCagePair:
        with LOG.scope(LOG_SCOPE), self._ensure_in_scene(target_object), self._ensure_in_scene(cage_object):
            bpy.context.view_layer.update()

            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated_target = target_object.evaluated_get(depsgraph)
            evaluated_cage = cage_object.evaluated_get(depsgraph)

            target_mesh = evaluated_target.to_mesh()
            cage_mesh = evaluated_cage.to_mesh()

            target_matrix = evaluated_target.matrix_world.copy()
            cage_matrix = evaluated_cage.matrix_world.copy()

            try:
                self._validate_topology(target_mesh, cage_mesh)

                target_corners = self._extract_corner_mesh(target_mesh)
                cage_corners = self._extract_corner_mesh(cage_mesh)

                # The original cage may have a different object transform.
                # Convert cage positions into the low object's local space before
                # calculating the projection vectors.
                cage_to_low = evaluated_target.matrix_world.inverted_safe() @ evaluated_cage.matrix_world

                cage_positions = np.empty_like(cage_corners.positions)

                for index, position in enumerate(cage_corners.positions):
                    cage_positions[index] = (cage_to_low @ Vector(position))[:]

                # The proxy uses the evaluated low geometry directly.
                proxy = self._create_mesh_object(
                    name=f"{target_object.name}_UBK_PROXY",
                    corners=target_corners,
                    positions=target_corners.positions,
                    matrix_world=target_matrix,
                )

                skew_field = SkewField.from_image(
                    skew_image,
                    channel=0,
                )

                skew_factors = skew_field.sample(target_corners.uv_layers[uv_layer_name])

                # Build the actual skewed cage from the proxy geometry.
                generated_cage_positions = self._build_cage_geometry(
                    target_positions=target_corners.positions,
                    original_cage_positions=cage_positions,
                    face_normals=target_corners.face_normals,
                    skew_factors=skew_factors,
                    cage_extrusion=cage_extrusion,
                )

                proxy_cage = self._create_mesh_object(
                    name=f"{target_object.name}_UBK_CAGE",
                    corners=target_corners,
                    positions=generated_cage_positions,
                    matrix_world=cage_matrix,
                )

                self._copy_material_slots(target_object, proxy)
                self._copy_material_slots(target_object, proxy_cage)

                proxy_cage.hide_render = True

                return CustomCagePair(
                    proxy=TempObject(proxy, target_object, cleanup=True),
                    cage=TempObject(proxy_cage, cage_object, cleanup=True),
                )
            finally:
                evaluated_target.to_mesh_clear()
                evaluated_cage.to_mesh_clear()

    @contextmanager
    def _ensure_in_scene(self, obj: bpy.types.Object):
        linked_to_scene = False

        try:
            if obj.name not in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.link(obj)
                linked_to_scene = True

            yield

        finally:
            if linked_to_scene:
                bpy.context.scene.collection.objects.unlink(obj)

    @staticmethod
    def _validate_topology(
        target_mesh: bpy.types.Mesh,
        cage_mesh: bpy.types.Mesh,
    ) -> None:
        if len(target_mesh.polygons) != len(cage_mesh.polygons):
            raise ValueError("Custom cage must have the same polygon count as the target mesh.")

        if len(target_mesh.loops) != len(cage_mesh.loops):
            raise ValueError("Custom cage must have the same loop count as the  mesh.")

        for low_poly, cage_poly in zip(
            target_mesh.polygons,
            cage_mesh.polygons,
        ):
            if low_poly.loop_total != cage_poly.loop_total:
                raise ValueError("Custom cage polygon loop topology does not match the low mesh.")

    @staticmethod
    def _extract_corner_mesh(
        mesh: bpy.types.Mesh,
    ) -> _CornerMesh:
        """
        Expand the mesh so every loop/corner owns one vertex.

        Crucially, geometric polygon normals and evaluated corner normals are
        kept as two different pieces of data:

        - face_normals:
            polygon.normal, repeated for every loop of that polygon.
            These define the face-perpendicular cage direction.

        - corner_normals:
            mesh.corner_normals[loop_index].
            These describe the low mesh's actual evaluated shading normals
            and are retained independently for future proxy/tangent handling.
        """

        loop_count = len(mesh.loops)

        positions = np.zeros((loop_count, 3), dtype=np.float64)
        corner_normals = np.zeros((loop_count, 3), dtype=np.float64)
        face_normals = np.zeros((loop_count, 3), dtype=np.float64)

        for loop_index, loop in enumerate(mesh.loops):
            positions[loop_index] = mesh.vertices[loop.vertex_index].co

            # Evaluated corner normal.
            value = mesh.corner_normals[loop_index]
            corner_normals[loop_index] = value.vector

        polygons: list[list[int]] = []
        material_indices: list[int] = []

        for polygon in mesh.polygons:
            polygon_loops = list(
                range(
                    polygon.loop_start,
                    polygon.loop_start + polygon.loop_total,
                )
            )

            polygons.append(polygon_loops)
            material_indices.append(polygon.material_index)

            # IMPORTANT:
            # Use the geometric polygon normal here, NOT the corner normal.
            #
            # Every corner belonging to this polygon receives exactly the
            # same face normal. This is what makes the generated cage
            # perpendicular to the individual face.
            polygon_normal = np.asarray(
                polygon.normal,
                dtype=np.float64,
            )

            for loop_index in polygon_loops:
                face_normals[loop_index] = polygon_normal

        use_smooth = [polygon.use_smooth for polygon in mesh.polygons]

        uv_layers: dict[str, np.ndarray] = {}

        for uv_layer in mesh.uv_layers:
            uv = np.zeros((loop_count, 2), dtype=np.float64)

            for loop_index, uv_data in enumerate(uv_layer.data):
                uv[loop_index] = uv_data.uv

            uv_layers[uv_layer.name] = uv

        return _CornerMesh(
            positions=positions,
            polygons=polygons,
            uv_layers=uv_layers,
            corner_normals=corner_normals,
            face_normals=face_normals,
            material_indices=material_indices,
            use_smooth=use_smooth,
        )

    @classmethod
    def _build_cage_geometry(
        cls,
        target_positions: np.ndarray,
        original_cage_positions: np.ndarray,
        face_normals: np.ndarray,
        skew_factors: np.ndarray,
        cage_extrusion: float,
    ) -> np.ndarray:
        """
        Generate cage positions whose cage->target direction is:

            normalize(
                lerp(
                    original_cage_to_target,
                    face_normal,
                    skew_factor,
                )
            )

        Blender's native custom-cage baker then casts from the generated
        cage point toward the corresponding target point.

        Therefore the generated geometry itself encodes the desired
        projection direction.
        """

        distance_scale = max(
            float(cage_extrusion),
            0.0,
        )

        delta = target_positions - original_cage_positions
        distances = np.linalg.norm(delta, axis=1)
        original_directions = np.zeros_like(delta)
        valid_original = distances > 1.0e-8
        original_directions[valid_original] = delta[valid_original] / distances[valid_original, None]

        # Normalize the geometric face normals defensively.
        normal_lengths = np.linalg.norm(face_normals, axis=1)
        normalized_face_normals = np.zeros_like(face_normals)
        valid_normals = normal_lengths > 1.0e-8
        normalized_face_normals[valid_normals] = face_normals[valid_normals] / normal_lengths[valid_normals, None]

        # Preserve the original cage direction when skew = 0.
        directions = cls._blend_directions(
            original_directions,
            normalized_face_normals,
            skew_factors,
        )

        direction_lengths = np.linalg.norm(directions, axis=1)
        valid_directions = direction_lengths > 1.0e-8
        normalized_directions = np.zeros_like(directions)
        normalized_directions[valid_directions] = (
            directions[valid_directions] / direction_lengths[valid_directions, None]
        )

        # Degenerate interpolation can occur when the original cage
        # direction and face normal are exact opposites. Fall back to the
        # original cage direction rather than producing a zero vector.
        fallback = ~valid_directions & valid_original

        normalized_directions[fallback] = original_directions[fallback]

        # If both directions are unavailable, fall back to the face normal.
        fallback_normal = ~valid_directions & ~valid_original & valid_normals
        normalized_directions[fallback_normal] = normalized_face_normals[fallback_normal]

        # Preserve the original cage distance independently from skew.
        #
        # C' = P - D * distance
        #
        # Blender's custom cage implementation then reconstructs:
        #
        # C' -> P = D * distance
        #
        # and normalizes that vector for the ray direction.

        generated = target_positions - normalized_directions * distance_scale

        return generated

    @staticmethod
    def _blend_directions(
        original_directions: np.ndarray,
        face_normals: np.ndarray,
        skew_factors: np.ndarray,
    ) -> np.ndarray:
        """
        Blend original cage directions toward geometric face normals.

        skew = 0: original cage direction
        skew = 1: geometric face normal
        """

        factors = np.clip(
            np.asarray(skew_factors, dtype=np.float32),
            0.0,
            1.0,
        )[:, None]

        directions = original_directions * (1.0 - factors) - face_normals * factors

        lengths = np.linalg.norm(directions, axis=1)

        valid = lengths > 1.0e-8

        result = np.zeros_like(directions)

        result[valid] = directions[valid] / lengths[valid, None]

        # If the directions cancel each other out, retain the original
        # direction rather than creating a zero-length ray.
        result[~valid] = original_directions[~valid]

        return result

    @staticmethod
    def _create_mesh_object(
        name: str,
        corners: _CornerMesh,
        positions: np.ndarray,
        matrix_world: Matrix,
    ) -> bpy.types.Object:
        mesh = bpy.data.meshes.new(name)

        vertices = [tuple(position) for position in positions]

        faces = [tuple(loop_indices) for loop_indices in corners.polygons]

        mesh.from_pydata(
            vertices,
            [],
            faces,
            shade_flat=False,
        )
        mesh.update()

        # Restore polygon shading flags.
        for polygon_index, use_smooth in enumerate(corners.use_smooth):
            mesh.polygons[polygon_index].use_smooth = use_smooth

        # Restore the original evaluated corner normals.
        mesh.normals_split_custom_set([tuple(normal) for normal in corners.corner_normals])

        # Restore UV data by loop index. Since this mesh is loop-expanded,
        # each loop corresponds directly to one generated vertex.
        for uv_name, uv_values in corners.uv_layers.items():
            uv_layer = mesh.uv_layers.new(name=uv_name)

            for loop_index, uv in enumerate(uv_values):
                uv_layer.data[loop_index].uv = tuple(uv)

        for polygon_index, material_index in enumerate(corners.material_indices):
            mesh.polygons[polygon_index].material_index = material_index

        obj = bpy.data.objects.new(name, mesh)

        obj.matrix_world = matrix_world

        LOG.debug(f"Proxy Object Created : {name}")

        return obj

    @staticmethod
    def _copy_material_slots(
        source: bpy.types.Object,
        destination: bpy.types.Object,
    ) -> None:
        for material in source.data.materials:
            destination.data.materials.append(material)
