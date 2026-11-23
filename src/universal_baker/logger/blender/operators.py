import bpy


# A sink registry keeps Blender operators independent of addon package paths.
# The runtime registers its UISink and passes the returned key to the operator.
_SINKS = {}


def register_sink(sink):
    key = str(id(sink))
    _SINKS[key] = sink
    sink._blender_registry_key = key
    return key


def unregister_sink(key):
    sink = _SINKS.pop(key, None)
    if sink is not None and getattr(sink, "_blender_registry_key", None) == key:
        delattr(sink, "_blender_registry_key")


def clear_registered_sinks():
    for key in tuple(_SINKS):
        unregister_sink(key)


class LOGGER_OT_ToggleEntry(bpy.types.Operator):
    bl_idname = "logger.toggle_entry"
    bl_label = "Toggle Log Entry"
    bl_description = "Expand or collapse this log entry"
    bl_options = {'INTERNAL'}

    sink_key: bpy.props.StringProperty(options={'HIDDEN'})
    entry_id: bpy.props.IntProperty(options={'HIDDEN'})
    action: bpy.props.EnumProperty(
        items=(
            ('TOGGLE_EXPANDED', "Toggle Entry", ""),
            ('TOGGLE_DETAILS', "Toggle Details", ""),
        ),
        options={'HIDDEN'},
    )

    def execute(self, context):
        sink = _SINKS.get(self.sink_key)
        if sink is None:
            return {'CANCELLED'}

        if self.action == 'TOGGLE_EXPANDED':
            changed = sink.toggle_entry(self.entry_id)
        else:
            changed = sink.toggle_details(self.entry_id)

        return {'FINISHED'} if changed else {'CANCELLED'}
