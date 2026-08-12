from __future__ import annotations


from ..runtime.task_pack import PackingTask
from ..runtime.context_pack import PackContext
from ..resources.pack import PackResource

from .image_base import ImageServiceBase


class ImagePackService(ImageServiceBase):
    """Manage destination images."""

    @classmethod
    def create_pack_resource(cls, task: PackingTask, ctx: PackContext) -> PackResource:
        resource = PackResource(task, ctx)
        return resource
