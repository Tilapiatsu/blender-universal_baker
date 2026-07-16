from . import (
    baker_list,
    object_list,
    packer_list,
    panel,
    panel_settings_baker,
    panel_settings_packer,
)

modules = (
    baker_list,
    object_list,
    packer_list,
    panel,
    panel_settings_baker,
    panel_settings_packer,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
