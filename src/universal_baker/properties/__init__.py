from . import (
    settings_output,
    settings_bake,
    settings_cage,
    settings_pack,
    baker,
    packer,
    object,
    bake_group,
    project,
)

modules = (
    settings_output,
    settings_bake,
    settings_cage,
    settings_pack,
    baker,
    packer,
    object,
    bake_group,
    project,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
