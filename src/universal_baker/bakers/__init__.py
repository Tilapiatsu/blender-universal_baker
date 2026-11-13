from . import (
    albedo,
    diffuse,
    normal,
    roughness,
)

modules = (
    diffuse,
    albedo,
    normal,
    roughness,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
