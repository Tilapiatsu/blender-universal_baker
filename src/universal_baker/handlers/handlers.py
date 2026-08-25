from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

from ..core.controller import BakeController
from ..services.project_synchronizer import ProjectSynchronizer


@persistent
def ubk_load_post(_dummy):
    for scene in bpy.data.scenes:
        ProjectSynchronizer.synchronize_project(BakeController.project(scene))


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------


def register():
    if ubk_load_post not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.load_post.append(ubk_load_post)


def unregister():
    if ubk_load_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.load_post.remove(ubk_load_post)
