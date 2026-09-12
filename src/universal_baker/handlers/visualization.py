from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

from ..core.controller import BakeController
from ..runtime.runtime_manager import RuntimeManager
from ..services.project_synchronizer import ProjectSynchronizer

suspension = None
visualization_mode = "NONE"
enabled_display = False
enabled_preview = False


@persistent
def ubk_load_post(_dummy):
    ProjectSynchronizer.synchronize_blend_file()


@persistent
def ubk_save_pre(_dummy):
    runtime = RuntimeManager.current(bpy.context)
    if runtime is None:
        return

    global suspension
    suspension = runtime.bake_visualization.do_suspend()

    if suspension.was_enabled:
        global visualization_mode
        global enabled_display
        global enabled_preview

        project = BakeController.project(bpy.context)
        visualization_mode = project.visualization.mode
        enabled_display = project.visualization.enabled_display
        enabled_preview = project.visualization.enabled_preview

        project.visualization.mode = "NONE"
        project.visualization.enabled_display = False
        project.visualization.enabled_preview = False


@persistent
def ubk_save_post(_dummy):
    global suspension

    if suspension is None:
        return

    suspension.restore()

    if suspension.was_enabled:
        global visualization_mode
        global enabled_display
        global enabled_preview

        project = BakeController.project(bpy.context)

        project.visualization.refreshing = True
        project.visualization.mode = visualization_mode
        project.visualization.enabled_display = enabled_display
        project.visualization.enabled_preview = enabled_preview
        project.visualization.refreshing = False


def register():
    if ubk_load_post not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.load_post.append(ubk_load_post)

    if ubk_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(ubk_save_pre)

    if ubk_save_post not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(ubk_save_post)


def unregister():
    if ubk_load_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.load_post.remove(ubk_load_post)

    if ubk_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(ubk_save_pre)

    if ubk_save_post in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(ubk_save_post)
