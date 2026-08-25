from __future__ import annotations

from .base import UBK_OT_Base
from ..services.project_synchronizer import ProjectSynchronizer


class UBK_OT_refresh_custom_baker_parameters(UBK_OT_Base):
    bl_idname = "ubk.refresh_custom_baker_parameters"
    bl_label = "Refresh Baker Parameters"
    bl_description = "Refresh parameters from external bakers if they have changed"

    def execute(self, context):
        ProjectSynchronizer.synchronize_blend_file()

        return {"FINISHED"}


classes = (UBK_OT_refresh_custom_baker_parameters,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
