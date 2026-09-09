from __future__ import annotations

from dataclasses import dataclass

import bpy

from .context import ExecutionContext
from .task_evaluate_mesh import EvaluateMeshesTask


# TODO: Need to properly write the contex to inherit from Context Class
@dataclass(slots=True)
class EvaluateMeshesContext(ExecutionContext):
    task: EvaluateMeshesTask

    finished: bool = False
    success: bool = False
    message: str = ""

    def succeed(self, message: str = "") -> None:
        self.finished = True
        self.success = True
        self.message = message

    def fail(self, message: str) -> None:
        self.finished = True
        self.success = False
        self.message = message
