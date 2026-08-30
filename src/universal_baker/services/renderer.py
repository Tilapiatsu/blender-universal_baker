from __future__ import annotations

import bpy
from ..constant import BAKE_VIEW_TRANSFORM
from ..runtime.context_bake import BakeContext
from ..runtime.visualization_state import SceneVisualizationState


class RendererService:
    """Wrapper around Blender's native baking system."""

    @staticmethod
    def capture_state() -> SceneVisualizationState:
        scene = bpy.context.scene
        scene_state = SceneVisualizationState(
            scene_name=scene.name,
            render_engine=scene.render.engine,
            view_transform=scene.view_settings.view_transform,
            exposure=scene.view_settings.exposure,
            gamma=scene.view_settings.gamma,
        )

        return scene_state

    @staticmethod
    def set_view_settings():
        view_settings = bpy.context.scene.view_settings
        view_settings.view_transform = BAKE_VIEW_TRANSFORM.view_transform
        view_settings.exposure = BAKE_VIEW_TRANSFORM.exposure
        view_settings.gamma = BAKE_VIEW_TRANSFORM.gamma

    @staticmethod
    def restore(scene_state: SceneVisualizationState):
        scene_name = scene_state.scene_name
        scene = bpy.data.scenes.get(scene_name)

        if scene is not None and scene_state.render_engine:
            scene.render.engine = scene_state.render_engine
            scene.view_settings.view_transform = scene_state.view_transform
            scene.view_settings.exposure = scene_state.exposure
            scene.view_settings.gamma = scene_state.gamma

    @classmethod
    def execute(cls, ctx: BakeContext):
        """Execute a single bake task."""
        scene_state = cls.capture_state()
        try:
            cls.set_view_settings()
            cls.configure(ctx)
            cls.prepare(ctx)
            cls.bake(ctx)
        finally:
            cls.restore(scene_state)

    @classmethod
    def configure(cls, ctx: BakeContext):
        """Configure Blender for the bake."""
        scene = ctx.session.context.scene
        settings_bake = ctx.settings.bake
        sampling_settings = ctx.settings.sampling

        scene.render.engine = "CYCLES"
        cycles = scene.cycles

        cycles.use_adaptive_sampling = sampling_settings.adaptive_sampling

        if sampling_settings.adaptive_sampling:
            cycles.adaptive_threshold = sampling_settings.noise_threshold
            cycles.samples = sampling_settings.max_samples
        else:
            cycles.samples = sampling_settings.samples

        cycles.use_denoising = sampling_settings.denoise

        bake = scene.render.bake
        bake.margin = settings_bake.margin
        bake.margin_type = settings_bake.margin_type
        bake.target = settings_bake.target

        bake.use_selected_to_active = ctx.task.selected_to_active

    # -------------------------------------------------------------------------
    # Prepare
    # -------------------------------------------------------------------------

    @classmethod
    def prepare(cls, ctx: BakeContext):
        """Prepare Blender selection."""
        bpy.ops.object.select_all(action="DESELECT")

        for obj in ctx.task.sources:
            obj.select_set(True)

        ctx.target.select_set(True)

        ctx.session.context.view_layer.objects.active = ctx.target

        if ctx.session.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        uv = ctx.target.data.uv_layers[ctx.task.uv_layer]

        ctx.target.data.uv_layers.active = uv

    @classmethod
    def bake(cls, ctx: BakeContext):
        """Execute Blender bake."""
        bpy.ops.object.bake(type=ctx.task.producer.blender_bake_type)
