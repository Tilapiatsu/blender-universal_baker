from . import (
    ambient_occlusion,
    curvature,
    id,
    normal_world_space,
    position,
    thickness,
)

modules = (
    ambient_occlusion,
    curvature,
    normal_world_space,
    position,
    thickness,
    id,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
