from __future__ import annotations

import bpy

from .preferences import classes as preference_classes

# Future imports
#
# from .properties import classes as property_classes
# from .operators import classes as operator_classes
# from .ui import classes as ui_classes

# -----------------------------------------------------------------------------
# Class Registry
# -----------------------------------------------------------------------------


class ClassRegistry:
    """
    Centralized class registration.

    Every package exposes a `classes` tuple.

    registration.py imports them and concatenates them.
    """

    def __init__(self):

        self._classes: list[type] = []

    def add(self, *groups):

        for group in groups:
            self._classes.extend(group)

    @property
    def classes(self):

        return tuple(self._classes)


_registry = ClassRegistry()

_registry.add(
    preference_classes,
)

# -----------------------------------------------------------------------------
# Scene Properties
# -----------------------------------------------------------------------------


def register_scene_properties():

    #
    # Placeholder.
    #
    # Part 2 will register:
    #
    # Scene.ubk_project
    #
    pass


def unregister_scene_properties():

    #
    # Placeholder.
    #
    pass


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------


def register():

    for cls in _registry.classes:
        bpy.utils.register_class(cls)

    register_scene_properties()


def unregister():

    unregister_scene_properties()

    for cls in reversed(_registry.classes):
        bpy.utils.unregister_class(cls)
