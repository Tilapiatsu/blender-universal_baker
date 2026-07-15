from __future__ import annotations

from typing import Optional

import bpy

from ..executors.executor_internal import BakeExecutorInternal
from ..runtime.job import Job
from ..runtime.session import ExecutionSession


class BakeManager:
    """
    Central manager responsible for executing bake jobs.

    Only one ExecutionSession may run at a time.
    """

    _instance: Optional["BakeManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()

        return cls._instance

    def _initialize(self):
        self._executor = BakeExecutorInternal()
        self._active_session: ExecutionSession | None = None
        self._is_running = False

    def start(self, context: bpy.types.Context, job: Job) -> ExecutionSession:
        """
        Execute a Job.
        """
        if self._is_running:
            raise RuntimeError("A bake session is already running.")

        self._is_running = True

        try:
            session = self._executor.execute(context, job)

            self._active_session = session
            return session

        finally:
            self._is_running = False

    def cancel(self):
        if not self._is_running:
            return

        self._executor.cancel()

    @property
    def active_session(self) -> ExecutionSession | None:
        return self._active_session

    @property
    def is_running(self) -> bool:
        return self._is_running


_MANAGER = BakeManager()


def get_bake_manager():
    return _MANAGER
