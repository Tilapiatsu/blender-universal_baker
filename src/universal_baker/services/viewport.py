from __future__ import annotations

import bpy

from ..constant import DISPLAY_COLORSPACE
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
                scene_name=scene.name,
                render_engine=scene.render.engine,
                view_transform=scene.view_settings.view_transform,
                exposure=scene.view_settings.exposure,
                gamma=scene.view_settings.gamma,
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
        view_settings = bpy.context.scene.view_settings
        view_settings.view_transform = DISPLAY_COLORSPACE.view_transform
        view_settings.exposure = DISPLAY_COLORSPACE.exposure
        view_settings.gamma = DISPLAY_COLORSPACE.gamma
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
                scene.view_settings.view_transform = scene_state.view_transform
                scene.view_settings.exposure = scene_state.exposure
                scene.view_settings.gamma = scene_state.gamma

            for viewport in scene_state.viewports:
                for window in bpy.context.window_manager.windows:
                    screen = window.screen

                    for area in screen.areas:
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
