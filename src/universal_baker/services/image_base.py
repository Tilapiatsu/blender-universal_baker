from __future__ import annotations

from pathlib import Path

import bpy
from ..runtime.settings_output import OutputSettings
from ..ressources.image import ImageResource
from ..runtime.task import Task


class ImageServiceBase:
    """Manage destination images."""

    @classmethod
    def acquire(cls, resource: ImageResource, settings: OutputSettings, task: Task) -> bpy.types.Image:
        """
        Acquire the destination image for this bake.
        """

        if resource.image is not None:
            return resource.image

        cls.configure(resource, settings, task)

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
    def save(cls, resource: ImageResource) -> None:
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
    def release(cls, resource: ImageResource) -> None:
        """
        Release temporary images.
        """

        if not resource.temporary:
            return

        if resource.image is None:
            return

        if resource.image.users == 0:
            bpy.data.images.remove(resource.image)

        resource.image = None

    @classmethod
    def configure(cls, resource: ImageResource, settings: OutputSettings, task: Task) -> None:
        """
        Populate the resource from the Task.
        """

        image_settings = settings.image
        color_settings = settings.color
        resource.name = task.output_name
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
    def clear(cls, resource: ImageResource) -> None:
        """
        Clear the bake target before rendering.
        """
        image = resource.image

        if image is None:
            return

        image.generated_color = (0.0, 0.0, 0.0, 0.0)
        image.update()

    @classmethod
    def mark_dirty(cls, resource: ImageResource) -> None:
        resource.mark_dirty()

    @classmethod
    def find(cls, name: str) -> bpy.types.Image | None:
        return bpy.data.images.get(name)

    @classmethod
    def cleanup(cls, resource: ImageResource) -> None:
        pass

    @classmethod
    def ensure_image_sizes(cls, *resources: ImageResource) -> None:
        """Ensure all imputed resources have the same size by scaling them to the highest resolution"""
        if not resources:
            return

        width: int = 0
        height: int = 0
        for r in resources:
            width = max(width, r.width)
            height = max(height, r.height)

        for r in resources:
            if r.width != width or r.height != height:
                r.scale(width, height)
