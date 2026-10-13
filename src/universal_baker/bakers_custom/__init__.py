from . import (
    ambient_occlusion,
    curvature,
)

modules = (
    ambient_occlusion,
    curvature,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
