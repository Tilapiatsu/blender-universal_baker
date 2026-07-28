import bpy
from .logger import Logger

from .logger.sinks.console import ConsoleSink
from .logger_bake_middleware.bake_summary import BakeSummaryMiddleware

LOG = Logger("Universal Baker")
LOG.dispatcher.add_sink(ConsoleSink())
LOG.middleware.add(BakeSummaryMiddleware())

BAKE_IMAGE_NODE_NAME = "UBK_BakeImage"
BAKE_IMAGE_NODE_LABEL = "Universal Baker"
BAKE_MATERIAL_NAME = "UBK_BakeMaterial"
INTERNAL_DATA_NAME = "UBK_INTERNAL_DO_NOT_TOUCH"
SAFE_CHR = "_"

ADDON_PACKAGE = __package__


def get_prefs():
    return bpy.context.preferences.addons[ADDON_PACKAGE].preferences
