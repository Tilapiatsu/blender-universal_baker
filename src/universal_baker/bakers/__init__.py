from . import (
    diffuse,
    custom,
)

modules = (
    diffuse,
    custom,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
