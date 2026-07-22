from . import (
    settings_output,
    settings_bake,
    settings_cage,
    settings_pack,
    baker,
    packer,
    object,
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
    project,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
