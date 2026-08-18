from __future__ import annotations

import bpy

from ..runtime.visualization_state import (
    VisualizationState,
    SceneVisualizationState,
    ViewportState,
)


class ViewportService:
    @staticmethod
    def capture_state() -> VisualizationState:

        state = VisualizationState()

        for scene in bpy.data.scenes:
            scene_state = SceneVisualizationState(
                render_engine=scene.render.engine,
            )

            state.scenes[scene.name] = scene_state

        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type != "VIEW_3D":
                    continue

                space = area.spaces.active

                shading = space.shading

                scene_state = state.scenes.get(window.scene.name)

                if scene_state is None:
                    continue

                scene_state.viewports.append(
                    ViewportState(
                        area=area,
                        shading_type=shading.type,
                        color_type=shading.color_type,
                    )
                )

        return state

    @staticmethod
    def set_rendered():
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != "VIEW_3D":
                    continue

                area.spaces.active.shading.type = "RENDERED"

    @staticmethod
    def set_texture():
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != "VIEW_3D":
                    continue

                shading = area.spaces.active.shading

                shading.type = "SOLID"
                shading.color_type = "TEXTURE"

    @staticmethod
    def restore(state: VisualizationState):
        for scene_name, scene_state in state.scenes.items():
            scene = bpy.data.scenes.get(scene_name)

            if scene is not None:
                if scene_state.render_engine:
                    scene.render.engine = scene_state.render_engine

            for viewport in scene_state.viewports:
                area = viewport.area

                # The area may have disappeared while
                # visualization was active.
                if area.type != "VIEW_3D":
                    continue

                shading = area.spaces.active.shading

                shading.type = viewport.shading_type
                shading.color_type = viewport.color_type
