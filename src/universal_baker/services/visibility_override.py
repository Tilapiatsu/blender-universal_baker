from __future__ import annotations

from dataclasses import dataclass

import bpy

from ..constant import LOG


@dataclass(slots=True, frozen=True)
class VisibilityState:
    render: bool
    viewport: bool
    select: bool
    show: bool
    visible_camera: bool
    visible_diffuse: bool
    visible_glossy: bool
    visible_transmission: bool
    visible_volume_scatter: bool
    visible_shadow: bool


class VisibilityOverride:
    def __init__(
        self,
        obj: bpy.types.Object | None,
        render: bool | None = None,
        viewport: bool | None = None,
        select: bool | None = None,
        show: bool | None = None,
        visible_camera: bool | None = None,
        visible_diffuse: bool | None = None,
        visible_glossy: bool | None = None,
        visible_transmission: bool | None = None,
        visible_volume_scatter: bool | None = None,
        visible_shadow: bool | None = None,
    ):
        self.obj_name = ""

        if obj is None:
            return

        self.obj_name = obj.name

        self.render = render
        self.viewport = viewport
        self.select = select
        self.show = not obj.hide_get() if obj is not None else True

        self.visible_camera = visible_camera
        self.visible_diffuse = visible_diffuse
        self.visible_glossy = visible_glossy
        self.visible_transmission = visible_transmission
        self.visible_volume_scatter = visible_volume_scatter
        self.visible_shadow = visible_shadow

        if self.obj is None:
            return

        self.visibility_state = VisibilityState(
            render=not self.obj.hide_render,
            viewport=not self.obj.hide_viewport,
            select=not self.obj.hide_select,
            show=self.show,
            visible_camera=self.obj.visible_camera,
            visible_diffuse=self.obj.visible_diffuse,
            visible_glossy=self.obj.visible_glossy,
            visible_transmission=self.obj.visible_transmission,
            visible_volume_scatter=self.obj.visible_volume_scatter,
            visible_shadow=self.obj.visible_shadow,
        )
        # LOG.debug(f"Store visibility state for {self.obj.name} : ")
        # LOG.debug(
        #     f"Visible = {not self.obj.hide_get()} | Viewport = {not self.obj.hide_viewport} | Select = {not self.obj.hide_select} | Render = {not self.obj.hide_render}"
        # )

        self._has_overriden = False

    @property
    def obj(self) -> bpy.data.Object | None:
        return bpy.data.objects.get(self.obj_name)

    def set_visibility(self) -> bpy.types.Object:
        if self.obj is None or self._has_overriden:
            return

        if self.render is not None:
            self.obj.hide_render = not self.render

        if self.viewport is not None:
            self.obj.hide_viewport = not self.viewport

        if self.select is not None:
            self.obj.hide_select = not self.select

        if self.show is not None:
            self.obj.hide_set(not self.show)

        if self.visible_camera is not None:
            self.obj.visible_camera = self.visible_camera

        if self.visible_diffuse is not None:
            self.obj.visible_diffuse = self.visible_diffuse

        if self.visible_glossy is not None:
            self.obj.visible_glossy = self.visible_glossy

        if self.visible_transmission is not None:
            self.obj.visible_transmission = self.visible_transmission

        if self.visible_volume_scatter is not None:
            self.obj.visible_volume_scatter = self.visible_volume_scatter

        if self.visible_shadow is not None:
            self.obj.visible_shadow = self.visible_shadow

        LOG.debug(f"Set visibility state for {self.obj.name} : ")
        LOG.debug(
            f"Visible = {not self.obj.hide_get()} | "
            f"Viewport = {not self.obj.hide_viewport} | "
            f"Select = {not self.obj.hide_select} | "
            f"Render = {not self.obj.hide_render} | "
            f"Camera = {self.obj.visible_camera} | "
            f"Diffuse = {self.obj.visible_diffuse} | "
            f"Glossy = {self.obj.visible_glossy} | "
            f"Transmission = {self.obj.visible_transmission} | "
            f"Volume = {self.obj.visible_volume_scatter} | "
            f"Shadow = {self.obj.visible_shadow} | "
        )

        self._has_overriden = True

        return self.obj

    def revert_visibility(self) -> None:
        if self.obj is None or not self._has_overriden:
            return

        self.obj.hide_render = not self.visibility_state.render
        self.obj.hide_viewport = not self.visibility_state.viewport
        self.obj.hide_select = not self.visibility_state.select
        self.obj.hide_set(not self.visibility_state.show)

        self.obj.visible_camera = self.visibility_state.visible_camera
        self.obj.visible_diffuse = self.visibility_state.visible_diffuse
        self.obj.visible_glossy = self.visibility_state.visible_glossy
        self.obj.visible_transmission = self.visibility_state.visible_transmission
        self.obj.visible_volume_scatter = self.visibility_state.visible_volume_scatter
        self.obj.visible_shadow = self.visibility_state.visible_shadow

        LOG.debug(f"visibility state for {self.obj.name} restored :")
        LOG.debug(
            f"Visible = {not self.obj.hide_get()} | "
            f"Viewport = {not self.obj.hide_viewport} | "
            f"Select = {not self.obj.hide_select} | "
            f"Render = {not self.obj.hide_render} | "
            f"Camera = {self.obj.visible_camera} | "
            f"Diffuse = {self.obj.visible_diffuse} | "
            f"Glossy = {self.obj.visible_glossy} | "
            f"Transmission = {self.obj.visible_transmission} | "
            f"Volume = {self.obj.visible_volume_scatter} | "
            f"Shadow = {self.obj.visible_shadow} | "
        )

        self._has_overriden = False

    def __enter__(self):
        return self.set_visibility()

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert_visibility()
