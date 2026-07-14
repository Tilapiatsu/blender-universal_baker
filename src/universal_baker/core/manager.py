from __future__ import annotations

from typing import Optional

import bpy

from ..runtime.executor_internal import BakeExecutorInternal
from ..runtime.job import BakeJob
from ..runtime.session import BakeSession


class BakeManager:
    """
    Central manager responsible for executing bake jobs.

    Only one BakeSession may run at a time.
    """

    _instance: Optional["BakeManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()

        return cls._instance

    def _initialize(self):
        self._executor = BakeExecutorInternal()
        self._active_session: BakeSession | None = None
        self._is_running = False

    def start(self, context: bpy.types.Context, job: BakeJob) -> BakeSession:
        """
        Execute a BakeJob.
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
    def active_session(self) -> BakeSession | None:
        return self._active_session

    @property
    def is_running(self) -> bool:
        return self._is_running


_MANAGER = BakeManager()


def get_bake_manager():
    return _MANAGER
