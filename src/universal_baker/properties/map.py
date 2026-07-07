from bpy.types import PropertyGroup, BoolProperty, EnumProperty, StringProperty, IntProperty


class UBK_Map(PropertyGroup):
    enabled: BoolProperty(default=True)
    baker: EnumProperty(items=get_registered_bakers)
    image_name: StringProperty(default="Bake")
    resolution_x: IntProperty(default=2048)
    resolution_y: IntProperty(default=2048)


classes = (UBK_Map,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
