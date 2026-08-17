from __future__ import annotations

from pathlib import Path

import bpy

from ..constant import LOG
from ..resources.image import ImageResource
from ..runtime.task import Task
from ..enum.image_layout import ImageLayout
from ..services.uv import UVService
from ..runtime.settings_output import OutputSettings

LOG_SCOPE = "Image Service"


class ImageServiceBase:
    """Manage destination images."""

    @classmethod
    def init_resource(cls, image: bpy.types.Image, output_settings: OutputSettings) -> ImageResource:
        with LOG.scope(LOG_SCOPE):
            LOG.debug(f"Init Image Resource : {image.name}")
            resource = ImageResource.create(
                width=output_settings.path.width,
                height=output_settings.path.height,
                name=image.name,
                filepath=image.filepath_raw,
                colorspace=output_settings.color.colorspace,
                image_format_settings=output_settings.image,
                alpha=output_settings.image.alpha,
                float_buffer=output_settings.image.float_buffer,
                is_udim=len(image.tiles) > 1,
                create_image=False,
            )

            return resource

    @classmethod
    def acquire(cls, resource: ImageResource, task: Task) -> ImageResource:
        """
        Acquire the destination image for this task.
        """
        with LOG.scope(LOG_SCOPE):
            LOG.debug("Acquire image ...")

            if resource.image is not None:
                LOG.debug("Update existing Image")
                cls.configure(resource, task)
                return resource

            cls.configure(resource, task)

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
            resource.is_udim = task.uv_layout.image_layout == ImageLayout.UDIM
            LOG.debug(f"Configure Image to {task.uv_layout.image_layout}")

            resource.filepath = task.absolute_filepath

    @classmethod
    def create(cls, resource: ImageResource, tiles: tuple[tuple[int, int], ...] = ((0, 0),)) -> bpy.types.Image:
        with LOG.scope("Create"):
            if resource.tiles_has_changed(UVService.tile_numbers(tiles)):
                resource.remove_image()

            if resource.name not in bpy.data.images:
                LOG.debug(f"Create Image : {resource.name}")
                image = bpy.data.images.new(
                    name=resource.name,
                    width=resource.width,
                    height=resource.height,
                    alpha=resource.image_format_settings.alpha,
                    float_buffer=resource.image_format_settings.float_buffer,
                    tiled=resource.is_udim,
                )

                if resource.is_udim:
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
            generated_type=resource.generated_type,
            object_name=resource.object_name,
            map_name=resource.map_name,
            colorspace=resource.colorspace,
            is_data=resource.is_data,
            image_format_settings=resource.image_format_settings,
            is_copy=True,
        )
        resources_copy.filepath = resource.filepath
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

    @classmethod
    def add_udim_tiles_bak(cls, resource: ImageResource, tiles: tuple[tuple[int, int], ...]) -> None:
        LOG.debug("Adding UDIM Tile")
        image = resource.image

        if image is None:
            cls.create(resource, tiles)
            image = resource.image

        assert image is not None
        assert image.tiles is not None

        cls.clear_tiles(resource)

        for tile in tiles:
            number = UVService.tile_number(*tile)
            LOG.debug(f"create UDIM Tile {number}")
            image_tile = image.tiles.new(number, label=str(number))

        first_tile = image.tiles.get(1001)
        if first_tile is not None and 1001 not in UVService.tile_numbers(tiles):
            image.tiles.remove(first_tile)

        image.update()

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

        first_tile = image.tiles.get(1001)
        if first_tile is not None and 1001 not in UVService.tile_numbers(tiles):
            image.tiles.remove(first_tile)

        # restore old active image in the image_editor
        if old_active_image is not None:
            image_area.spaces.active.image = old_active_image

        # if context.area changed, restore back
        if context.area.ui_type != old_area_type and old_area_type is not None:
            context.area.ui_type = old_area_type

    @classmethod
    def clear_tiles(cls, resource: ImageResource):
        image = resource.image

        if image is None:
            return

        if image.tiles is None:
            return

        for tile in image.tiles.values():
            image.tiles.remove(tile)
