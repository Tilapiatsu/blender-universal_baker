from __future__ import annotations

from typing import TYPE_CHECKING


from .output_repository import OutputRepository
from ..services.output_provider import OutputProvider
from .artifact_repository import ArtifactRepository
from .runtime_visualization import VisualizationRuntime

if TYPE_CHECKING:
    from bpy.types import Scene


class BakeRuntime:
    """
    Runtime data associated with one Blender scene.

    This object only exists while Blender is running.

    It owns every temporary resource created during baking,
    previewing and exporting.

    Nothing stored here is serialized inside the .blend file.
    """

    outputs: OutputRepository
    provider: OutputProvider
    visualization: VisualizationRuntime

    def __init__(self, scene: Scene):

        self._scene = scene

        self.artifacts = ArtifactRepository(
            scene.name,
        )

        #
        # Runtime repositories
        #
        self.outputs = OutputRepository(self.artifacts)

        #
        # High level services
        #
        self.provider = OutputProvider(
            repository=self.outputs,
        )

        self.visualization = VisualizationRuntime()

        #
        # Future runtime objects
        #
        self.preview_cache = {}
        self.image_cache = {}
        self.statistics = {}
        self.active_sessions = []

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def scene(self) -> Scene:
        return self._scene

    # ---------------------------------------------------------
    # Runtime lifecycle
    # ---------------------------------------------------------

    def clear(self):
        """
        Clears every runtime resource.

        Called when:
            - user requests a reset
            - scene changes
            - runtime is destroyed
        """

        self.outputs.clear()
        self.provider.clear()
        self.preview_cache.clear()
        self.visualization.clear()
        self.image_cache.clear()
        self.statistics.clear()
        self.active_sessions.clear()

    def register_session(self, session):
        if session not in self.active_sessions:
            self.active_sessions.append(session)

    def unregister_session(self, session):
        if session in self.active_sessions:
            self.active_sessions.remove(session)

    def has_active_sessions(self) -> bool:
        return bool(self.active_sessions)

    def __repr__(self):
        return (
            f"<BakeRuntime scene='{self.scene.name}' outputs={self.outputs.count} sessions={len(self.active_sessions)}>"
        )
