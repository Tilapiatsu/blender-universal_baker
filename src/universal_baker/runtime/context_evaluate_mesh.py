from __future__ import annotations

from dataclasses import dataclass

from .context import ExecutionContext
from .task_evaluate_mesh import EvaluateMeshesTask


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
