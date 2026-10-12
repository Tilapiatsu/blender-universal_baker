from . import (
    albedo,
    custom,
    diffuse,
    normal,
)

modules = (
    diffuse,
    albedo,
    custom,
    normal,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
