from __future__ import annotations

from pathlib import Path

import bpy

from ..constant import LOG
from ..resources.image import ImageResource
from ..runtime.task import Task

LOG_SCOPE = "Image Service"


class ImageServiceBase:
    """Manage destination images."""

    @classmethod
    def init_resource(cls, image: bpy.types.Image) -> ImageResource:
        resource = ImageResource(image)
        resource.init_from_image()
        return resource

    @classmethod
    def acquire(
        cls, resource: ImageResource, task: Task, suffix: str | None = None, sub_folder: str | None = None
    ) -> ImageResource:
        """
        Acquire the destination image for this bake.
        """
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Acquire image ...")

            if resource.image is not None:
                LOG.debug("Update existing Image")
                cls.configure(resource, task, suffix, sub_folder)
                return resource

            cls.configure(resource, task, suffix, sub_folder)

            image = bpy.data.images.get(resource.name)

            if image is None:
                image = cls.create(resource)
                resource.created = True

            elif cls.is_image_settings_changed(image, resource):
                image = cls.create(resource)
                resource.created = True

            resource.image = image

            cls.apply_settings(resource)

            return resource

    @classmethod
    def save(cls, resource: ImageResource) -> None:
        with LOG.scope("Save"):
            LOG.debug(f'Save Image Resource "{resource.name}" : {resource.filepath}')

            if resource.image is None:
                return

            image = resource.image
            image.filepath_raw = str(resource.filepath)
            image.file_format = resource.image_format_settings.file_format
            image.save()
            image.pack()

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
    def configure(
        cls,
        resource: ImageResource,
        task: Task,
        suffix: str | None = None,
        sub_folder: str | None = None,
    ) -> None:
        """
        Populate the resource from the Task.
        """
        with LOG.scope("Configure"):
            LOG.debug(f"Setting up ressource from task {task.output_name}")

            image_settings = task.output_context.output_settings.image
            color_settings = task.output_context.output_settings.color
            path_settings = task.output_context.output_settings.path

            resource.name = task.output_name
            resource.width = path_settings.width
            resource.height = path_settings.height
            resource.colorspace = color_settings.colorspace
            resource.image_format_settings = image_settings
            # TODO: Need to pipe the information about the use of UDIM properly to the image resource

            resource.filepath = cls.resolve_filepath(task, suffix, sub_folder)

    @classmethod
    def resolve_filepath(cls, task: Task, suffix: str | None = None, sub_folder: str | None = None) -> Path:
        from ..core.output_resolver import OutputResolver

        file_output = OutputResolver.resolve(task.output_context, suffix, sub_folder)
        return file_output.absolute_path

    @classmethod
    def create(cls, resource: ImageResource) -> bpy.types.Image:
        with LOG.scope("Create"):
            if resource.name not in bpy.data.images:
                LOG.debug(f"Create Image : {resource.name}")
                image = bpy.data.images.new(
                    name=resource.name,
                    width=resource.width,
                    height=resource.height,
                    alpha=resource.image_format_settings.alpha,
                    float_buffer=resource.image_format_settings.float_buffer,
                )
            else:
                LOG.debug(f"Image found : {resource.name}")
                image = cls.find(resource.name)
                assert image is not None
                image.scale(resource.width, resource.height)
                image.filepath_raw = str(resource.filepath)
                # image.update()
                image.pack()

            return image

    @classmethod
    def copy(cls, resource: ImageResource) -> ImageResource:
        image_copy = resource.image.copy() if resource.image is not None else None
        resources_copy = ImageResource(
            image=image_copy,
            name=image_copy.name if image_copy is not None else "",
            filepath=resource.filepath,
            generated_type=resource.generated_type,
            object_name=resource.object_name,
            map_name=resource.map_name,
            colorspace=resource.colorspace,
            is_data=resource.is_data,
            image_format_settings=resource.image_format_settings,
            is_copy=True,
        )

        return resources_copy

    @classmethod
    def is_image_settings_changed(cls, image: bpy.types.Image, resource: ImageResource) -> bool:
        return (
            image.size[0] != resource.width
            or image.size[1] != resource.height
            or ((image.channels == 4) != resource.image_format_settings.alpha)
            or image.filepath_raw != str(resource.filepath)
            # or image.colorspace_settings.name != resources.image_format_settings.colorspace
        )

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
        resource.reset()

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
                r = cls.copy(r)
                r.scale(width, height)
