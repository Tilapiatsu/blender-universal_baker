from __future__ import annotations

import bpy


def parameter_updated(self, context):
    from ..runtime.runtime_manager import RuntimeManager

    runtime = RuntimeManager.get(context.scene).visualization

    if runtime.preview_enabled:
        runtime.request_preview_refresh()

    runtime.refresh_preview_parameters(ui_prop=self)


class UBK_BakerParameterValue(bpy.types.PropertyGroup):
    identifier: bpy.props.StringProperty(update=parameter_updated)
    float_value: bpy.props.FloatProperty(update=parameter_updated)
    int_value: bpy.props.IntProperty(update=parameter_updated)
    bool_value: bpy.props.BoolProperty(update=parameter_updated)
    enum_value: bpy.props.StringProperty(update=parameter_updated)


classes = (UBK_BakerParameterValue,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
