from __future__ import annotations

import bpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties.baker import UBK_Baker
    from ..properties.packer import UBK_Packer

from ..core.registry_token import registry_token


def get_variables(
    obj: bpy.types.Object,
    baker: UBK_Baker | None,
    packer: UBK_Packer | None,
    image_name: str,
    scene: bpy.types.Scene,
    extension: str,
):
    return {
        "object": obj,
        "baker": baker,
        "packer": packer,
        "image_name": image_name,
        "scene": scene,
        "extension": extension,
    }


def register():
    registry_token.register(
        "object",
        lambda ctx: ctx.variables["object"].name,
    )
    registry_token.register(
        "baker",
        lambda ctx: ctx.variables["baker"].baker if ctx.variables["baker"].baker else "",
    )
    registry_token.register(
        "packer",
        lambda ctx: ctx.variables["packer"].name if ctx.variables["packer"].name else "",
    )
    registry_token.register(
        "image_name",
        lambda ctx: ctx.variables["image_name"],
    )
    registry_token.register(
        "scene",
        lambda ctx: ctx.variables["scene"].name,
    )
    registry_token.register(
        "blend",
        lambda ctx: bpy.path.basename(bpy.data.filepath).split(".")[0],
    )
    registry_token.register(
        "extension",
        lambda ctx: ctx.variables["extension"],
    )


def unregister():
    pass
