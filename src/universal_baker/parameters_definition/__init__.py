from . import (
    baker_settings,
    cage,
)

modules = (
    baker_settings,
    cage,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
