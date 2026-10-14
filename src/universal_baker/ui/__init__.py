from . import (
    bake_group_list,
    baker_library_list,
    baker_list,
    baker_menu,
    packer_list,
    panel,
    panel_settings_bake_group,
    panel_settings_baker,
    panel_settings_object,
    panel_settings_output,
    panel_settings_packer,
    source_object_list,
    target_object_list,
)

modules = (
    bake_group_list,
    baker_list,
    target_object_list,
    source_object_list,
    packer_list,
    baker_library_list,
    baker_menu,
    panel,
    panel_settings_bake_group,
    panel_settings_object,
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
