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


# TODO: Need to support ray visibility : When baking Diffuse for exemple, I want to be able to disable camera ray, but keep indirect and shadow ray for all sources. Its important to make interaction beetween target_objects believable


class VisibilityOverride:
    def __init__(
        self,
        obj: bpy.types.Object | None,
        render: bool = True,
        viewport: bool = True,
        select: bool = True,
        show: bool = True,
    ):
        self.obj_name = ""

        if obj is None:
            return

        self.obj_name = obj.name

        self.render = render
        self.viewport = viewport
        self.select = select
        self.show = not obj.hide_get() if obj is not None else True

        if self.obj is None:
            return

        self.visibility_state = VisibilityState(
            render=not self.obj.hide_render,
            viewport=not self.obj.hide_viewport,
            select=not self.obj.hide_select,
            show=self.show,
        )
        LOG.debug(f"Store visibility state for {self.obj.name} : ")
        LOG.debug(
            f"Visible = {not self.obj.hide_get()} | Viewport = {not self.obj.hide_viewport} | Select = {not self.obj.hide_select} | Render = {not self.obj.hide_render}"
        )

        self._has_overriden = False

    @property
    def obj(self) -> bpy.data.Object | None:
        return bpy.data.objects.get(self.obj_name)

    def set_visibility(self) -> bpy.types.Object:
        if self.obj is None or self._has_overriden:
            return

        self.obj.hide_render = not self.render
        self.obj.hide_viewport = not self.viewport
        self.obj.hide_select = not self.select
        self.obj.hide_set(not self.show)

        LOG.debug(f"Set visibility state for {self.obj.name} : ")
        LOG.debug(
            f"Visible = {not self.obj.hide_get()} | Viewport = {not self.obj.hide_viewport} | Select = {not self.obj.hide_select} | Render = {not self.obj.hide_render}"
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

        LOG.debug(f"visibility state for {self.obj.name} restored :")
        LOG.debug(
            f"Visible = {not self.obj.hide_get()} | Viewport = {not self.obj.hide_viewport} | Select = {not self.obj.hide_select} | Render = {not self.obj.hide_render}"
        )

        self._has_overriden = False

    def __enter__(self):
        return self.set_visibility()

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert_visibility()
