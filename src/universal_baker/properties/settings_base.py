import bpy


def get_colorspace_items(self, context):
    items = [("Non-Color", "Non-Color", "")]
    for i in bpy.types.Image.bl_rna.properties["colorspace_settings"].fixed_type.properties["name"].enum_items:
        if (i.name, i.name, "") in items:
            continue
        items.append((i.name, i.name, ""))
    return items
