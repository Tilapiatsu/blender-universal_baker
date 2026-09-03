from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import bpy

from ..constant import LOG
from ..runtime.color_management_info import ColorManagementInfo


class ViewTransformOverride:
    @staticmethod
    def _capture(scene: bpy.types.Scene) -> ColorManagementInfo:
        return ColorManagementInfo(
            apply_view_transform=True,
            display_device=scene.display_settings.display_device,
            view_transform=scene.view_settings.view_transform,
            look=scene.view_settings.look,
            exposure=scene.view_settings.exposure,
            gamma=scene.view_settings.gamma,
        )

    @staticmethod
    def _apply_to_scene(scene: bpy.types.Scene, color_management_info: ColorManagementInfo):
        scene.display_settings.display_device = color_management_info.display_device
        scene.view_settings.view_transform = color_management_info.view_transform
        scene.view_settings.look = color_management_info.look
        scene.view_settings.exposure = color_management_info.exposure
        scene.view_settings.gamma = color_management_info.gamma

    @classmethod
    @contextmanager
    def override(cls, scene: bpy.types.Scene, color_management_info: ColorManagementInfo) -> Generator[None, Any, Any]:
        backup = cls._capture(scene)
        try:
            LOG.debug(f"Apply ColorManagementInfo : {color_management_info}")
            cls._apply_to_scene(scene, color_management_info)
            yield
        finally:
            LOG.debug(f"Restore ColorManagementInfo : {backup}")
            cls._apply_to_scene(scene, backup)
