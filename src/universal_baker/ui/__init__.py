from . import (
    baker_list,
    object_list,
    packer_list,
    panel,
    panel_settings_baker,
    panel_settings_packer,
    panel_settings_output,
)


modules = (
    baker_list,
    object_list,
    packer_list,
    panel,
    panel_settings_baker,
    panel_settings_packer,
    panel_settings_output,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
