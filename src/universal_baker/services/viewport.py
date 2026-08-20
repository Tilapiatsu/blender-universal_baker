from __future__ import annotations

import bpy

from ..runtime.runtime_visualization import VisualizationRuntime

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
                        shading_light=shading.light,
                        show_object_outline=shading.show_object_outline,
                        show_xray=shading.show_xray,
                        show_shadows=shading.show_shadows,
                        show_cavity=shading.show_cavity,
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
                shading.light = "FLAT"
                shading.show_object_outline = False
                shading.show_shadows = False
                shading.show_xray = False
                shading.show_cavity = False

    @staticmethod
    def restore(state: VisualizationRuntime):
        for scene_name, scene_state in state.scenes.items():
            scene = bpy.data.scenes.get(scene_name)

            if scene is not None and scene_state.render_engine:
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
                shading.light = viewport.shading_light
                shading.show_object_outline = viewport.show_object_outline
                shading.show_xray = viewport.show_xray
                shading.show_shadows = viewport.show_shadows
                shading.show_cavity = viewport.show_cavity
