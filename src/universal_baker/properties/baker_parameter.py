from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bakers.parameter.parameter import BakerParameterType

import bpy


def draw_baker_parameters(layout, baker, values):
    for parameter in baker.parameters.values():
        if not parameter.visible:
            continue

        value = values.get(parameter.identifier)

        if value is None:
            continue

        row = layout.row()

        row.label(text=parameter.name)

        match parameter.type:
            case BakerParameterType.FLOAT:
                row.prop(
                    value,
                    "float_value",
                    text="",
                )
            case BakerParameterType.INT:
                row.prop(
                    value,
                    "int_value",
                    text="",
                )
            case BakerParameterType.BOOL:
                row.prop(
                    value,
                    "bool_value",
                    text="",
                )
            case BakerParameterType.ENUM:
                row.prop(
                    value,
                    "enum_value",
                    text="",
                )


class UBK_BakerParameterValue(bpy.types.PropertyGroup):
    identifier: bpy.props.StringProperty()
    float_value: bpy.props.FloatProperty()
    int_value: bpy.props.IntProperty()
    bool_value: bpy.props.BoolProperty()
    enum_value: bpy.props.StringProperty()


classes = (UBK_BakerParameterValue,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
