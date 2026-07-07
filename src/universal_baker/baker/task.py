import bpy
from ..properties.map import UBK_Map
from dataclasses import dataclass


@dataclass
class BakeTask:
    target: bpy.types.Object
    bake_map: UBK_Map
    # output_path: Path
    # image
    # status
    # progress
