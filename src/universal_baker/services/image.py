from __future__ import annotations

from pathlib import Path

import bpy
from universal_baker.baker.planner import BakePlanner

from ..baker.context import BakeContext
from ..resources.image import ImageResource


class ImageService:
    """Manage bake destination images."""

    @classmethod
    def acquire(cls, ctx: BakeContext) -> bpy.types.Image:
        """
        Acquire the destination image for this bake.
        """
        resource = ctx.image

        if resource.image is not None:
            return resource.image

        cls.configure(resource, ctx)

        image = bpy.data.images.get(resource.name)

        if image is None:
            image = cls.create(resource)

            resource.created = True

        resource.image = image

        cls.apply_settings(resource)

        return image

    @classmethod
    def save(cls, ctx: BakeContext) -> None:
        resource = ctx.image

        if resource.image is None:
            return

        if resource.filepath is None:
            return

        image = resource.image
        image.filepath_raw = str(resource.filepath)
        image.file_format = resource.file_format
        image.save()

        resource.mark_saved()

    @classmethod
    def release(cls, ctx: BakeContext) -> None:
        """
        Release temporary images.
        """
        resource = ctx.image

        if not resource.temporary:
            return

        if resource.image is None:
            return

        if resource.image.users == 0:
            bpy.data.images.remove(resource.image)

        resource.image = None

    @classmethod
    def configure(cls, resource: ImageResource, ctx: BakeContext) -> None:
        """
        Populate the resource from the BakeTask.
        """
        task = ctx.task

        #
        # MVP defaults.
        # Later these will come from OutputSettings.
        #

        resource.name = f"{task.object_name}_{task.baker_id.lower()}"
        resource.width = 2048
        resource.height = 2048
        resource.alpha = False
        resource.float_buffer = False
        resource.colorspace = "sRGB"
        resource.file_format = "PNG"
        resource.color_depth = "8"

        #
        # TODO
        #
        # Output directory service.
        #

        resource.filepath = Path(bpy.path.abspath("//")) / f"{resource.name}.png"

    @classmethod
    def create(cls, resource: ImageResource) -> bpy.types.Image:

        image = bpy.data.images.new(
            name=resource.name,
            width=resource.width,
            height=resource.height,
            alpha=resource.alpha,
            float_buffer=resource.float_buffer,
        )

        return image

    @classmethod
    def apply_settings(
        cls,
        resource: ImageResource,
    ) -> None:

        image = resource.image

        if image is None:
            return

        image.colorspace_settings.name = resource.colorspace
        image.alpha_mode = "STRAIGHT" if resource.alpha else "NONE"

    @classmethod
    def clear(cls, ctx: BakeContext) -> None:
        """
        Clear the bake target before rendering.
        """
        image = ctx.image.image

        if image is None:
            return

        image.generated_color = (0.0, 0.0, 0.0, 0.0)
        image.update()

    @classmethod
    def mark_dirty(cls, ctx: BakeContext) -> None:
        ctx.image.mark_dirty()

    @classmethod
    def find(cls, name: str) -> bpy.types.Image | None:
        return bpy.data.images.get(name)

    @classmethod
    def cleanup(cls, ctx: BakeContext) -> None:
        pass
