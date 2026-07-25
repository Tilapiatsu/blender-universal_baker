from __future__ import annotations

import bpy
from collections import defaultdict
from typing import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime.bake_group import BakeGroup
    from .bake_output import BakeOutput


class OutputRepository:
    """
    Runtime repository storing every BakeOutput produced
    during the execution of a BakeSession.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        self._outputs: dict[str, BakeOutput] = {}

        #
        # (bake_group_uuid, baker_uuid)
        #
        self._target_baker_index = defaultdict(list)

        #
        # (bake_group_uuid, baker_uuid, object_name)
        #
        self._object_index = {}

    def add(self, output: BakeOutput):
        self._outputs[output.uuid] = output

        target_key = (output.bake_group.uuid, output.uuid)

        self._target_baker_index[target_key].append(output)

        object_key = (output.bake_group.uuid, output.uuid, output.target_object_name)

        self._object_index[object_key] = output

    def remove(self, output: BakeOutput):
        self._outputs.pop(output.uuid, None)

        target_key = (
            output.bake_group_name,
            output.uuid,
        )

        outputs = self._target_baker_index.get(target_key)

        if outputs:
            outputs.remove(output)

            if not outputs:
                del self._target_baker_index[target_key]

        self._object_index.pop(
            (output.bake_group_name, output.uuid, output.target_object_name),
            None,
        )

    def get_outputs(self, bake_group_uuid: str, baker_uuid: str) -> list[BakeOutput]:
        """
        Returns every output belonging to a bake target
        for one baker.
        """
        return list(
            self._target_baker_index.get(
                (bake_group_uuid, baker_uuid),
                [],
            )
        )

    def get_output(self, bake_group: BakeGroup, baker_uuid: str, object: bpy.types.Object) -> BakeOutput | None:
        return self._object_index.get((bake_group.uuid, baker_uuid, object.name))

    def has_output(self, bake_group: BakeGroup, baker_uuid: str, object: bpy.types.Object) -> bool:
        return self.get_output(bake_group, baker_uuid, object) is not None

    def iter_outputs(self) -> Iterable[BakeOutput]:
        return self._outputs.values()

    @property
    def count(self) -> int:
        return len(self._outputs)

    def clear_target(self, bake_group: BakeGroup):
        ids = [output.uuid for output in self.iter_outputs() if output.bake_group == bake_group]

        for output_id in ids:
            self.remove(self._outputs[output_id])

    def iter_target_outputs(self, bake_group: BakeGroup):
        for output in self.iter_outputs():
            if output.bake_group == bake_group:
                yield output

    def _max_chr(self) -> dict[str, int]:
        max_chr = {"target_name": 0, "bake_id": 0, "uuid": 0}
        for id, output in self._outputs.items():
            max_chr["target_name"] = max(len(output.target_object_name), max_chr["target_name"])
            max_chr["baker_id"] = max(len(output.baker.id), max_chr["bake_id"])
            max_chr["uuid"] = max(len(id), max_chr["uuid"])

        return max_chr

    def __repr__(self) -> str:
        result = f"Repository contains {self.count} output(s)\n"
        for id, output in self._outputs.items():
            result += f"{output.target_object_name:20} | {output.baker.id:20} | {id}\n"

        return result
