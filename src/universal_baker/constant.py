import bpy

from .logger import Logger

from .logger.severity import Severity
from .logger.sinks.console import ConsoleSink
from .logger.middleware.statistics import StatisticsMiddleware
from .logger_bake_middleware.bake_summary import BakeSummaryMiddleware

LOG = Logger("Universal Baker")
LOG.dispatcher.add_sink(ConsoleSink(level=Severity.DEBUG))
LOG.middleware.add(BakeSummaryMiddleware())
LOG.middleware.add(StatisticsMiddleware())

BAKE_IMAGE_NODE_NAME = "UBK_BakeImage"
BAKE_IMAGE_NODE_LABEL = "Universal Baker"
BAKE_MATERIAL_NAME = "UBK_BakeMaterial"
INTERNAL_DATA_NAME = "UBK_INTERNAL_DO_NOT_TOUCH"
PROTOTYPE_NAME = "UBK_PROTOTYPE"
SAFE_CHR = "_"
ADDON_PACKAGE = __package__


def get_prefs():
    return bpy.context.preferences.addons[ADDON_PACKAGE].preferences
