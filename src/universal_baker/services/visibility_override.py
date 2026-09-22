from __future__ import annotations

from dataclasses import dataclass

import bpy
from universal_baker.constant import LOG


@dataclass(slots=True, frozen=True)
class VisibilityState:
    hide_render: bool
    hide_viewport: bool
    hide_select: bool
    hide_get: bool


# TODO: Need to support ray visibility : When baking Diffuse for exemple, I want to be able to disable camera ray, but keep indirect and shadow ray for all sources. Its important to make interaction beetween target_objects believable


class VisibilityOverride:
    def __init__(
        self,
        obj: bpy.types.Object | None,
        hide_render: bool = False,
        hide_viewport: bool = False,
        hide_select: bool = False,
        hide_get: bool = False,
    ):
        self.obj = obj

        self.hide_render = hide_render
        self.hide_viewport = hide_viewport
        self.hide_select = hide_select
        self.hide_get = obj.hide_get() if obj is not None else False

        if self.obj is None:
            return

        self.visibility_state = VisibilityState(
            hide_render=self.obj.hide_render,
            hide_viewport=self.obj.hide_viewport,
            hide_select=self.obj.hide_select,
            hide_get=self.hide_get,
        )
        LOG.debug(f"Store visibility state for {self.obj.name} : ")
        LOG.debug(f"Visible = {not self.obj.hide_get()}")
        LOG.debug(f"Viewport = {not self.obj.hide_viewport}")
        LOG.debug(f"Select = {not self.obj.hide_select}")
        LOG.debug(f"Render = {not self.obj.hide_render}")

        self._has_overriden = False

    def set_visibility(self) -> bpy.types.Object:
        if self.obj is None or self._has_overriden:
            return

        self.obj.hide_render = self.hide_render
        self.obj.hide_viewport = self.hide_viewport
        self.obj.hide_select = self.hide_select
        self.obj.hide_set(self.hide_get)

        LOG.debug(f"Set visibility state for {self.obj.name} : ")
        LOG.debug(f"Visible = {not self.obj.hide_get()}")
        LOG.debug(f"Viewport = {not self.obj.hide_viewport}")
        LOG.debug(f"Select = {not self.obj.hide_select}")
        LOG.debug(f"Render = {not self.obj.hide_render}")

        self._has_overriden = True

        return self.obj

    def revert_visibility(self) -> None:
        if self.obj is None or not self._has_overriden:
            return

        self.obj.hide_render = self.visibility_state.hide_render
        self.obj.hide_viewport = self.visibility_state.hide_viewport
        self.obj.hide_select = self.visibility_state.hide_select
        self.obj.hide_set(self.visibility_state.hide_get)

        LOG.debug(f"visibility state for {self.obj.name} restored :")
        LOG.debug(f"Visible = {not self.obj.hide_get()}")
        LOG.debug(f"Viewport = {not self.obj.hide_viewport}")
        LOG.debug(f"Select = {not self.obj.hide_select}")
        LOG.debug(f"Render = {not self.obj.hide_render}")

        self._has_overriden = False

    def __enter__(self):
        return self.set_visibility()

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert_visibility()
