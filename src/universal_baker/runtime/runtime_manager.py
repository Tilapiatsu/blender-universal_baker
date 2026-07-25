from __future__ import annotations

import bpy

from .runtime import BakeRuntime


class RuntimeManager:
    """
    Singleton responsible for managing BakeRuntime instances.

    One runtime exists for each Blender Scene.

    The runtime is NOT serialized inside the .blend file.
    """

    _runtimes: dict[int, BakeRuntime] = {}

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    @classmethod
    def _scene_key(cls, scene: bpy.types.Scene) -> int:
        """
        Returns a unique runtime key for a Scene.
        """

        return scene.as_pointer()

    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------

    @classmethod
    def get(cls, scene: bpy.types.Scene) -> BakeRuntime:
        """
        Returns the runtime associated with a Scene.

        Creates it if necessary.
        """

        key = cls._scene_key(scene)
        runtime = cls._runtimes.get(key)

        if runtime is None:
            runtime = BakeRuntime(scene)
            cls._runtimes[key] = runtime

        return runtime

    @classmethod
    def current(cls, context) -> BakeRuntime:
        return cls.get(context.scene)

    @classmethod
    def has_runtime(cls, scene) -> bool:
        return cls._scene_key(scene) in cls._runtimes

    @classmethod
    def destroy(cls, scene):
        """
        Destroys the runtime associated with a Scene.
        """
        key = cls._scene_key(scene)
        runtime = cls._runtimes.pop(key, None)

        if runtime is None:
            return

        runtime.clear()

    @classmethod
    def clear(cls):
        """
        Removes every runtime.
        """

        for runtime in cls._runtimes.values():
            runtime.clear()

        cls._runtimes.clear()

    @classmethod
    def all(cls):
        return tuple(cls._runtimes.values())

    @classmethod
    def statistics(cls):
        return {
            "runtime_count": len(cls._runtimes),
            "output_count": sum(runtime.outputs.count for runtime in cls._runtimes.values()),
            "active_sessions": sum(len(runtime.active_sessions) for runtime in cls._runtimes.values()),
        }
