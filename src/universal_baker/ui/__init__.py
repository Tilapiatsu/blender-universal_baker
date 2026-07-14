from . import bake_settings_panel, map_list, object_list, panel

modules = (
    map_list,
    object_list,
    panel,
    bake_settings_panel,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
