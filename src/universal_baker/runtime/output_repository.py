from __future__ import annotations

from collections import defaultdict
from typing import Iterable

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
        # (target_name, baker_id)
        #
        self._target_baker_index = defaultdict(list)

        #
        # (target_name, baker_id, object_name)
        #
        self._object_index = {}

    def add(self, output: BakeOutput):
        self._outputs[output.id] = output

        target_key = (output.bake_group_name, output.baker_id)

        self._target_baker_index[target_key].append(output)

        object_key = (output.bake_group_name, output.baker_id, output.target_object_name)

        self._object_index[object_key] = output

    def remove(self, output: BakeOutput):
        self._outputs.pop(output.id, None)

        target_key = (
            output.bake_group_name,
            output.baker_id,
        )

        outputs = self._target_baker_index.get(target_key)

        if outputs:
            outputs.remove(output)

            if not outputs:
                del self._target_baker_index[target_key]

        self._object_index.pop(
            (output.bake_group_name, output.baker_id, output.target_object_name),
            None,
        )

    def get_outputs(self, target, baker) -> list[BakeOutput]:
        """
        Returns every output belonging to a bake target
        for one baker.
        """
        return list(
            self._target_baker_index.get(
                (target.name, baker.id),
                [],
            )
        )

    def get_output(self, target, baker, object) -> BakeOutput | None:
        return self._object_index.get((target.name, baker.id, object.name))

    def has_output(self, target, baker, object) -> bool:
        return self.get_output(target, baker, object) is not None

    def iter_outputs(self) -> Iterable[BakeOutput]:
        return self._outputs.values()

    def count(self) -> int:
        return len(self._outputs)

    def clear_target(self, target):
        ids = [output.id for output in self.iter_outputs() if output.bake_group == target]

        for output_id in ids:
            self.remove(self._outputs[output_id])
