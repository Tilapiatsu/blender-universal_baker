from __future__ import annotations

import bpy


def parameter_updated(self, context):
    from ..runtime.runtime_manager import RuntimeManager

    runtime = RuntimeManager.get(context.scene).visualization

    if runtime.preview_enabled:
        runtime.request_preview_refresh()

    if context.scene.ubk_project.visualization.is_dragging:
        pass
    else:
        bpy.ops.draggableprop.subscribe("INVOKE_DEFAULT")

    runtime.refresh_preview_parameters(ui_prop=self)


# https://blender.stackexchange.com/questions/245233/drag-events-of-a-panel-ui-slider
class DRAGGABLEPROP_OT_subscribe(bpy.types.Operator):
    bl_idname = "draggableprop.subscribe"
    bl_label = ""
    # This is used so we don't end up in an infinite loop because we blocked the release event
    stop: bpy.props.BoolProperty()

    def modal(self, context, event):
        if self.stop:
            context.scene.ubk_project.visualization.is_dragging = False
            return {"FINISHED"}

        # Stop the modal on next frame. Don't block the event since we want to exit the field dragging
        if context.scene.ubk_project.visualization.is_dragging and event.value == "RELEASE":
            self.stop = True
        elif not context.scene.ubk_project.visualization.is_dragging and event.type == "MOUSEMOVE":
            context.scene.ubk_project.visualization.is_dragging = True

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class UBK_BakerParameterValue(bpy.types.PropertyGroup):
    identifier: bpy.props.StringProperty(update=parameter_updated)
    float_value: bpy.props.FloatProperty(update=parameter_updated)
    int_value: bpy.props.IntProperty(update=parameter_updated)
    bool_value: bpy.props.BoolProperty(update=parameter_updated)
    enum_value: bpy.props.StringProperty(update=parameter_updated)


classes = (
    DRAGGABLEPROP_OT_subscribe,
    UBK_BakerParameterValue,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
