from __future__ import annotations

import bpy
from bpy.props import BoolProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup

from ..services.bake_visualization import update_visualization
from ..services.cage_visualization import update_active_target
from .artifact import UBK_Artifact
from .bake_group import UBK_BakeGroup
from .settings_bake import UBK_BakeSettings
from .visualization import UBK_Visualization


def update_active_bake_group(self, context):
    update_visualization(self, context)
    update_active_target(self, context)


class UBK_Project(PropertyGroup):
    """Scene baking project."""

    project_name: bpy.props.StringProperty(
        name="Project Name",
        default="Bake Project",
    )
    bake_groups: CollectionProperty(type=UBK_BakeGroup)
    active_bake_group_index: bpy.props.IntProperty(
        default=0,
        update=update_active_bake_group,
    )
    settings_bake: PointerProperty(type=UBK_BakeSettings)
    artifacts: CollectionProperty(
        type=UBK_Artifact,
    )
    visualization: PointerProperty(
        type=UBK_Visualization,
    )
    use_maskers: BoolProperty(
        name="Use Maskers",
        default=True,
        description="A bit slower, but ensure that the bake results does NOT overlap with a large margin and with multiple target objects",
    )


classes = (UBK_Project,)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.ubk_project = PointerProperty(type=UBK_Project)


def unregister():
    del bpy.types.Scene.ubk_project

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
