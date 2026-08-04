from __future__ import annotations

from pathlib import Path

import bpy

from ..constant import LOG
from ..resources.image import ImageResource
from ..runtime.task import Task
from ..enum.image_layout import ImageLayout
from ..services.uv import UVService

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
                image = cls.create(resource, task.uv_layout.udim_tiles)
                resource.created = True

            elif cls.is_image_settings_changed(image, resource):
                image = cls.create(resource, task.uv_layout.udim_tiles)
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
            # TODO : saving image in UDIM Format need to have a filename with .100X suffix in it. But How to make sure
            # each tiles have the proper name ?
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
            resource.tiles = task.uv_layout.image_layout == ImageLayout.UDIM
            LOG.debug(f"Configure Image to {task.uv_layout.image_layout}")

            resource.filepath = cls.resolve_filepath(task, suffix, sub_folder)

    @classmethod
    def resolve_filepath(cls, task: Task, suffix: str | None = None, sub_folder: str | None = None) -> Path:
        from ..core.output_resolver import OutputResolver

        file_output = OutputResolver.resolve(task.output_context, suffix, sub_folder)
        return file_output.absolute_path

    @classmethod
    def create(cls, resource: ImageResource, tiles: tuple[tuple[int, int], ...]) -> bpy.types.Image:
        with LOG.scope("Create"):
            if resource.name not in bpy.data.images:
                LOG.debug(f"Create Image : {resource.name}")
                image = bpy.data.images.new(
                    name=resource.name,
                    width=resource.width,
                    height=resource.height,
                    alpha=resource.image_format_settings.alpha,
                    float_buffer=resource.image_format_settings.float_buffer,
                    tiled=resource.tiles,
                )

                if resource.tiles:
                    resource.image = image
                    cls.add_udim_tiles(resource, tiles)
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

    # https://blender.stackexchange.com/questions/274964/how-to-add-udim-tiles-to-an-image-and-fill-them-via-python
    @classmethod
    def add_udim_tiles(cls, resource: ImageResource, tiles: tuple[tuple[int, int], ...]) -> None:
        context = bpy.context
        areas = context.screen.areas
        image = resource.image

        assert image is not None

        image_area = None
        image_screen = None
        image_region = None
        old_area_type = None

        # NOTE: it is possible to find image/uv editor and execute fill there
        # but for some reason **context incorrect** error appears every time
        # finding image_editor area to exec image OTs
        # for screen in bpy.data.screens:
        #     for area in screen.areas:
        #         if area.ui_type in ['IMAGE_EDITOR', 'UV']:
        #             image_area = area
        #             for region in area.regions:
        #                 print(region.height, region.type)
        #                 if region.type == 'WINDOW':
        #                     image_region = region
        #             # XXX don't know if there's always a WINDOW region
        #             if image_region is None:
        #                 image_region = area.regions[0]
        #             image_screen = screen
        #             break

        # NOTE: but looks like it works with just changing current area
        # if not found: change context.area ui_type
        if any([image_area is None, image_screen is None]):
            old_area_type = context.area.ui_type
            context.area.ui_type = "UV"
            image_area = context.area
            for region in image_area.regions:
                if region.type == "WINDOW":
                    image_region = region
            # XXX don't know if there's always a WINDOW region
            if image_region is None:
                image_region = context.area.regions[0]
            image_screen = context.screen

        # set image_editor active image
        old_active_image = image_area.spaces.active.image
        image_area.spaces.active.image = image

        # overriding context to avoid RuntimeError
        context_overridden = context.copy()
        context_overridden["area"] = image_area
        context_overridden["screen"] = image_screen
        context_overridden["region"] = image_region

        with bpy.context.temp_override(area=image_area, screen=image_screen, region=image_region):
            for tile in tiles:
                bpy.ops.image.tile_add(
                    number=UVService.tile_number(*tile),
                    label="",
                    fill=True,
                    # color=color,
                    generated_type=resource.generated_type,
                    width=resource.width,
                    height=resource.height,
                    float=resource.float_buffer,
                    alpha=resource.channels == 4,
                )

        # restore old active image in the image_editor
        if old_active_image is not None:
            image_area.spaces.active.image = old_active_image
        # if context.area changed, restore back
        if context.area.ui_type != old_area_type and old_area_type is not None:
            context.area.ui_type = old_area_type
