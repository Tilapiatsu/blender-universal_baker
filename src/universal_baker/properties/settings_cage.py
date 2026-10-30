from __future__ import annotations

import bpy
from bpy.props import EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy.types import Image, Object, PropertyGroup

from ..resources.asset_info import CageSkewInfo


def parameter_updated(self, context):
    from ..core.controller import BakeController
    from ..runtime.runtime_manager import RuntimeManager

    target = BakeController.active_target_object(context)

    if target is None:
        return

    runtime = RuntimeManager.get(context.scene).cage_visualization

    if runtime.active:
        runtime.request_preview_refresh()

    return runtime


def cage_extrusion_updated(self, context):
    runtime = parameter_updated(self, context)
    if runtime is None:
        return

    source_info = CageSkewInfo(
        uvmap=None,
        precision=None,
        skew_image=None,
        offset=self.cage_extrusion,
        offset_group=None,
        optimize_resample=None,
        skew=None,
    )

    runtime.refresh_skew_remesher_parameters(source_info=source_info)


def skew_precision_updated(self, context):
    runtime = parameter_updated(self, context)
    if runtime is None:
        return

    source_info = CageSkewInfo(
        uvmap=None,
        precision=self.skew_precision,
        skew_image=None,
        offset=None,
        offset_group=None,
        optimize_resample=None,
        skew=None,
    )

    runtime.refresh_skew_remesher_parameters(source_info=source_info)


def max_ray_distance_updated(self, context):
    if not context.scene.ubk_project.visualization.preview_bake:
        return

    from ..runtime.runtime_manager import RuntimeManager

    runtime = RuntimeManager.get(context.scene).cage_visualization

    if runtime.active:
        runtime.request_preview_refresh()

    runtime.refresh_max_ray_distance_preview_parameters(value=self.max_ray_distance)


def mode_updated(self, context):
    from ..core.controller import BakeController
    from ..runtime.runtime_manager import RuntimeManager

    target = BakeController.active_target_object(context)

    if target is None:
        return

    runtime = RuntimeManager.get(context.scene).cage_visualization

    if runtime.active and self.cage_mode == "OBJECT":
        from ..services.visualization_cage import CageVisualizationService

        CageVisualizationService.disable()

        visualization = BakeController.project(context).visualization

        visualization.cage_edit = False


class UBK_CageSettings(PropertyGroup):
    cage_mode: EnumProperty(
        name="Mode",
        items=[
            ("GENERATED", "Generated", "Automatically generate Cage by offsetting vertices along normal"),
            ("OBJECT", "Object", "Specify an object as the cage"),
        ],
        default="GENERATED",
        update=mode_updated,
    )

    # TODO: Need to prevent to load the same object as the target object
    cage_object_custom: PointerProperty(
        name="Cage Object",
        type=Object,
    )
    cage_object_generated: PointerProperty(
        name="Genertated Cage Object",
        type=Object,
    )
    cage_extrusion: FloatProperty(
        name="Cage Extrusion",
        default=0.1,
        min=0.0,
        subtype="DISTANCE",
        update=cage_extrusion_updated,
    )
    max_ray_distance: FloatProperty(
        name="Max Ray Distance",
        default=0.0,
        min=0.0,
        subtype="DISTANCE",
        description="The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit.",
        update=max_ray_distance_updated,
    )
    extrusion_group: StringProperty(
        name="Extrusion Group",
        default="UBK_EXTRUSION_GROUP",
    )
    skew_image: PointerProperty(name="Skew Image", type=Image)

    skew_precision: FloatProperty(
        name="Skew Precision",
        description="The distance between each bake projection is recalculate to prerform the skew correction",
        default=0.01,
        min=0.0001,
        subtype="DISTANCE",
        update=skew_precision_updated,
    )

    @property
    def cage_object(self) -> Object | None:
        match self.cage_mode:
            case "OBJECT":
                return self.cage_object_custom
            case "GENERATED":
                return self.cage_object_generated

    @property
    def is_cage_generated(self) -> bool:
        return self.cage_mode == "GENERATED"

    @property
    def is_skew_correction_enabled(self) -> bool:
        return self.skew_image is not None and self.is_cage_generated


classes = (UBK_CageSettings,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
