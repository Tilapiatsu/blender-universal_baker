from __future__ import annotations

import bpy

from ..baker.session import BakeSession
from ..baker.task import BakeTask


class RendererService:
    """Wrapper around Blender's native baking system."""

    @classmethod
    def execute(cls, session: BakeSession, task: BakeTask):
        """Execute a single bake task."""

        cls.configure(session, task)
        cls.prepare(session, task)
        cls.bake(session, task)

    # -------------------------------------------------------------------------
    # Configure
    # -------------------------------------------------------------------------

    @classmethod
    def configure(cls, session: BakeSession, task: BakeTask):
        """Configure Blender for the bake."""

        scene = session.context.scene

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

        #
        # Selected to Active
        #

        bake.use_selected_to_active = task.selected_to_active

    # -------------------------------------------------------------------------
    # Prepare
    # -------------------------------------------------------------------------

    @classmethod
    def prepare(cls, session: BakeSession, task: BakeTask):
        """Prepare Blender selection."""

        bpy.ops.object.select_all(action="DESELECT")

        #
        # Sources
        #

        for obj in task.sources:
            obj.select_set(True)

        #
        # Target
        #

        task.target.select_set(True)

        session.context.view_layer.objects.active = task.target

        #
        # Force Object Mode
        #

        if session.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    @classmethod
    def bake(cls, session: BakeSession, task: BakeTask):
        """Execute Blender bake."""

        bpy.ops.object.bake(type=task.blender_bake_type)
