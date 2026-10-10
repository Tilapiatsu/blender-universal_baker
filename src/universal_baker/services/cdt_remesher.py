import random

import bpy
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

from ..constant import LOG

LOG_SCOPE = "CDT Remesher"


class CDTRemesher:
    """
    Builds a triangulated duplicate.

    Density is target sample spacing in centimeters, measured in world space.
    The source mesh datablock is never modified.
    """

    def __init__(self, obj, spacing_cm=10.0, seed=1, preserve_custom_normals=True, link_to_collection=False):
        if obj is None or obj.type != "MESH":
            raise TypeError("Active object must be a mesh.")
        if spacing_cm <= 0:
            raise ValueError("Spacing must be greater than zero.")

        self.obj = obj
        self.mesh = obj.data
        # Convert centimeters to Blender world units using the current scene's
        # unit scale. With scale_length=1.0, 1 BU corresponds to 1 meter.
        unit_scale = bpy.context.scene.unit_settings.scale_length or 1.0
        self.spacing_world = (spacing_cm * 0.01) / unit_scale
        self.seed = seed
        self.preserve_custom_normals = preserve_custom_normals
        self.rng = random.Random(seed)
        self.link_to_collection = link_to_collection

    def build(self):
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Remeshing {self.obj.name}")
            src = self.mesh
            src.calc_loop_triangles()

            # Snapshot all original local and world positions. The source is untouched.
            original_local = [v.co.copy() for v in src.vertices]
            matrix_world = self.obj.matrix_world.copy()
            inverse_world = matrix_world.inverted_safe()
            original_world = [matrix_world @ co for co in original_local]

            # Cache source corner normals by loop index. New corners will receive
            # interpolated normals from their source triangle.
            try:
                src_corner_normals = [loop.normal.copy() for loop in src.loops]
            except Exception:
                src_corner_normals = [Vector((0, 0, 1)) for _ in src.loops]

            # Each output vertex is either an original vertex or an interior sample.
            # Start with every original vertex so original coordinates/indices survive.
            out_local = [co.copy() for co in original_local]
            out_faces = []
            out_face_materials = []
            out_face_smooth = []
            out_corner_normals = []

            # for edge in src.loop_edges:

            # Existing triangle edges are used as per-triangle constraints.
            # This also means the existing polygon tessellation is retained as a
            # piecewise-planar surface for non-planar n-gons.
            for tri in src.loop_triangles:
                source_vertex_ids = list(tri.vertices)
                source_loop_ids = list(tri.loops)

                p0, p1, p2 = [original_world[i] for i in source_vertex_ids]
                basis = self._triangle_basis(p0, p1, p2)
                if basis is None:
                    continue
                project, unproject = basis

                tri_2d = [project(p0), project(p1), project(p2)]

                # Ensure the triangle boundary is counter-clockwise in the local
                # 2D plane, while keeping loop/vertex associations consistent.
                if self._cross_2d(*tri_2d) < 0:
                    source_vertex_ids[1], source_vertex_ids[2] = source_vertex_ids[2], source_vertex_ids[1]
                    source_loop_ids[1], source_loop_ids[2] = source_loop_ids[2], source_loop_ids[1]
                    p0, p1, p2 = [original_world[i] for i in source_vertex_ids]
                    basis = self._triangle_basis(p0, p1, p2)
                    project, unproject = basis
                    tri_2d = [project(p0), project(p1), project(p2)]

                # Interior samples are distributed in world-space distance units.
                samples_world = self._sample_triangle_poissonish(p0, p1, p2, self.spacing_world, self.rng)
                samples_2d = [project(p) for p in samples_world]

                # CDT input indices 0..2 correspond to the triangle's original
                # vertices; indices 3+ correspond to generated interior samples.
                cdt_verts_in = [Vector((p[0], p[1])) for p in tri_2d]
                cdt_verts_in.extend(Vector((p[0], p[1])) for p in samples_2d)
                cdt_edges_in = [(0, 1), (1, 2), (2, 0)]
                cdt_faces_in = [(0, 1, 2)]

                try:
                    cdt_verts, _cdt_edges, cdt_faces, orig_verts, _orig_edges, _orig_faces = delaunay_2d_cdt(
                        cdt_verts_in,
                        cdt_edges_in,
                        cdt_faces_in,
                        1,  # triangles inside constraints
                        1e-9,
                        True,
                    )
                except Exception as exc:
                    raise RuntimeError(
                        f"Constrained triangulation failed for source triangle {tuple(tri.vertices)}: {exc}"
                    ) from exc

                # Map CDT output vertices to output mesh vertices. Original triangle
                # corners map to the exact original mesh vertex index. Other points
                # are mapped back to the triangle plane and then to object-local space.
                local_map = {}
                for out_i, coord2d in enumerate(cdt_verts):
                    source_ids = orig_verts[out_i] if out_i < len(orig_verts) else []
                    input_id = source_ids[0] if source_ids else None

                    if input_id is not None and input_id in (0, 1, 2):
                        local_map[out_i] = source_vertex_ids[input_id]
                        continue

                    # CDT should not create intersections for this simple input.
                    # If it does, reconstruct the point from its 2D coordinate.
                    world_co = unproject(Vector((coord2d[0], coord2d[1])))
                    local_co = inverse_world @ world_co
                    local_map[out_i] = len(out_local)
                    out_local.append(local_co)

                # Source triangle's corner normals correspond to source_loop_ids.
                n0, n1, n2 = [src_corner_normals[i].copy() for i in source_loop_ids]
                # World coordinates are projected onto this triangle plane. Compute
                # barycentric weights for interpolating the original corner normals.
                a2, b2, c2 = tri_2d
                denom = self._cross_2d(a2, b2, c2)
                material_index = src.polygons[tri.polygon_index].material_index
                smooth = src.polygons[tri.polygon_index].use_smooth

                for cdt_face in cdt_faces:
                    if len(cdt_face) != 3:
                        continue

                    face = [local_map[i] for i in cdt_face]
                    if len(set(face)) != 3:
                        continue

                    # Reject any degenerate output triangles.
                    q0 = Vector(cdt_verts[cdt_face[0]])
                    q1 = Vector(cdt_verts[cdt_face[1]])
                    q2 = Vector(cdt_verts[cdt_face[2]])
                    if abs(self._cross_2d(q0, q1, q2)) < 1e-12:
                        continue

                    out_faces.append(face)
                    out_face_materials.append(material_index)
                    out_face_smooth.append(smooth)

                    for output_vertex_index in cdt_face:
                        q = Vector(cdt_verts[output_vertex_index])
                        if abs(denom) > 1e-15:
                            w0 = self._cross_2d(q, b2, c2) / denom
                            w1 = self._cross_2d(a2, q, c2) / denom
                            w2 = self._cross_2d(a2, b2, q) / denom
                            n = n0 * w0 + n1 * w1 + n2 * w2
                            if n.length_squared > 1e-20:
                                n.normalize()
                            else:
                                n = Vector((0, 0, 1))
                        else:
                            n = n0.copy()
                        out_corner_normals.append(n)

            # Preserve original loose edges that are not already represented by faces.
            face_edge_keys = set()
            for face in out_faces:
                for i, a in enumerate(face):
                    b = face[(i + 1) % len(face)]
                    face_edge_keys.add((min(a, b), max(a, b)))

            loose_edges = []
            for edge in src.edges:
                a, b = edge.vertices
                key = (min(a, b), max(a, b))
                if key not in face_edge_keys:
                    loose_edges.append((a, b))

            new_mesh = bpy.data.meshes.new(f"{src.name}_remeshed")
            new_mesh.from_pydata(out_local, loose_edges, out_faces)
            new_mesh.update()

            # Assign face-level material and smooth-shading flags in the same order
            # as the faces supplied to from_pydata().
            for i, poly in enumerate(new_mesh.polygons):
                if i < len(out_face_materials):
                    poly.material_index = out_face_materials[i]
                    poly.use_smooth = out_face_smooth[i]

            # Copy material slots.
            for material in src.materials:
                new_mesh.materials.append(material)

            # Restore custom split/corner normals when possible. Blender versions
            # differ in how custom normals are exposed, so fail gracefully.
            if self.preserve_custom_normals and len(out_corner_normals) == len(new_mesh.loops):
                try:
                    new_mesh.normals_split_custom_set(out_corner_normals)
                except Exception:
                    pass

            # Copy UV maps and attributes where the domains/counts still match.
            # This prototype deliberately does not attempt to interpolate arbitrary
            # attributes yet; doing so needs source-triangle provenance for each output
            # corner/point and domain-specific interpolation rules.
            for src_uv in src.uv_layers:
                dst_uv = new_mesh.uv_layers.new(name=src_uv.name)
                if len(src_uv.data) == len(dst_uv.data):
                    for i, item in enumerate(src_uv.data):
                        dst_uv.data[i].uv = item.uv

            # Blender 4.1+ uses sharp edges and custom corner normals rather than
            # the removed Mesh.use_auto_smooth toggle.

            new_obj = self.obj.copy()
            new_obj.data = new_mesh
            new_obj.name = f"{self.obj.name}_remeshed"
            new_obj.matrix_world = matrix_world
            new_obj.animation_data_clear()

            if self.link_to_collection:
                # Link duplicate to the same collections as the source.
                for collection in self.obj.users_collection:
                    collection.objects.link(new_obj)

            return new_obj

    @staticmethod
    def _cross_2d(a, b, c):
        """Twice the signed area of triangle ABC in 2D."""
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    @classmethod
    def _point_in_triangle_2d(cls, p, a, b, c, eps=1e-10):
        c1 = cls._cross_2d(a, b, p)
        c2 = cls._cross_2d(b, c, p)
        c3 = cls._cross_2d(c, a, p)
        return (c1 >= -eps and c2 >= -eps and c3 >= -eps) or (c1 <= eps and c2 <= eps and c3 <= eps)

    @staticmethod
    def _sample_triangle_poissonish(a, b, c, spacing, rng, attempts_factor=24):
        """
        Approximate Poisson-disk samples inside one triangle.

        This deliberately simple first prototype uses rejection sampling with a
        minimum-distance check. It is not a full Bridson sampler, and samples are
        generated independently per source triangle.
        """
        ab = (b - a).length
        bc = (c - b).length
        ca = (a - c).length
        area = 0.5 * (b - a).cross(c - a).length

        if area <= 1e-14 or spacing <= 0:
            return []

        # Approximate number of interior samples for triangular packing.
        target = max(0, int(area / (0.866025403784 * spacing * spacing)))
        if target == 0:
            return []

        # Generate uniform random points in a triangle using reflected barycentrics.
        samples = []
        max_attempts = max(target * attempts_factor, 80)
        min_dist_sq = spacing * spacing

        for _ in range(max_attempts):
            if len(samples) >= target:
                break

            u = rng.random()
            v = rng.random()
            if u + v > 1.0:
                u = 1.0 - u
                v = 1.0 - v

            p = a + (b - a) * u + (c - a) * v

            # Keep a margin from triangle boundaries. This avoids generating
            # nearly duplicate vertices on shared source edges.
            edge_margin = min(
                (p - a).cross(b - a).length / max(ab, 1e-12),
                (p - b).cross(c - b).length / max(bc, 1e-12),
                (p - c).cross(a - c).length / max(ca, 1e-12),
            )
            if edge_margin < spacing * 0.08:
                continue

            if all((p - q).length_squared >= min_dist_sq for q in samples):
                samples.append(p)

        return samples

    @staticmethod
    def _triangle_basis(p0, p1, p2):
        """Return a stable 2D basis for a non-degenerate 3D triangle."""
        e1 = p1 - p0
        if e1.length_squared < 1e-20:
            return None

        x_axis = e1.normalized()
        normal = e1.cross(p2 - p0)
        if normal.length_squared < 1e-20:
            return None

        normal.normalize()
        y_axis = normal.cross(x_axis).normalized()

        def project(p):
            d = p - p0
            return (d.dot(x_axis), d.dot(y_axis))

        def unproject(p2d):
            return p0 + x_axis * p2d[0] + y_axis * p2d[1]

        return project, unproject
