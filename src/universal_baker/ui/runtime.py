# from ..logger.runtime import logger, ui_sink
from ..constant import LOG
from ..logger.blender.redraw import BlenderRedrawAdapter

redraw_adapter = None


def register():
    global redraw_adapter

    ui_sink = LOG.get_sink("ui")
    if ui_sink is not None:
        redraw_adapter = BlenderRedrawAdapter(
            sink=ui_sink,
            space_types={"VIEW_3D"},
        )


def unregister():
    global redraw_adapter

    if redraw_adapter is not None:
        redraw_adapter.close()
        redraw_adapter = None
