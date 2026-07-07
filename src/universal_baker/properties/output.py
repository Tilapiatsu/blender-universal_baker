from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty


# TODO: Need to set the proper output properties
class UBK_Output(PropertyGroup):
    enabled: BoolProperty(default=True)


classes = (UBK_Output,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
