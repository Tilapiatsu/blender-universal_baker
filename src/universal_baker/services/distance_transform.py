from __future__ import annotations

import numpy as np

from ..runtime.label_set import LabelSet

INF = np.float32(1e20)


class DistanceTransform:
    @staticmethod
    def distance_transform_1d(values: np.ndarray) -> np.ndarray:
        """
        Exact squared Euclidean distance transform of a 1D array.

        `values` should contain:
            0      for feature pixels
            INF    for non-feature pixels
        """

        n = len(values)

        distance = np.empty(n, dtype=np.float32)

        v = np.empty(n, dtype=np.int32)

        z = np.empty(n + 1, dtype=np.float32)

        k = 0
        v[0] = 0
        z[0] = -INF
        z[1] = INF

        for q in range(1, n):
            while True:
                p = v[k]

                s = ((values[q] + q * q) - (values[p] + p * p)) / (2 * q - 2 * p)

                if s > z[k]:
                    break

                k -= 1

            k += 1

            v[k] = q
            z[k] = s
            z[k + 1] = INF

        k = 0

        for q in range(n):
            while z[k + 1] < q:
                k += 1

            p = v[k]

            distance[q] = (q - p) * (q - p) + values[p]

        return distance

    @classmethod
    def euclidean_distance_transform(cls, mask: np.ndarray) -> np.ndarray:
        """
        Compute squared Euclidean distance to the nearest
        non-zero pixel.

        Returns a float32 array.
        """

        height, width = mask.shape

        source = np.where(mask, 0.0, INF).astype(np.float32)

        horizontal = np.empty_like(source)

        for y in range(height):
            horizontal[y] = cls.distance_transform_1d(source[y])

        result = np.empty_like(source)

        for x in range(width):
            result[:, x] = cls.distance_transform_1d(horizontal[:, x])

        return result

    @classmethod
    def calculate_ownership(cls, masks: LabelSet) -> np.ndarray:
        """
        Calculate the nearest-object ownership map.

        masks:
            object_uuid -> binary UV coverage
        """

        object_ids = masks.buffers

        if not object_ids:
            raise ValueError("No objects supplied.")

        distances = []

        for object_id in object_ids:
            distance = cls.euclidean_distance_transform(object_id.pixels)

            distances.append(distance)

        stacked = np.stack(distances, axis=0)

        owners = np.argmin(stacked, axis=0)

        return owners
