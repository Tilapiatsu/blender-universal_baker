import bpy


def get_colorspace_items(self, context):
    items = []
    for i in bpy.types.Image.bl_rna.properties["colorspace_settings"].fixed_type.properties["name"].enum_items:
        items.append((i.name, i.name, ""))
    return items
