from __future__ import annotations

from dataclasses import dataclass

import bpy


@dataclass(slots=True, frozen=True)
class VisibilityState:
    hide_render: bool
    hide_viewport: bool
    hide_select: bool


class VisibilityOverride:
    def __init__(
        self,
        obj: bpy.types.Object | None,
        hide_render: bool,
        hide_viewport: bool,
        hide_select: bool,
    ):
        self.obj = obj

        self.hide_render = hide_render
        self.hide_viewport = hide_viewport
        self.hide_select = hide_select

        if self.obj is None:
            return

        self.visibility_state = VisibilityState(
            hide_render=self.obj.hide_render,
            hide_viewport=self.obj.hide_viewport,
            hide_select=self.obj.hide_select,
        )

    def __enter__(self):
        if self.obj is None:
            return

        self.obj.hide_render = self.hide_render
        self.obj.hide_viewport = self.hide_viewport
        self.obj.hide_select = self.hide_select

        return self.obj

    def __exit__(self, exc_type, exc_value, traceback):
        if self.obj is None:
            return

        self.obj.hide_render = self.visibility_state.hide_render
        self.obj.hide_viewport = self.visibility_state.hide_viewport
        self.obj.hide_select = self.visibility_state.hide_select
