from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..constant import LOG
from ..runtime.runtime_visualization_cage import (
    CageVisualizationRuntime,
    ObjectVisibilityState,
)

if TYPE_CHECKING:
    from ..properties.object import UBK_TargetObject

LOG_SCOPE = "Cage Visualization"
TEMP_COLLECTION_NAME = "UBK_CAGE_VISUALIZATION"


def update_edit_cage(self, context):
    from ..core.controller import BakeController

    target = BakeController.active_target_object(context)
    project = BakeController.project(context)

    edit_cage = project.visualization.cage_edit

    if edit_cage:
        if target is None:
            edit_cage = False
            return

        if not CageVisualizationService.enable(target):
            edit_cage = False

    else:
        CageVisualizationService.disable()


def update_active_target(self, context):
    from ..core.controller import BakeController

    if not CageVisualizationService.is_active():
        return

    target = BakeController.active_target_object(context)

    if target is None:
        CageVisualizationService.disable()
        return

    CageVisualizationService.refresh(target)


class CageVisualizationError(RuntimeError):
    """Base exception for Cage Visualization errors."""


class CageVisualizationService:
    """
    Handles interactive visualization of a bake cage.

    Responsibilities:

        - acquire the cage
        - capture/restore visibility
        - show sources
        - hide targets
        - draw the cage through the GPU API
        - enter weight paint mode
        - refresh when the active target changes
        - restore Blender state on disable

    Collision detection is intentionally not part of MVP 1.
    """

    _runtime: CageVisualizationRuntime | None = None

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    SURFACE_COLOR = (
        0.05,
        0.65,
        1.0,
        0.20,
    )

    WIRE_COLOR = (
        0.05,
        0.65,
        1.0,
        0.25,
    )

    LINE_WIDTH = 2.0

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    @classmethod
    def _ensure_runtime(cls):
        if cls._runtime is None:
            from ..runtime.runtime_manager import RuntimeManager

            runtime = RuntimeManager.current(bpy.context)
            cls._runtime = runtime.cage_visualization

        return cls._runtime

    @classmethod
    def is_active(cls) -> bool:
        return cls._runtime is not None and cls._runtime.active

    @classmethod
    def runtime(cls) -> CageVisualizationRuntime | None:
        return cls._runtime

    # ---------------------------------------------------------
    # Enable
    # ---------------------------------------------------------

    @classmethod
    def enable(
        cls,
        target: UBK_TargetObject,
    ) -> bool:
        """
        Enable cage visualization for target.

        Returns False if the target cannot be visualized.
        """
        with LOG.scope(LOG_SCOPE):
            if target is None or target.object is None:
                LOG.warning("Cannot visualize cage: target object is missing")
                return False

            if not cls._target_uses_cage(target):
                LOG.debug(f"Cage visualization ignored for {target.object.name}: cage disabled")
                return False

            if cls.is_active():
                cls.disable()

            LOG.debug(f"Enabling Cage Visualization | {target.object.name}")

            runtime = cls._ensure_runtime()

            # -----------------------------------------------------
            # Acquire cage
            # -----------------------------------------------------

            cage = cls._acquire_cage(target)

            if cage is None:
                LOG.warning(f"Unable to acquire cage for {target.object.name}")
                return False

            runtime.begin(
                target_uuid=target.uuid,
                target_name=target.object.name,
                cage_name=cage.name,
            )

            try:
                cls._capture_state(target, cage)
                cls._create_temporary_collection()
                cls._link_visualization_objects(target, cage)
                cls._configure_visibility()
                cls._create_gpu_resources(cage)
                cls._register_draw_handler()
                cls._enter_weight_paint(cage)

                return True

            except Exception:
                raise CageVisualizationError("Failed to enable Cage Visualization")
                cls.disable()

                return False

    # ---------------------------------------------------------
    # Disable
    # ---------------------------------------------------------

    @classmethod
    def disable(cls) -> None:
        """
        Disable cage visualization and restore Blender state.

        This method is intentionally idempotent.
        """
        with LOG.scope("Disable"):
            runtime = cls._runtime

            if runtime is None or not runtime.active:
                return

            LOG.debug("Disabling Cage Visualization")

            try:
                cls._remove_draw_handler()
                cls._release_gpu_resources()
                cls._restore_mode_and_active_object()
                cls._restore_visibility()
                cls._cleanup_temporary_collection()

            except Exception:
                raise CageVisualizationError("Failed while restoring Cage Visualization")

            finally:
                runtime.clear()

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------
    @classmethod
    def refresh(
        cls,
        target: UBK_TargetObject | None,
    ) -> bool:
        """
        Refresh the cage visualization for a new active target.

        If the new target does not use a cage, visualization is
        disabled.
        """
        with LOG.scope("Refresh"):
            if not cls.is_active():
                if target is None:
                    return False

                return cls.enable(target)

            if target is None:
                cls.disable()
                return False

            if not cls._target_uses_cage(target):
                cls.disable()
                return False

            runtime = cls._ensure_runtime()

            if runtime.target_uuid == target.uuid:
                return True

            LOG.debug(f"Refreshing Cage Visualization | {runtime.target_name} -> {target.object.name}")

            # Do not call disable() here because that would restore
            # the original scene visibility between targets.
            cls._remove_draw_handler()
            cls._release_gpu_resources()

            cage = cls._acquire_cage(target)

            if cage is None:
                cls.disable()
                return False

            # Update runtime identity.
            runtime.target_uuid = target.uuid
            runtime.target_name = target.object.name
            runtime.cage_name = cage.name

            try:
                cls._configure_visibility()
                cls._create_gpu_resources(cage)
                cls._register_draw_handler()
                cls._enter_weight_paint(cage)

                return True

            except Exception:
                raise CageVisualizationError("Failed to refresh Cage Visualization")

                cls.disable()

                return False

    # ---------------------------------------------------------
    # Target
    # ---------------------------------------------------------

    @classmethod
    def _target_uses_cage(
        cls,
        target: UBK_TargetObject,
    ) -> bool:

        settings = target.settings_cage

        if settings is None:
            return False

        return settings.cage_mode != "NONE"

    @classmethod
    def _acquire_cage(
        cls,
        target: UBK_TargetObject,
    ) -> bpy.types.Object | None:
        """
        Delegate cage creation/retrieval entirely to CageObjectService.
        """

        from .cage_object import CageObjectService

        return CageObjectService.acquire(target)

    # ---------------------------------------------------------
    # State Capture
    # ---------------------------------------------------------

    @classmethod
    def _capture_state(
        cls,
        target,
        cage: bpy.types.Object,
    ) -> None:
        runtime = cls._ensure_runtime()

        active_object = bpy.context.view_layer.objects.active

        if active_object is not None:
            runtime.active_object_name = active_object.name
            runtime.active_object_mode = active_object.mode

        runtime.target_object_names.clear()
        runtime.source_object_names.clear()

        from ..core.controller import BakeController

        active_bake_group = BakeController.active_bake_group(bpy.context)
        if active_bake_group is None:
            raise CageVisualizationError("No active Bake group found")
            return

        target_objects = active_bake_group.target_objects

        # Capture target objects.
        for target_item in target_objects:
            obj = target_item.object

            if obj is None:
                continue

            runtime.target_object_names.append(obj.name)

            runtime.visibility[obj.name] = ObjectVisibilityState(
                name=obj.name,
                hide_viewport=obj.hide_viewport,
                hide_get=obj.hide_get(),
            )

        # Capture sources.
        for source in target.source_object_list:
            if source is None:
                continue

            runtime.source_object_names.append(source.name)

            if source.name not in runtime.visibility:
                runtime.visibility[source.name] = ObjectVisibilityState(
                    name=source.name,
                    hide_viewport=source.hide_viewport,
                    hide_get=source.hide_get(),
                )

        # Capture cage state too.
        if cage.name not in runtime.visibility:
            runtime.visibility[cage.name] = ObjectVisibilityState(
                name=cage.name,
                hide_viewport=cage.hide_viewport,
                hide_get=cage.hide_get(),
            )

    @classmethod
    def _get_group_targets(
        cls,
        target: UBK_TargetObject,
    ):

        from ..core.controller import BakeController

        group = BakeController.active_bake_group(bpy.context)

        if group is None:
            return [target]

        return group.target_objects

    # ---------------------------------------------------------
    # Visibility
    # ---------------------------------------------------------

    @classmethod
    def _configure_visibility(cls) -> None:
        runtime = cls._ensure_runtime()

        # The temporary collection is the visibility boundary for
        # visualization objects.
        collection = cls._get_temporary_collection()

        if collection is not None:
            collection.hide_viewport = False

        # Show sources.
        for name in runtime.source_object_names:
            obj = bpy.data.objects.get(name)

            if obj is None:
                continue

            obj.hide_viewport = False
            obj.hide_set(False)

        # Hide all target objects.
        for name in runtime.target_object_names:
            obj = bpy.data.objects.get(name)

            if obj is None:
                continue

            obj.hide_viewport = True
            obj.hide_set(True)

        # Cage must be visible and selectable for weight paint.
        if runtime.cage_name:
            cage = bpy.data.objects.get(runtime.cage_name)

            if cage is not None:
                cage.hide_viewport = False
                cage.hide_set(False)

    @classmethod
    def _restore_visibility(cls) -> None:
        runtime = cls._ensure_runtime()

        for state in runtime.visibility.values():
            obj = bpy.data.objects.get(state.name)

            if obj is None:
                continue

            obj.hide_viewport = state.hide_viewport
            obj.hide_set(state.hide_get)

    # ---------------------------------------------------------
    # Temporary Collection
    # ---------------------------------------------------------
    #
    @classmethod
    def _create_temporary_collection(cls) -> bpy.types.Collection:
        runtime = cls._ensure_runtime()

        collection = bpy.data.collections.new(TEMP_COLLECTION_NAME)

        # Link to the current scene collection.
        bpy.context.scene.collection.children.link(collection)

        runtime.temporary_collection_name = collection.name
        runtime.owns_temporary_collection = True

        return collection

    @classmethod
    def _get_temporary_collection(cls) -> bpy.types.Collection | None:
        runtime = cls._ensure_runtime()

        if not runtime.temporary_collection_name:
            return None

        return bpy.data.collections.get(runtime.temporary_collection_name)

    @classmethod
    def _link_object_to_temporary_collection(
        cls,
        obj: bpy.types.Object,
    ) -> None:
        runtime = cls._ensure_runtime()
        collection = cls._get_temporary_collection()

        if collection is None:
            return

        if obj.name in collection.objects:
            return

        collection.objects.link(obj)
        runtime.temporary_links.add(obj.name)

    @classmethod
    def _link_visualization_objects(
        cls,
        target,
        cage: bpy.types.Object,
    ) -> None:
        # Link cage.
        cls._link_object_to_temporary_collection(cage)

        # Link every source object belonging to the target.
        for source in target.source_object_list:
            if source is None:
                continue

            cls._link_object_to_temporary_collection(source)

    @classmethod
    def _cleanup_temporary_collection(cls) -> None:
        runtime = cls._ensure_runtime()

        if not runtime.owns_temporary_collection:
            return

        collection = cls._get_temporary_collection()

        if collection is None:
            return

        # Remove only the links that this service created.
        for object_name in runtime.temporary_links:
            obj = bpy.data.objects.get(object_name)

            if obj is None:
                continue

            if collection.objects.get(obj.name) is not None:
                collection.objects.unlink(obj)

        # Now the temporary collection should be empty.
        #
        # Since we created it ourselves, it is safe to remove.
        bpy.data.collections.remove(collection)

    # ---------------------------------------------------------
    # GPU
    # ---------------------------------------------------------

    @classmethod
    def _create_gpu_resources(
        cls,
        cage: bpy.types.Object,
    ) -> None:
        with LOG.scope("Create GPU Resources"):
            runtime = cls._ensure_runtime()

            mesh = cage.data

            if mesh is None:
                raise RuntimeError(f"Cage {cage.name} has no mesh")

            surface_shader = gpu.shader.from_builtin("SMOOTH_COLOR")
            wire_shader = gpu.shader.from_builtin("UNIFORM_COLOR")

            surface_positions = []

            mesh.calc_loop_triangles()

            for triangle in mesh.loop_triangles:
                for vertex_index in triangle.vertices:
                    vertex = mesh.vertices[vertex_index]

                    surface_positions.append(vertex.co.copy())

            surface_colors = [cls.SURFACE_COLOR for _ in surface_positions]

            surface_batch = batch_for_shader(
                surface_shader,
                "TRIS",
                {
                    "pos": surface_positions,
                    "color": surface_colors,
                },
            )

            # -----------------------------------------------------
            # Build wire batch
            # -----------------------------------------------------

            wire_positions = []

            for edge in mesh.edges:
                v1 = mesh.vertices[edge.vertices[0]].co
                v2 = mesh.vertices[edge.vertices[1]].co

                wire_positions.append(v1.copy())
                wire_positions.append(v2.copy())

            wire_batch = batch_for_shader(
                wire_shader,
                "LINES",
                {
                    "pos": wire_positions,
                },
            )

            runtime.surface_shader = surface_shader
            runtime.wire_shader = wire_shader

            runtime.surface_batch = surface_batch
            runtime.wire_batch = wire_batch

    @classmethod
    def _release_gpu_resources(cls) -> None:
        with LOG.scope("Release GPU Resources"):
            runtime = cls._runtime

            if runtime is None:
                return

            # GPU batches/shaders are Python-side references.
            # Clearing them allows Blender/GPU resources to be released.
            runtime.surface_batch = None
            runtime.wire_batch = None

            runtime.surface_shader = None
            runtime.wire_shader = None

    # ---------------------------------------------------------
    # Draw Handler
    # ---------------------------------------------------------

    @classmethod
    def _register_draw_handler(cls) -> None:
        with LOG.scope("Register Draw Handler"):
            runtime = cls._ensure_runtime()

            if runtime.draw_handler is not None:
                return

            runtime.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                cls._draw,
                (),
                "WINDOW",
                "POST_VIEW",
            )

    @classmethod
    def _remove_draw_handler(cls) -> None:
        with LOG.scope("Remove Draw Handler"):
            runtime = cls._runtime

            if runtime is None:
                return

            handler = runtime.draw_handler

            if handler is None:
                return

            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    handler,
                    "WINDOW",
                )

            except Exception:
                raise CageVisualizationError("Failed to remove cage draw handler")

            finally:
                runtime.draw_handler = None

    @classmethod
    def _draw(cls) -> None:
        with LOG.scope("Draw"):
            runtime = cls._runtime

            if runtime is None or not runtime.active:
                return

            cage_name = runtime.cage_name

            if cage_name is None:
                return

            cage = bpy.data.objects.get(cage_name)

            if cage is None:
                return

            surface_shader = runtime.surface_shader
            wire_shader = runtime.wire_shader

            surface_batch = runtime.surface_batch
            wire_batch = runtime.wire_batch

            if surface_shader is None or wire_shader is None or surface_batch is None or wire_batch is None:
                return

            # -----------------------------------------------------
            # Preserve GPU state
            # -----------------------------------------------------

            try:
                gpu.state.blend_set("ALPHA")

                # We want the cage to remain visible even when it
                # intersects/overlaps the source geometry.
                gpu.state.depth_test_set("LESS")
                gpu.state.face_culling_set("BACK")

                # -------------------------------------------------
                # Object transform
                # -------------------------------------------------

                gpu.matrix.push()

                gpu.matrix.multiply_matrix(cage.matrix_world)

                # -------------------------------------------------
                # Surface
                # -------------------------------------------------

                surface_shader.bind()

                surface_batch.draw(surface_shader)

                # -------------------------------------------------
                # Wire
                # -------------------------------------------------

                gpu.state.line_width_set(cls.LINE_WIDTH)

                wire_shader.bind()

                wire_shader.uniform_float(
                    "color",
                    cls.WIRE_COLOR,
                )

                wire_batch.draw(wire_shader)

                gpu.matrix.pop()

            finally:
                # -------------------------------------------------
                # Restore GPU state
                # -------------------------------------------------

                gpu.state.line_width_set(1.0)
                gpu.state.depth_test_set("LESS_EQUAL")
                gpu.state.blend_set("NONE")

    # ---------------------------------------------------------
    # Weight Paint
    # ---------------------------------------------------------

    @classmethod
    def _enter_weight_paint(
        cls,
        cage: bpy.types.Object,
    ) -> None:
        with LOG.scope("Enter Weight Paint"):
            # The actual cage object must be active even though
            # the GPU visualization is what the user sees.

            if bpy.context.mode != "OBJECT":
                try:
                    bpy.ops.object.mode_set(mode="OBJECT")
                except RuntimeError:
                    pass

            bpy.ops.object.select_all(action="DESELECT")

            cage.hide_set(False)
            cage.select_set(True)

            bpy.context.view_layer.objects.active = cage

            try:
                bpy.ops.object.mode_set(mode="WEIGHT_PAINT")

            except RuntimeError as exc:
                LOG.warning(f"Unable to enter Weight Paint mode for cage {cage.name}: {exc}")

    # ---------------------------------------------------------
    # Mode / Active Object restoration
    # ---------------------------------------------------------

    @classmethod
    def _restore_mode_and_active_object(cls) -> None:
        with LOG.scope("Restore mode and active object"):
            runtime = cls._runtime

            if runtime is None:
                return

            try:
                # Always leave Weight Paint first.
                if bpy.context.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")

            except RuntimeError:
                pass

            # Restore selection.
            bpy.ops.object.select_all(action="DESELECT")

            active_name = runtime.active_object_name

            if active_name is None:
                bpy.context.view_layer.objects.active = None
                return

            obj = bpy.data.objects.get(active_name)

            if obj is None:
                bpy.context.view_layer.objects.active = None
                return

            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Restore the previous mode where possible.
            previous_mode = runtime.active_object_mode

            if previous_mode != "OBJECT" and previous_mode in {
                "EDIT_MESH",
                "SCULPT",
                "VERTEX_PAINT",
                "WEIGHT_PAINT",
                "TEXTURE_PAINT",
            }:
                try:
                    bpy.ops.object.mode_set(mode=previous_mode)
                except RuntimeError:
                    LOG.debug(f"Unable to restore mode {previous_mode}")
