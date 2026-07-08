import bpy


class UBK_OT_Base(bpy.types.Operator):
    def info(self, message):
        self.report({"INFO"}, message)

    def warning(self, message):
        self.report({"WARNING"}, message)

    def error(self, message):
        self.report({"ERROR"}, message)
