from __future__ import annotations

import bpy


class TempCollection:
    def __init__(self, name: str, objects: list[bpy.types.Object]) -> None:
        self.collection_name = name
        self._objects = [o.name for o in objects]
        self._collection_objects = []

    @property
    def objects(self) -> list[bpy.types.Object]:
        objects = [bpy.data.objects.get(o) for o in self._objects if bpy.data.objects.get(o) is not None]

        return objects

    @property
    def collection(self) -> bpy.types.Collection:
        return bpy.data.collections.get(self.collection_name)

    def create(self) -> None:
        self._create_temporary_collection()
        for o in self.objects:
            self._link_object_to_temporary_collection(o)

    def _create_temporary_collection(self) -> None:
        collection = bpy.data.collections.get(self.collection_name)

        if collection is None:
            collection = bpy.data.collections.new(self.collection_name)

        # Link to the current scene collection.
        bpy.context.scene.collection.children.link(collection)

    def _link_object_to_temporary_collection(
        self,
        obj: bpy.types.Object,
    ) -> None:
        if self.collection is None:
            return

        if self.collection.objects.get(obj.name) is not None:
            return

        self.collection.objects.link(obj)
        self._collection_objects.append(obj.name)

    def cleanup(self) -> None:
        if self.collection is None:
            return

        # Remove only the links that this service created.
        for object_name in self._collection_objects:
            obj = bpy.data.objects.get(object_name)

            if obj is None:
                continue

            if self.collection.objects.get(obj.name) is not None:
                self.collection.objects.unlink(obj)

        # Now the temporary collection should be empty.
        #
        # Since we created it ourselves, it is safe to remove.
        bpy.data.collections.remove(self.collection)

    def __enter__(self):
        return self.create()

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
