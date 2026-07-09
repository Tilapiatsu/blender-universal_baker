from __future__ import annotations

import bpy
from ..baker.context import BakeContext


class RendererService:
    """Wrapper around Blender's native baking system."""

    @classmethod
    def execute(cls, ctx: BakeContext):
        """Execute a single bake task."""
        cls.configure(ctx)
        cls.prepare(ctx)
        cls.bake(ctx)

    @classmethod
    def configure(cls, ctx: BakeContext):
        """Configure Blender for the bake."""
        scene = ctx.session.context.scene

        #
        # MVP
        #
        # Later these values will come from the
        # Output Settings.
        #

        scene.render.engine = "CYCLES"
        cycles = scene.cycles
        cycles.samples = 64
        bake = scene.render.bake
        bake.margin = 16
        bake.margin_type = "ADJACENT_FACES"

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

        ctx.task.target.select_set(True)

        ctx.session.context.view_layer.objects.active = ctx.task.target

        if ctx.session.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    @classmethod
    def bake(cls, ctx: BakeContext):
        """Execute Blender bake."""

        bpy.ops.object.bake(type=ctx.task.baker.blender_bake_type)
