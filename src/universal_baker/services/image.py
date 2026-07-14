from __future__ import annotations

from pathlib import Path

import bpy
from universal_baker import ressources
from ..runtime.context import BakeContext
from ..ressources.image import ImageResource


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

        elif cls.is_image_settings_changed(image, resource):
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
        image.file_format = resource.image_format_settings.file_format
        image.save()

        resource.mark_saved()

    @classmethod
    def remove(cls, image: bpy.types.Image) -> None:
        bpy.data.images.remove(bpy.data.images[image.name])

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

        image_settings = ctx.bake_settings.image
        color_settings = ctx.bake_settings.color
        resource.name = f"{task.object_name}_{task.baker_id.lower()}"
        resource.width = image_settings.width
        resource.height = image_settings.height
        resource.colorspace = color_settings.colorspace
        resource.image_format_settings = image_settings

        #
        # TODO:
        # Output directory service.
        #

        resource.filepath = Path(bpy.path.abspath("//")) / f"{resource.name}.png"

    @classmethod
    def create(cls, resource: ImageResource) -> bpy.types.Image:
        if resource.name not in bpy.data.images:
            image = bpy.data.images.new(
                name=resource.name,
                width=resource.width,
                height=resource.height,
                alpha=resource.image_format_settings.alpha,
                float_buffer=resource.image_format_settings.float_buffer,
            )
        else:
            image = cls.find(resource.name)
            assert image is not None
            image.scale(resource.width, resource.height)
            # image.update()
            image.pack()

        return image

    @classmethod
    def is_image_settings_changed(cls, image: bpy.types.Image, resource: ImageResource) -> bool:
        if (
            image.size[0] != resource.width
            or image.size[1] != resource.height
            or ((image.channels == 4) != resource.image_format_settings.alpha)
            # or image.colorspace_settings.name != ressources.image_format_settings.colorspace
        ):
            return True

        return False

    @classmethod
    def apply_settings(cls, resource: ImageResource) -> None:
        image = resource.image

        if image is None:
            return

        image.colorspace_settings.name = resource.colorspace
        image.alpha_mode = "STRAIGHT" if resource.image_format_settings.alpha else "NONE"

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
