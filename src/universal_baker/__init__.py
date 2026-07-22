bl_info = {
    "name": "Universal Baker",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "description": "Blender Baking Made Easy",
    "category": "Render",
}

# from . import registration
#
# modules = (registration,)

from . import (
    preferences,
    properties,
    output,
    ui,
    operators,
    bakers,
    executors,
)

modules = (
    preferences,
    properties,
    output,
    ui,
    operators,
    bakers,
    executors,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
