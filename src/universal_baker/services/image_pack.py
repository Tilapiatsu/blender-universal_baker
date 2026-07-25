from __future__ import annotations


from ..runtime.task_pack import PackingTask
from ..runtime.context import PackContext
from ..resources.pack import PackResource

from .image_base import ImageServiceBase


class ImageServicePack(ImageServiceBase):
    """Manage destination images."""

    @classmethod
    def create_pack_resource(cls, task: PackingTask, ctx: PackContext) -> PackResource:
        resource = PackResource(task, ctx)
        return resource
