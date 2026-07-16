from __future__ import annotations
from typing import Callable

import bpy

from ..core.controller import BakeController

# -------------------------------------------------------------------------
# Draw Settings Functions
# -------------------------------------------------------------------------


def draw_global_output_settings(self, context, draw: Callable):
    project = BakeController.project(context)
    if project is None:
        return

    layout = self.layout

    settings_bake = project.settings_bake

    draw(layout, settings_bake)


# -------------------------------------------------------------------------
# Output Settings Panel
# -------------------------------------------------------------------------


def draw_output_settings(layout, settings):
    layout.use_property_split = True
    layout.use_property_decorate = False
    internal_data = BakeController.get_output_node(settings.internal_name)
    if internal_data is None:
        layout.label(text="Add a Target object and a Map first.", icon="INFO")
    else:
        layout.prop(settings, "resolution_x")
        layout.prop(settings, "resolution_y")
        layout.template_image_settings(internal_data.format, color_management=False)
