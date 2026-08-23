from . import (
    baker_parameter,
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

modules = (
    baker_parameter,
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
