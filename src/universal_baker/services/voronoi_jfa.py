from __future__ import annotations

from collections.abc import Mapping

import numpy as np

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
        Build the initial JFA seed maps.

        Parameters
        ----------
        objects:
            Mapping of object UUID -> UV coverage TileSet.

        Returns
        -------
        seeds:
            tile number -> integer seed labels.

        label_to_uuid:
            internal JFA label -> object UUID.

        Notes
        -----
        Integer labels are internal to the JFA implementation.
        UUIDs remain the authoritative object identity.
        """

        # Sort UUIDs so label assignment is deterministic.
        uuids = sorted(objects.keys())

        uuid_to_label = {uuid: label for label, uuid in enumerate(uuids, start=1)}

        label_to_uuid = {label: uuid for uuid, label in uuid_to_label.items()}

        tile_numbers = set()

        for tileset in objects.values():
            tile_numbers.update(tileset.keys())

        result = {}

        for tile_number in sorted(tile_numbers):
            tile_arrays = []

            for object_uuid in uuids:
                tileset = objects[object_uuid]

                if tile_number not in tileset:
                    continue

                tile = tileset[tile_number]

                if tile is None:
                    continue

                tile_arrays.append(
                    (
                        uuid_to_label[object_uuid],
                        tile.pixels,
                    )
                )

            if not tile_arrays:
                continue

            shape = tile_arrays[0][1].shape

            seeds = np.zeros(
                shape,
                dtype=np.int32,
            )

            for label, mask in tile_arrays:
                if mask.shape != shape:
                    raise ValueError(f"Tile {tile_number} has inconsistent resolution.")

                occupied = mask != 0

                # First object wins if UVs overlap.
                seeds[occupied & (seeds == 0)] = label

            result[tile_number] = seeds

        return result, label_to_uuid

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
        tuple[LabelSet, dict[int, str]]

            Ownership Label -> ownership labels

            0 = no owner
            >0 = object ID
        """

        seeds, label_to_uuid = cls._build_seed_map(objects)

        ownership = LabelSet()

        for tile_number, seed_map in seeds.items():
            ownership[tile_number] = LabelBuffer.from_nd_array(cls._jump_flood(seed_map))

        return ownership, label_to_uuid
