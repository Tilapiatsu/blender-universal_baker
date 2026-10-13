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
    accumulators,
    assets,
    bakers,
    bakers_custom,
    compositors,
    executors,
    handlers,
    maskers,
    operators,
    output,
    packers,
    parameters_definition,
    preferences,
    properties,
    ui,
)

modules = (
    preferences,
    output,
    ui,
    operators,
    bakers,
    bakers_custom,
    parameters_definition,
    properties,
    executors,
    compositors,
    packers,
    accumulators,
    maskers,
    handlers,
    assets,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
