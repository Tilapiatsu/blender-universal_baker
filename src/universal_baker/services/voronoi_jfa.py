from __future__ import annotations

import numpy as np
from typing import Mapping

from universal_baker.resources.label_buffer import LabelBuffer
from universal_baker.runtime.tile_set import TileSet

from ..runtime.label_set import LabelSet


class VoronoiJFA:
    @staticmethod
    def _build_seed_map(
        objects: Mapping[str, TileSet],
    ) -> tuple[
        dict[int, np.ndarray],
        dict[int, str],
    ]:
        """
        Build:

            tile -> object label image

        Returns the mapping between integer labels and
        object names.
        """

        object_ids = {name: index for index, name in enumerate(objects.keys(), start=1)}

        labels_to_objects = {index: name for name, index in object_ids.items()}

        tile_numbers = set()

        for tileset in objects.values():
            tile_numbers.update(tileset.keys())

        result = {}

        for tile_number in tile_numbers:
            tile_arrays = []

            for object_name, tileset in objects.items():
                if tile_number not in tileset.tiles:
                    continue
                tile = tileset[tile_number]

                if tile is None:
                    continue

                array = tile.pixels

                tile_arrays.append(
                    (
                        object_ids[object_name],
                        array,
                    )
                )

            if not tile_arrays:
                continue

            shape = tile_arrays[0][1].shape

            seeds = np.zeros(
                shape,
                dtype=np.int32,
            )

            for object_id, mask in tile_arrays:
                if mask.shape != shape:
                    raise ValueError(f"Tile {tile_number} has inconsistent resolution.")

                occupied = mask != 0

                # First object wins if UVs overlap.
                seeds[occupied & (seeds == 0)] = object_id

            result[tile_number] = seeds

        return result, labels_to_objects

    @staticmethod
    def _jump_flood(
        seeds: np.ndarray,
    ) -> np.ndarray:
        """
        Compute Voronoi ownership using the Jump Flooding Algorithm.

        Parameters
        ----------
        seeds:
            2D int32 array.

            0 = empty
            >0 = object ownership label

        Returns
        -------
        np.ndarray
            2D int32 array containing the nearest object label.
        """

        height, width = seeds.shape

        yy, xx = np.indices(
            (height, width),
            dtype=np.int32,
        )

        seed_x = np.full(
            (height, width),
            -1,
            dtype=np.int32,
        )

        seed_y = np.full(
            (height, width),
            -1,
            dtype=np.int32,
        )

        owner = np.zeros(
            (height, width),
            dtype=np.int32,
        )

        occupied = seeds != 0

        seed_x[occupied] = xx[occupied]
        seed_y[occupied] = yy[occupied]
        owner[occupied] = seeds[occupied]

        # Largest power of two >= image dimension.
        step = 1

        while step < max(width, height):
            step <<= 1

        step >>= 1

        while step >= 1:
            best_x = seed_x.copy()
            best_y = seed_y.copy()
            best_owner = owner.copy()

            best_distance = np.full(
                (height, width),
                np.inf,
                dtype=np.float32,
            )

            valid = seed_x >= 0

            best_distance[valid] = (xx[valid] - seed_x[valid]) ** 2 + (yy[valid] - seed_y[valid]) ** 2

            # 8-neighbourhood.
            for dy in (-step, 0, step):
                for dx in (-step, 0, step):
                    if dx == 0 and dy == 0:
                        continue

                    source_x = seed_x
                    source_y = seed_y
                    source_owner = owner

                    shifted_x = np.roll(
                        source_x,
                        shift=(dy, dx),
                        axis=(0, 1),
                    )

                    shifted_y = np.roll(
                        source_y,
                        shift=(dy, dx),
                        axis=(0, 1),
                    )

                    shifted_owner = np.roll(
                        source_owner,
                        shift=(dy, dx),
                        axis=(0, 1),
                    )

                    # np.roll wraps around, so invalidate the
                    # wrapped regions.
                    valid_source = shifted_x >= 0

                    if dy > 0:
                        valid_source[:dy, :] = False
                    elif dy < 0:
                        valid_source[dy:, :] = False

                    if dx > 0:
                        valid_source[:, :dx] = False
                    elif dx < 0:
                        valid_source[:, dx:] = False

                    if not np.any(valid_source):
                        continue

                    distance = np.full(
                        (height, width),
                        np.inf,
                        dtype=np.float32,
                    )

                    distance[valid_source] = (xx[valid_source] - shifted_x[valid_source]) ** 2 + (
                        yy[valid_source] - shifted_y[valid_source]
                    ) ** 2

                    replace = valid_source & (distance < best_distance)

                    best_x[replace] = shifted_x[replace]
                    best_y[replace] = shifted_y[replace]
                    best_owner[replace] = shifted_owner[replace]

                    best_distance[replace] = distance[replace]

            seed_x = best_x
            seed_y = best_y
            owner = best_owner

            step //= 2

        return owner

    @classmethod
    def calculate_ownership(
        cls,
        objects: Mapping[str, TileSet],
    ) -> tuple[LabelSet, dict[int, str]]:
        """
        Calculate Voronoi ownership for all objects and all UDIM tiles.

        Parameters
        ----------
        objects:
            Mapping:

                object name -> TileSet / LabelSet

        Returns
        -------
        dict[int, np.ndarray]

            tile number -> ownership labels

            0 = no owner
            >0 = object ID
        """

        seeds, object_ids = cls._build_seed_map(objects)

        ownership = LabelSet()

        for tile_number, seed_map in seeds.items():
            ownership[tile_number] = LabelBuffer.from_nd_array(cls._jump_flood(seed_map))

        return ownership, object_ids
