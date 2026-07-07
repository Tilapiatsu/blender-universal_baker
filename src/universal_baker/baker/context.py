import bpy
from dataclasses import dataclass


@dataclass
class BakeContext:
    previous_active: bpy.types.Object
    previous_selected: bpy.types.Object
    temporary_materials: bpy.types.Material
    temporary_images: bpy.types.Image
