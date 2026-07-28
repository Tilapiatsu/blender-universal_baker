import bpy

from ..constant import LOG


class UBK_OT_Base(bpy.types.Operator):
    LOG_SCOPE = "Operator"

    def info(self, message):
        self.report({"INFO"}, message)
        with LOG.scope(self.LOG_SCOPE):
            LOG.info(message)

    def warning(self, message):
        self.report({"WARNING"}, message)
        with LOG.scope(self.LOG_SCOPE):
            LOG.warning(message)

    def error(self, message):
        self.report({"ERROR"}, message)
        with LOG.scope(self.LOG_SCOPE):
            LOG.error(message)
