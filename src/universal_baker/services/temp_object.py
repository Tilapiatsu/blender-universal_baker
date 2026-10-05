from __future__ import annotations

import bpy


class TempObject:
    def __init__(self, new_obj: bpy.types.Object, backup_obj: bpy.types.Object, cleanup: bool = False) -> None:
        self._object = new_obj.name
        self._backup_object = backup_obj.name
        self._cleanup = cleanup

    @property
    def object(self) -> bpy.types.Object | None:
        obj = bpy.data.objects.get(self._object)

        return obj

    @property
    def backup_object(self) -> bpy.types.Object | None:
        obj = bpy.data.objects.get(self._backup_object)

        return obj

    def cleanup(self) -> None:
        if self.object is None or not self._cleanup:
            return

        bpy.data.objects.remove(self.object)

    def __enter__(self):
        return self.object

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
