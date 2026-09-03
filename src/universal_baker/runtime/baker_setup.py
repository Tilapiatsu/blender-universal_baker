from __future__ import annotations

from dataclasses import dataclass, field
import bpy

from ..constant import LOG
from ..services.bake_material import BakeMaterialSetup

LOG_SCOPE = "Baker Asset"


@dataclass
class BakerSetup:
    """
    Temporary Blender state created for one custom baker operation.
    """

    target: bpy.types.Object | None = None
    temporary_objects: list[bpy.types.Object] = field(default_factory=list)
    temporary_materials: list[bpy.types.Material] = field(default_factory=list)
    temporary_modifiers: list[tuple[bpy.types.Object, str]] = field(default_factory=list)
    material_setup: BakeMaterialSetup | None = None

    def cleanup(self) -> None:
        """
        Remove all temporary Blender datablocks created by this setup.
        """
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Cleaning up BakerSetup")

            if self.material_setup is not None:
                self.material_setup.cleanup()
                self.material_setup = None

            # Objects first.
            for obj in list(self.temporary_objects):
                if obj is None:
                    continue

                if obj.name in bpy.data.objects:
                    LOG.debug(f"Remove Temporary Object: {obj.name}")
                    bpy.data.objects.remove(
                        obj,
                        do_unlink=True,
                    )

            self.temporary_objects.clear()

            # Materials created specifically by the setup.
            for material in list(self.temporary_materials):
                if material is None:
                    continue

                if material.name in bpy.data.materials:
                    LOG.debug(f"Remove Temporary Material: {material.name}")
                    bpy.data.materials.remove(
                        material,
                        do_unlink=True,
                    )

            self.temporary_materials.clear()

            self.temporary_modifiers.clear()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.cleanup()

        return False


@dataclass
class BakerExecution:
    target: bpy.types.Object
    setup: BakerSetup | None = None

    def cleanup(self):
        if self.setup is not None:
            self.setup.cleanup()
