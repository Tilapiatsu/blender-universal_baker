import math
from pathlib import Path

import bpy
import gpu
import numpy as np


class GPUUdimAtlas:
    @classmethod
    def _get_udim_coordinates(cls, tile_number: int):
        """Convert a UDIM number into its original U/V coordinates."""

        index = tile_number - 1001

        if index < 0:
            raise ValueError(f"Invalid UDIM number: {tile_number}")

        return index % 10, index // 10

    @classmethod
    def _get_udim_tile_path(cls, filepath: str, tile_number: int):
        """Resolve the filepath of an individual UDIM tile."""

        if "<UDIM>" not in filepath:
            raise ValueError(f"UDIM filepath must contain <UDIM>: {filepath}")

        path = Path(filepath.replace("<UDIM>", str(tile_number)))

        if not path.is_file():
            raise FileNotFoundError(f"UDIM tile file not found: {path}")

        return path

    @classmethod
    def _read_udim_tile_size(cls, filepath: Path):
        """
        Read an individual tile's dimensions.

        The temporary Blender image is removed immediately.
        """

        tile_image = bpy.data.images.load(
            str(filepath),
            check_existing=False,
        )

        try:
            return tuple(tile_image.size[:])

        finally:
            bpy.data.images.remove(tile_image)

    @classmethod
    def _read_udim_tile_pixels(cls, filepath: Path):
        """
        Read the red channel of an individual UDIM tile.

        Returns a detached float32 NumPy array shaped (height, width).
        """

        tile_image = bpy.data.images.load(
            str(filepath),
            check_existing=False,
        )

        try:
            width, height = tile_image.size[:]

            rgba = np.empty(
                (height, width, 4),
                dtype=np.float32,
            )

            tile_image.pixels.foreach_get(rgba.ravel())

            # Copy the red channel before removing the image datablock.
            return rgba[:, :, 0].copy()

        finally:
            bpy.data.images.remove(tile_image)

    @classmethod
    def _pack_udim_tiles(cls, tile_sizes: dict[int, tuple[int, int]]):
        """
        Pack variable-sized UDIM rectangles into a compact atlas.

        Uses a simple shelf-packing algorithm.

        Args:
            tile_sizes:
                {tile_number: (width, height)}

        Returns:
            tile_mapping:
                {tile_number: (x, y, width, height)}

            atlas_size:
                (atlas_width, atlas_height)
        """

        if not tile_sizes:
            raise ValueError("No UDIM tiles to pack")

        # Estimate a reasonable atlas width based on total pixel area.
        total_area = sum(width * height for width, height in tile_sizes.values())

        max_width = max(width for width, height in tile_sizes.values())

        atlas_width = max(
            max_width,
            math.ceil(math.sqrt(total_area)),
        )

        # Sort largest rectangles first.
        sorted_tiles = sorted(
            tile_sizes.items(),
            key=lambda item: (
                -item[1][1],
                -item[1][0],
                item[0],
            ),
        )

        tile_mapping = {}

        x = 0
        y = 0
        shelf_height = 0

        for tile_number, (width, height) in sorted_tiles:
            # Start a new shelf if this rectangle doesn't fit.
            if x > 0 and x + width > atlas_width:
                y += shelf_height
                x = 0
                shelf_height = 0

            tile_mapping[tile_number] = (
                x,
                y,
                width,
                height,
            )

            x += width
            shelf_height = max(shelf_height, height)

        atlas_height = y + shelf_height

        return (
            tile_mapping,
            (atlas_width, atlas_height),
        )

    @classmethod
    def _create_gpu_texture(cls, pixels: np.ndarray, texture_format: str):
        """
        Create a GPU texture from a contiguous NumPy array.

        pixels:
            (height, width) for R32F
            (height, width, 4) for RGBA32F
        """

        pixels = np.ascontiguousarray(
            pixels,
            dtype=np.float32,
        )

        height, width = pixels.shape[:2]

        if pixels.ndim == 2:
            buffer_dimensions = (width, height)

        elif pixels.ndim == 3:
            channels = pixels.shape[2]
            buffer_dimensions = (width, height, channels)

        else:
            raise ValueError(f"Unsupported texture dimensions: {pixels.shape}")

        buffer = gpu.types.Buffer(
            "FLOAT",
            buffer_dimensions,
            pixels.ravel(),
        )

        texture = gpu.types.GPUTexture(
            (width, height),
            format=texture_format,
            data=buffer,
        )

        return texture

    @classmethod
    def create_udim_atlas(
        cls, image: bpy.types.Image
    ) -> tuple[
        gpu.types.GPUTexture,
        gpu.types.GPUTexture,
        tuple[int, int],
        tuple[int, int],
        dict[int, tuple[int, int, int, int]],
    ]:
        """
        Build a packed GPU atlas and a UDIM lookup texture.

        Supports:
            - Sparse UDIM layouts.
            - UDIM layouts not starting at 1001.
            - Missing UDIM tiles.
            - Different tile resolutions.

        Reads tile files from disk. Unsaved Texture Paint changes
        are not included by this implementation.

        Returns:
            atlas_texture
            lookup_texture
            atlas_size
            lookup_size
            tile_mapping
        """

        if image.source != "TILED":
            raise ValueError("Image must be a tiled image")

        filepath = bpy.path.abspath(image.filepath)

        if "<UDIM>" not in filepath:
            raise ValueError(f"Invalid UDIM filepath: {filepath}")

        # ---------------------------------------------------------
        # 1. Retrieve tile numbers and paths
        # ---------------------------------------------------------

        tile_numbers = sorted(tile.number for tile in image.tiles)

        if not tile_numbers:
            raise ValueError("Image contains no UDIM tiles")

        tile_paths = {
            number: cls._get_udim_tile_path(
                filepath,
                number,
            )
            for number in tile_numbers
        }

        # ---------------------------------------------------------
        # 2. Retrieve individual tile dimensions
        # ---------------------------------------------------------

        tile_sizes = {number: cls._read_udim_tile_size(path) for number, path in tile_paths.items()}

        # ---------------------------------------------------------
        # 3. Calculate packed atlas layout
        # ---------------------------------------------------------

        tile_mapping, atlas_size = cls._pack_udim_tiles(tile_sizes)

        atlas_width, atlas_height = atlas_size

        # Single-channel float32 pixel atlas.
        atlas_pixels = np.zeros(
            (atlas_height, atlas_width),
            dtype=np.float32,
        )

        # ---------------------------------------------------------
        # 4. Copy individual tile pixels into the atlas
        # ---------------------------------------------------------

        for tile_number, filepath in tile_paths.items():
            x, y, width, height = tile_mapping[tile_number]

            tile_pixels = cls._read_udim_tile_pixels(filepath)

            if tile_pixels.shape != (height, width):
                raise ValueError(f"UDIM {tile_number} changed resolution while building the atlas")

            atlas_pixels[
                y : y + height,
                x : x + width,
            ] = tile_pixels

        # ---------------------------------------------------------
        # 5. Build the UDIM lookup texture
        # ---------------------------------------------------------

        # U coordinates are 0..9.
        # V coordinates start at 0 and grow upwards.

        udim_coords = {number: cls._get_udim_coordinates(number) for number in tile_numbers}

        lookup_height = max(v for u, v in udim_coords.values()) + 1

        # RGBA:
        # R = atlas origin X, in pixels
        # G = atlas origin Y, in pixels
        # B = tile width, in pixels
        # A = tile height, in pixels
        lookup_pixels = np.zeros(
            (lookup_height, 10, 4),
            dtype=np.float32,
        )

        for tile_number, (tile_u, tile_v) in udim_coords.items():
            x, y, width, height = tile_mapping[tile_number]

            lookup_pixels[tile_v, tile_u] = (
                x,
                y,
                width,
                height,
            )

        # ---------------------------------------------------------
        # 6. Upload both textures to the GPU
        # ---------------------------------------------------------

        atlas_texture = cls._create_gpu_texture(
            atlas_pixels,
            "R32F",
        )

        lookup_texture = cls._create_gpu_texture(
            lookup_pixels,
            "RGBA32F",
        )

        # Lookup entries must never be interpolated.
        lookup_texture.filter_mode(False)
        lookup_texture.extend_mode("EXTEND")

        # Pixel atlas uses linear filtering.
        atlas_texture.filter_mode(True)
        atlas_texture.extend_mode("EXTEND")

        lookup_size = (10, lookup_height)

        return (
            atlas_texture,
            lookup_texture,
            atlas_size,
            lookup_size,
            tile_mapping,
        )
