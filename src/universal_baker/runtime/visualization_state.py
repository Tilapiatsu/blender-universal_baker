from __future__ import annotations

from dataclasses import dataclass, field

import bpy

from ..services.material_override import (
    MaterialSnapshot,
)


@dataclass(slots=True)
class ViewportState:
    """
    Runtime state of one 3D viewport.

    This is intentionally not stored in Blender properties.
    """

    shading_type: str
    color_type: str
    shading_light: str
    show_object_outline: bool
    show_xray: bool
    show_shadows: bool
    show_cavity: bool
    render_pass: str


@dataclass
class SceneVisualizationState:
    """
    Runtime state belonging to a Blender scene.
    """

    scene_name: str
    view_transform: str
    display_device: str
    exposure: float
    gamma: float
    render_engine: str | None = None
    material_overrides: dict[
        str,
        bpy.types.Material | None,
    ] = field(default_factory=dict)

    viewports: list[ViewportState] = field(default_factory=list)


@dataclass
class VisualizationState:
    """
    Runtime snapshot used to restore Blender after
    visualization is disabled.
    """

    scenes: dict[
        str,
        SceneVisualizationState,
    ] = field(default_factory=dict)

    material_snapshots: list[MaterialSnapshot] = field(default_factory=list)

    active: bool = False

    mode: str | None = None
