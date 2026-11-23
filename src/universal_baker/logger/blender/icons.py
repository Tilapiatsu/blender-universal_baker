from __future__ import annotations

from ..scopes.task_status import TaskStatus
from ..severity import Severity


STATUS_ICONS = {
    TaskStatus.PENDING: "DOT",
    TaskStatus.RUNNING: "TIME",
    TaskStatus.SUCCESS: "CHECKMARK",
    TaskStatus.WARNING: "ERROR",
    TaskStatus.ERROR: "CANCEL",
    TaskStatus.CANCELLED: "CANCEL",
}

SEVERITY_ICONS = {
    Severity.DEBUG: "INFO",
    Severity.INFO: "INFO",
    Severity.WARNING: "ERROR",
    Severity.ERROR: "CANCEL",
    Severity.CRITICAL: "CANCEL",
}
