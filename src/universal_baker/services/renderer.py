from __future__ import annotations

import bpy

from ..constant import LOG
from ..resources.scene_view_transform import SceneViewTransform
from ..runtime.context_bake import BakeContext
from ..runtime.render_settings import RenderSettings
from ..runtime.visualization_state import SceneVisualizationState


class RendererService:
    """Wrapper around Blender's native baking system."""

    @staticmethod
    def capture_state() -> SceneVisualizationState:
        scene = bpy.context.scene
        scene_state = SceneVisualizationState(
            scene_name=scene.name,
            render_engine=scene.render.engine,
            display_device=scene.display_settings.display_device,
            view_transform=scene.view_settings.view_transform,
            look=scene.view_settings.look,
            exposure=scene.view_settings.exposure,
            gamma=scene.view_settings.gamma,
        )

        return scene_state

    @staticmethod
    def capture_render_settings() -> RenderSettings:
        scene = bpy.context.scene
        cycles = scene.cycles
        bake = scene.render.bake

        render_settings = RenderSettings(
            use_adaptive_sampling=cycles.use_adaptive_sampling,
            adaptive_threshold=cycles.adaptive_threshold,
            samples=cycles.samples,
            adaptive_min_samples=cycles.adaptive_min_samples,
            use_denoising=cycles.use_denoising,
            bake_margin=bake.margin,
            bake_margin_type=bake.margin_type,
            bake_target=bake.target,
            bake_use_selected_to_active=bake.use_selected_to_active,
            bake_use_cage=bake.use_cage,
            bake_cage_object=bake.cage_object,
            bake_cage_extrusion=bake.cage_extrusion,
            bake_max_ray_distance=bake.max_ray_distance,
        )

        return render_settings

    @staticmethod
    def set_view_settings(view_transform: SceneViewTransform):
        view_settings = bpy.context.scene.view_settings
        view_settings.view_transform = view_transform.view_transform.value
        view_settings.exposure = view_transform.exposure
        view_settings.gamma = view_transform.gamma
        LOG.debug(f"Set Viewtransform to {view_transform.view_transform.value}")

    @staticmethod
    def restore(scene_state: SceneVisualizationState, render_settings: RenderSettings):
        scene_name = scene_state.scene_name
        scene = bpy.data.scenes.get(scene_name)

        if scene is not None:
            if scene_state.render_engine:
                LOG.debug(f"Restore Viewtransform to {scene_state.view_transform}")

                scene.render.engine = scene_state.render_engine
                scene.display_settings.display_device = scene_state.display_device
                scene.view_settings.view_transform = scene_state.view_transform
                scene.view_settings.look = scene_state.look
                scene.view_settings.exposure = scene_state.exposure
                scene.view_settings.gamma = scene_state.gamma

            cycles = scene.cycles
            bake = scene.render.bake

            cycles.use_adaptive_sampling = render_settings.use_adaptive_sampling
            cycles.adaptive_threshold = render_settings.adaptive_threshold
            cycles.samples = render_settings.samples
            cycles.adaptive_min_samples = render_settings.adaptive_min_samples
            cycles.use_denoising = render_settings.use_denoising
            bake.margin = render_settings.bake_margin
            bake.margin_type = render_settings.bake_margin_type
            bake.target = render_settings.bake_target
            bake.use_selected_to_active = render_settings.bake_use_selected_to_active
            bake.use_cage = render_settings.bake_use_cage
            bake.cage_object = render_settings.bake_cage_object
            bake.cage_extrusion = render_settings.bake_cage_extrusion
            bake.max_ray_distance = render_settings.bake_max_ray_distance

    @classmethod
    def execute(cls, ctx: BakeContext):
        """Execute a single bake task."""
        scene_state = cls.capture_state()
        render_settings = cls.capture_render_settings()
        try:
            # cls.set_view_settings(ctx.task.producer.bake_view_transform)
            cls.configure(ctx)
            cls.prepare(ctx)
            cls.bake(ctx)
        finally:
            cls.restore(scene_state, render_settings)

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
        bake.use_cage = ctx.task.settings_cage.mode != "NONE"
        bake.cage_object = ctx.task.settings_cage.cage_object
        bake.cage_extrusion = ctx.task.settings_cage.cage_extrusion
        bake.max_ray_distance = ctx.task.settings_cage.max_ray_distance

    # -------------------------------------------------------------------------
    # Prepare
    # -------------------------------------------------------------------------

    @classmethod
    def prepare(cls, ctx: BakeContext):
        """Prepare Blender selection."""
        bpy.ops.object.select_all(action="DESELECT")

        for obj in ctx.sources:
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
