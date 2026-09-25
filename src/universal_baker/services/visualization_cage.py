from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..constant import BAKE_CLIPPING_PREVIEW_ASSET_PATH, BAKE_PORTAL_PREVIEW_ASSET_PATH, LOG
from ..core.registry_baker import registry_baker
from ..enum.visualization import BakeVisualizationMode
from ..resources.asset_external import AssetExtrenal
from ..runtime.bake_objects import BakeObjects
from ..runtime.runtime_visualization_cage import (
    CageVisualizationRuntime,
)
from ..services.asset_external_setup import AssetExternalCageClippingSetup, AssetExternalCagePortalSetup
from ..services.temp_collection import TempCollection
from ..services.visualization_bake import BakeVisualizationService, PreviewData, set_preview_enabled
from .visibility_override import VisibilityOverride

if TYPE_CHECKING:
    from ..properties.object import UBK_TargetObject

LOG_SCOPE = "Cage Visualization"
TEMP_COLLECTION_NAME = "UBK_CAGE_VISUALIZATION"


def set_edit_cage(value: bool):
    from ..core.controller import BakeController

    project = BakeController.project(bpy.context)
    if project is None:
        return

    visualization = project.visualization

    visualization.cage_edit = value


def set_bake_preview(value: bool):
    from ..core.controller import BakeController

    project = BakeController.project(bpy.context)
    if project is None:
        return

    visualization = project.visualization

    visualization.preview_bake = value


def update_cage_color(self, context):
    if CageVisualizationService._runtime is None or not CageVisualizationService._runtime.active:
        return
    CageVisualizationService._refresh_cage_color()


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


def update_preview_bake(self, context):
    from ..core.controller import BakeController

    target = BakeController.active_target_object(context)
    project = BakeController.project(context)

    preview_bake = project.visualization.preview_bake

    if preview_bake:
        if target is None:
            preview_bake = False
            return

        if not CageVisualizationService.enable_bake_preview(target):
            preview_bake = False

    else:
        CageVisualizationService.disable_bake_preview()


def update_active_target(self, context):
    from ..core.controller import BakeController

    project = BakeController.project(context)

    preview_bake = project.visualization.preview_bake

    if not CageVisualizationService.is_active():
        return

    target = BakeController.active_target_object(context)

    if target is None or not target.have_source:
        CageVisualizationService.disable()
        set_edit_cage(False)
        return

    CageVisualizationService.refresh(target, preview_bake)


def exit_weight_paint_callback(obj, mode):
    try:
        safe_obj = getattr(obj, mode)

        if safe_obj == "OBJECT":
            # ISSUE: Crash when exit weight paint in bake preview mode
            CageVisualizationService.disable_bake_preview()
            CageVisualizationService.disable()

            set_bake_preview(False)
            set_edit_cage(False)

    except ReferenceError:
        return


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
    _cage_color: tuple[float, float, float, float] = (
        0.05,
        0.65,
        1.0,
        0.25,
    )

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    LINE_WIDTH = 2.0

    MSGBUS_OWNER = object()

    @classmethod
    def surface_color(cls) -> tuple[float, float, float, float]:
        return (cls._cage_color[0], cls._cage_color[1], cls._cage_color[2], cls._cage_color[3] * 0.8)

    @classmethod
    def wire_color(cls) -> tuple[float, float, float, float]:
        return cls._cage_color

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
    # TODO: Need to create way to enable the cage display, while dragging, and hide it after releasing

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
            from ..services.visualization_bake import BakeVisualizationService

            BakeVisualizationService.disable()

            runtime = cls._ensure_runtime()

            # -----------------------------------------------------
            # Acquire cage
            # -----------------------------------------------------
            cage = cls._acquire_cage(target)

            if cage is None:
                LOG.warning(f"Unable to acquire cage for {target.object.name}")
                return False

            asset_portal = AssetExtrenal(filepath=BAKE_PORTAL_PREVIEW_ASSET_PATH)
            bake_objects = BakeObjects(
                target_object=target.object,
                cage_object=cage,
                cage_hidden=cage.hide_render,
                is_cage_generated=True,
                source_objects=target.source_object_list,
            )

            runtime.cage_asset_setup = AssetExternalCagePortalSetup.prepare(
                asset_portal,
                bake_objects,
                target.uv_layer,
            )

            if runtime.cage_asset_setup is None or runtime.cage_asset_setup.object_offset_edit is None:
                LOG.warning("Cage asset preparation failed")
                return False

            runtime.cage_asset_setup.object_offset_edit.offset()

            runtime.begin(
                target_uuid=target.uuid,
                target_name=target.object.name,
                cage_name=cage.name,
            )

            try:
                cls._update_cage_color()
                cls._capture_state(target, cage)
                cls._create_temporary_collection(
                    [
                        runtime.cage_asset_setup.target,
                        cage,
                        runtime.cage_asset_setup.projection_target,
                        runtime.cage_asset_setup.projection_cage,
                    ]
                    + bake_objects.source_objects
                )
                cls._configure_visibility()
                cls._create_gpu_resources(cage)
                cls._register_draw_handler()
                cls._register_depsgraph_handler(cage)
                cls._enter_weight_paint(cage)

                return True

            except Exception:
                raise CageVisualizationError("Failed to enable Cage Visualization")
                cls.disable()

                return False

    @classmethod
    def enable_bake_preview(
        cls,
        target: UBK_TargetObject,
    ) -> None:
        # ISSUE: In bake preview mode, the baker parameters are not updating the material inputs anymore :(
        # ISSUE: In bake preview mode, the proper view transform is not loaded correctly
        # ISSUE: In Bake preview switching baker updates the preview properly, but selecting the selected baker again
        # disable the preview and I want to prevent that
        # ISSUE: Sometime Crash when ctrl + z in bake preview mode
        # TODO: Need to modify the parameter system to support SHADER sockets, and to insert group at the end of the
        # Prototype node tree : just before the node group output
        # TODO: need to tackle the ray visibility to control an object visible from secondary ray but not primary ones

        with LOG.scope(LOG_SCOPE):
            from ..core.controller import BakeController

            bake_group = BakeController.active_bake_group(bpy.context)

            if bake_group is None:
                LOG.warning("Bake Group not found")
                return

            active_baker = BakeController.active_baker(bpy.context)

            if active_baker is None:
                return

            producer = registry_baker[active_baker.baker]

            runtime = cls._runtime
            if runtime is None or not runtime.active:
                return

            if (
                runtime.cage_asset_setup is None
                or runtime.cage_asset_setup.object_offset_edit is None
                or runtime.cage_asset_setup.object_offset_preview is None
            ):
                raise ReferenceError("Projection Target is None")

            runtime.cage_asset_setup.object_offset_edit.revert()
            runtime.cage_asset_setup.object_offset_preview.offset()

            data = PreviewData(
                producer=producer,
                bake_group_uuid=bake_group.uuid,
                producer_uuid=active_baker.uuid,
                mode=BakeVisualizationMode.PREVIEW_CAGE,
                projection_target=runtime.cage_asset_setup.projection_target,
            )
            LOG.info("Enabling Bake Preview")
            BakeVisualizationService.enable_preview(data)

            cage = runtime.cage_asset_setup.cage

            if cage is None:
                LOG.error("Cage not found")
                return

            asset_clipping = AssetExtrenal(filepath=BAKE_CLIPPING_PREVIEW_ASSET_PATH)

            bake_objects = BakeObjects(
                target_object=target.object,
                cage_object=cage,
                cage_hidden=cage.hide_render,
                is_cage_generated=True,
                source_objects=target.source_object_list,
            )
            runtime.cage_clipping_setup = AssetExternalCageClippingSetup.prepare(
                asset_clipping,
                bake_objects,
                target.settings_cage.max_ray_distance,
            )

    # ---------------------------------------------------------
    # Disable
    # ---------------------------------------------------------

    @classmethod
    def disable(cls, disable_property=True) -> None:
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
                cls.disable_bake_preview()
                cls._remove_depsgraph_handler()
                cls._remove_draw_handler()
                cls._release_gpu_resources()
                cls._restore_mode_and_active_object()
                cls._restore_visibility()
                cls._cleanup_temporary_collection()
                cls._cleanup_cage_asset_setup()

            except Exception:
                raise CageVisualizationError("Failed while restoring Cage Visualization")

            finally:
                runtime.clear()

                if disable_property:
                    set_edit_cage(False)
                    set_bake_preview(False)

    @classmethod
    def disable_bake_preview(
        cls,
    ) -> None:
        with LOG.scope(LOG_SCOPE):
            runtime = cls._runtime
            if runtime is None or not runtime.active:
                return

            if (
                runtime.cage_asset_setup is None
                or runtime.cage_asset_setup.object_offset_edit is None
                or runtime.cage_asset_setup.object_offset_preview is None
            ):
                raise ReferenceError("Projection Target is None")

            runtime.cage_asset_setup.object_offset_preview.revert()
            runtime.cage_asset_setup.object_offset_edit.offset()

            BakeVisualizationService.disable()

            cls._cleanup_cage_clipping_setup()

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------
    @classmethod
    def refresh(cls, target: UBK_TargetObject | None, preview_bake: bool = False) -> bool:
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
                cls.disable_bake_preview()
                cls.disable()
                return False

            if not cls._target_uses_cage(target):
                cls.disable_bake_preview()
                cls.disable()
                return False

            runtime = cls._ensure_runtime()

            if runtime.target_uuid == target.uuid:
                return True

            LOG.debug(f"Refreshing Cage Visualization | {runtime.target_name} -> {target.object.name}")

            cls.disable_bake_preview()
            cls.disable(disable_property=target.settings_cage.cage_mode == "OBJECT")

            if target.settings_cage.cage_mode == "GENERATED":
                cls.enable(target)
                if preview_bake:
                    cls.enable_bake_preview(target)

            return True

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

        return CageObjectService.acquire(target.object, target.settings_cage)

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

        target_objects = [o.object for o in active_bake_group.target_objects if o.enabled and o.object is not None]

        # Capture target objects.
        for obj in target_objects:
            if obj is None:
                continue

            runtime.target_object_names.append(obj.name)

        # Capture sources.
        for source in target.source_object_list:
            if source is None:
                continue

            runtime.source_object_names.append(source.name)

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

            vo = VisibilityOverride(
                obj=obj,
                hide_get=False,
                hide_viewport=False,
            )

            runtime.visibility[obj.name] = vo

            vo.set_visibility()

        # Hide all target objects.
        for name in runtime.target_object_names:
            obj = bpy.data.objects.get(name)

            if obj is None:
                continue

            vo = VisibilityOverride(
                obj=obj,
                hide_get=True,
                hide_viewport=True,
            )
            runtime.visibility[obj.name] = vo

            vo.set_visibility()

        # Cage must be visible and selectable for weight paint.
        if runtime.cage_name:
            cage = bpy.data.objects.get(runtime.cage_name)

            if cage is not None:
                vo = VisibilityOverride(
                    obj=cage,
                    hide_get=False,
                    hide_viewport=False,
                )

                runtime.visibility[cage.name] = vo

                vo.set_visibility()

    @classmethod
    def _restore_visibility(cls) -> None:
        runtime = cls._ensure_runtime()

        for override in runtime.visibility.values():
            override.revert_visibility()

    # ---------------------------------------------------------
    # Temporary Collection
    # ---------------------------------------------------------
    #
    @classmethod
    def _create_temporary_collection(cls, objects: list[bpy.types.Object]) -> bpy.types.Collection:
        runtime = cls._ensure_runtime()

        runtime.temporary_collection = TempCollection(TEMP_COLLECTION_NAME, objects=objects)
        runtime.temporary_collection.create()

        return runtime.temporary_collection.collection

    @classmethod
    def _get_temporary_collection(cls) -> bpy.types.Collection | None:
        runtime = cls._ensure_runtime()

        if not runtime.temporary_collection_name:
            return None

        return bpy.data.collections.get(runtime.temporary_collection_name)

    @classmethod
    def _cleanup_temporary_collection(cls) -> None:
        runtime = cls._ensure_runtime()

        if runtime.temporary_collection is None:
            return

        runtime.temporary_collection.cleanup()

    @classmethod
    def _cleanup_cage_asset_setup(cls):
        runtime = cls._ensure_runtime()
        if runtime.cage_asset_setup is not None:
            runtime.cage_asset_setup.cleanup()

    @classmethod
    def _cleanup_cage_clipping_setup(cls):
        runtime = cls._ensure_runtime()
        if runtime.cage_clipping_setup is not None:
            runtime.cage_clipping_setup.cleanup()

    # ---------------------------------------------------------
    # GPU
    # ---------------------------------------------------------

    @classmethod
    def _create_gpu_resources(
        cls,
        cage: bpy.types.Object,
    ) -> None:
        runtime = cls._ensure_runtime()

        # Release the previous batches first.
        cls._release_gpu_batches()

        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_cage = cage.evaluated_get(depsgraph)

        evaluated_mesh = None

        try:
            evaluated_mesh = evaluated_cage.to_mesh()

            if evaluated_mesh is None:
                return

            evaluated_mesh.calc_loop_triangles()

            runtime.surface_shader = gpu.shader.from_builtin("SMOOTH_COLOR")

            runtime.wire_shader = gpu.shader.from_builtin("UNIFORM_COLOR")

            surface_positions = []
            surface_colors = []

            for triangle in evaluated_mesh.loop_triangles:
                for vertex_index in triangle.vertices:
                    surface_positions.append(evaluated_mesh.vertices[vertex_index].co[:])
                    surface_colors.append(cls.surface_color())

            runtime.surface_batch = batch_for_shader(
                runtime.surface_shader,
                "TRIS",
                {
                    "pos": surface_positions,
                    "color": surface_colors,
                },
            )

            wire_positions = []

            for edge in evaluated_mesh.edges:
                wire_positions.append(evaluated_mesh.vertices[edge.vertices[0]].co[:])

                wire_positions.append(evaluated_mesh.vertices[edge.vertices[1]].co[:])

            runtime.wire_batch = batch_for_shader(runtime.wire_shader, "LINES", {"pos": wire_positions})

        finally:
            if evaluated_mesh is not None:
                evaluated_cage.to_mesh_clear()

        runtime.gpu_dirty = False

    @classmethod
    def _release_gpu_batches(cls) -> None:
        runtime = cls._ensure_runtime()

        runtime.surface_batch = None
        runtime.wire_batch = None

    @classmethod
    def _release_gpu_resources(cls) -> None:
        runtime = cls._ensure_runtime()

        cls._release_gpu_batches()

        runtime.surface_shader = None
        runtime.wire_shader = None

    @classmethod
    def _update_cage_color(cls) -> None:
        from ..core.controller import BakeController

        project = BakeController.project(bpy.context)

        cls._cage_color = project.visualization.cage_color

    @classmethod
    def _refresh_cage_color(cls) -> None:

        runtime = cls._ensure_runtime()
        cage = bpy.data.objects.get(runtime.cage_name)

        if cage is None:
            return

        cls._remove_draw_handler()
        cls._release_gpu_resources()

        cls._update_cage_color()

        cls._create_gpu_resources(cage)
        cls._register_draw_handler()

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
        runtime = cls._ensure_runtime()

        if not runtime.active:
            return

        cage = bpy.data.objects.get(runtime.cage_name) if runtime.cage_name else None

        if cage is None:
            return

        # The cage's modifiers / evaluated geometry changed.
        if runtime.gpu_dirty:
            cls._create_gpu_resources(cage)

        if runtime.surface_batch is None:
            return

        gpu.state.blend_set("ALPHA")

        # IMPORTANT:
        # Use the depth buffer so the cage behaves like a real
        # surface instead of being drawn through everything.
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(False)

        gpu.matrix.push()

        try:
            gpu.matrix.multiply_matrix(cage.matrix_world)

            runtime.surface_shader.bind()

            runtime.surface_batch.draw(runtime.surface_shader)

            if runtime.wire_batch is not None:
                gpu.state.line_width_set(1.5)

                runtime.wire_shader.bind()

                runtime.wire_shader.uniform_float("color", cls.wire_color())

                runtime.wire_batch.draw(runtime.wire_shader)

        finally:
            gpu.matrix.pop()

            gpu.state.line_width_set(1.0)
            gpu.state.depth_mask_set(True)
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
                cage.hide_set(True)

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

    @classmethod
    def depsgraph_update_post(cls, scene, depsgraph) -> None:
        with LOG.scope(LOG_SCOPE):
            runtime = cls._ensure_runtime()

            if not runtime.active:
                LOG.warning("Runtime is not active")
                cls._remove_depsgraph_handler()
                return

            if runtime.cage_name is None:
                LOG.warning("Cage is unknown")
                cls._remove_depsgraph_handler()
                return

            cage = bpy.data.objects.get(runtime.cage_name)

            if cage is None:
                LOG.warning("Cage is None")
                cls.disable()
                return

            for update in depsgraph.updates:
                if update.id.name == cage.name:
                    runtime.mark_gpu_dirty()
                    return

    @classmethod
    def subscribe_to(cls, obj, data_path, callback):
        # Get a rna subscription link from the object
        subscribe_to = obj.path_resolve(data_path, False)

        # Effectively subscribe to the rna path from the object
        bpy.msgbus.subscribe_rna(
            key=subscribe_to,
            owner=cls.MSGBUS_OWNER,
            args=(
                obj,
                data_path,
            ),
            notify=callback,
        )

    # NOTE: https://blender.stackexchange.com/questions/21408/know-when-edit-mode-is-entered-by-script-python
    @classmethod
    def _register_depsgraph_handler(cls, cage: bpy.types.Object) -> None:
        if cls.depsgraph_update_post not in bpy.app.handlers.depsgraph_update_post:
            LOG.debug("Registering depsgraph handler")
            cls.subscribe_to(cage, "mode", exit_weight_paint_callback)
            bpy.app.handlers.depsgraph_update_post.append(cls.depsgraph_update_post)

    @classmethod
    def _remove_depsgraph_handler(cls) -> None:
        LOG.debug("Clear Message Bus on Cage")
        bpy.msgbus.clear_by_owner(cls.MSGBUS_OWNER)

        handler = cls.depsgraph_update_post

        if handler in bpy.app.handlers.depsgraph_update_post:
            LOG.debug("Unregistering depsgraph handler")
            bpy.app.handlers.depsgraph_update_post.remove(handler)
