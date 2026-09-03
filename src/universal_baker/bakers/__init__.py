from . import (
    diffuse,
    albedo,
    custom,
)

modules = (
    diffuse,
    albedo,
    custom,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
