import bpy

BAKE_IMAGE_NODE_NAME = "UBK_BakeImage"
BAKE_IMAGE_NODE_LABEL = "Universal Baker"
BAKE_MATERIAL_NAME = "UBK_BakeMaterial"
ADDON_PACKAGE = __package__


def get_prefs():
    return bpy.context.preferences.addons[ADDON_PACKAGE].preferences
