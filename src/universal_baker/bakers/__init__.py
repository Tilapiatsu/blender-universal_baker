from . import (
    albedo,
    diffuse,
    normal,
)

modules = (
    diffuse,
    albedo,
    normal,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
