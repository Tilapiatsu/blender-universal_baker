from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(frozen=True, slots=True)
class UvTriangle:
    """
    A triangle in UV space together with its source mesh identity.

    UV coordinates are stored per loop/corner, while vertex_indices identify
    the corresponding mesh vertices. polygon_index identifies the original
    Blender polygon from which this triangle was generated.
    """

    index: int
    polygon_index: int
    vertex_indices: tuple[int, int, int]

    uv0: tuple[float, float]
    uv1: tuple[float, float]
    uv2: tuple[float, float]


@dataclass(frozen=True, slots=True)
class UvMesh:
    """
    Blender-independent representation of a mesh in UV space.

    The triangles are already triangulated and contain enough information
    to reconstruct vertex-based data later.
    """

    triangles: tuple[UvTriangle, ...]


class UvMeshExtractor:
    """
    Converts a Blender Mesh into the lightweight UvMesh representation.

    Blender UV coordinates are stored per loop rather than per vertex.
    Therefore UVs are read from polygon.loop_indices while vertex identity
    comes from the corresponding mesh loop.
    """

    def extract(
        self,
        mesh: bpy.types.Mesh,
        uv_layer_name: str,
    ) -> UvMesh:
        uv_layer = mesh.uv_layers.get(uv_layer_name)

        if uv_layer is None:
            raise ValueError(f"UV map '{uv_layer_name}' does not exist on mesh '{mesh.name}'.")

        triangles: list[UvTriangle] = []
        triangle_index = 0

        for polygon in mesh.polygons:
            loop_indices = polygon.loop_indices

            if len(loop_indices) < 3:
                continue

            # Blender polygons can contain more than three vertices.
            #
            # We use a fan:
            #
            #       0 -------- 1
            #       |        / |
            #       |      /   |
            #       |    /     |
            #       |  /       |
            #       3 -------- 2
            #
            # becomes:
            #
            #       0 -------- 1
            #       |       / |
            #       |     /   |
            #       |   /     |
            #       | /       |
            #       3 -------- 2
            #
            #       (0, 1, 2)
            #       (0, 2, 3)

            first_loop_index = loop_indices[0]

            for i in range(1, len(loop_indices) - 1):
                second_loop_index = loop_indices[i]
                third_loop_index = loop_indices[i + 1]

                first_loop = mesh.loops[first_loop_index]
                second_loop = mesh.loops[second_loop_index]
                third_loop = mesh.loops[third_loop_index]

                uv0 = tuple(uv_layer.data[first_loop_index].uv)
                uv1 = tuple(uv_layer.data[second_loop_index].uv)
                uv2 = tuple(uv_layer.data[third_loop_index].uv)

                triangles.append(
                    UvTriangle(
                        index=triangle_index,
                        polygon_index=polygon.index,
                        vertex_indices=(
                            first_loop.vertex_index,
                            second_loop.vertex_index,
                            third_loop.vertex_index,
                        ),
                        uv0=(float(uv0[0]), float(uv0[1])),
                        uv1=(float(uv1[0]), float(uv1[1])),
                        uv2=(float(uv2[0]), float(uv2[1])),
                    )
                )

                triangle_index += 1

        return UvMesh(
            triangles=tuple(triangles),
        )
