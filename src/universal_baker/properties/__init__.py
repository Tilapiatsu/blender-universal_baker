from . import (
    artifact,
    bake_group,
    baker,
    custom_baker,
    object,
    packer,
    parameter_value,
    project,
    settings_bake,
    settings_cage,
    settings_output,
    settings_pack,
    visualization,
)

modules = (
    parameter_value,
    custom_baker,
    settings_output,
    settings_bake,
    settings_cage,
    settings_pack,
    baker,
    packer,
    object,
    bake_group,
    artifact,
    visualization,
    project,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
