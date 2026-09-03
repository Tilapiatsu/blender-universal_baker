from __future__ import annotations

import bpy

from ..constant import LOG, get_prefs
from ..services.baker_library import BakerLibraryService
from .base import UBK_OT_Base
from ..bakers.custom import refresh


class UBK_OT_BakerlibraryRemove(UBK_OT_Base):
    """Remove a baker library item."""

    bl_idname = "ubk.remove_baker_library"
    bl_label = "Remove Baker library"
    bl_description = "Remove a new baker library to Universal Baker's preferences"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        preferences = get_prefs()

        return len(preferences.baker_libraries) and preferences.active_baker_library_idx != 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        preferences = get_prefs()

        service = BakerLibraryService()
        active = service.active(preferences)

        if active is None:
            return {"CANCELLED"}

        service.remove(preferences, preferences.active_baker_library_idx)

        refresh()

        return {"FINISHED"}


classes = (UBK_OT_BakerlibraryRemove,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
