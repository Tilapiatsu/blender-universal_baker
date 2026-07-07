from .task import BakeTask
from dataclasses import dataclass


@dataclass(slots=True)
class BakeJob:
    tasks: list[BakeTask]
    total_tasks: int = 0
    current_task: int = 0
    cancelled: bool = False
