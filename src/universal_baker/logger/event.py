from dataclasses import dataclass, field
from typing import Any
import time

from .severity import Severity


@dataclass(slots=True, frozen=True)
class LogEvent:
    severity: Severity
    message: str
    timestamp: float = field(default_factory=time.time)
    addon: str | None = None
    category: str | None = None
    exception: Exception | None = None
    data: dict[str, Any] = field(default_factory=dict)
