from . import (
    ambient_occlusion,
    curvature,
    normal_world_space,
    position,
)

modules = (
    ambient_occlusion,
    curvature,
    normal_world_space,
    position,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
