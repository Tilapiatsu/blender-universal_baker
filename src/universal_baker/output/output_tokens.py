from __future__ import annotations

import bpy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..properties.baker import UBK_Baker
    from ..properties.packer import UBK_Packer

from ..core.registry_token import registry_token


def get_variables(
    bake_group_name: str,
    baker: UBK_Baker | None,
    packer: UBK_Packer | None,
    image_name: str,
    scene: bpy.types.Scene,
    extension: str,
):
    return {
        "bake_group": bake_group_name,
        "baker": baker,
        "packer": packer,
        "image_name": image_name,
        "scene": scene,
        "extension": extension,
    }


def register():
    registry_token.register(
        "bake_group",
        lambda variables: variables["bake_group"],
    )
    registry_token.register(
        "baker",
        lambda variables: variables["baker"].baker if variables["baker"].baker else "",
    )
    registry_token.register(
        "packer",
        lambda variables: variables["packer"].name if variables["packer"].name else "",
    )
    registry_token.register(
        "image_name",
        lambda variables: variables["image_name"],
    )
    registry_token.register(
        "scene",
        lambda variables: variables["scene"].name,
    )
    registry_token.register(
        "blend",
        lambda variables: bpy.path.basename(bpy.data.filepath).split(".")[0],
    )
    registry_token.register(
        "extension",
        lambda variables: variables["extension"],
    )


def unregister():
    pass
