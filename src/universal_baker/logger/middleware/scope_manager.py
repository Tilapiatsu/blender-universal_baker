from contextlib import contextmanager

from .task_scope import TaskScope


class ScopeManager:
    def __init__(self):
        self._stack: list[TaskScope] = []
        self._roots: list[TaskScope] = []

    @property
    def current(self) -> TaskScope | None:
        if not self._stack:
            return None

        return self._stack[-1]

    @property
    def current_path(self) -> tuple[str, ...]:
        return tuple(scope.name for scope in self._stack)

    @property
    def roots(self) -> list[TaskScope]:
        return self._roots

    @contextmanager
    def scope(self, name, **metadata):
        scope = TaskScope(name=name, metadata=metadata)

        if self._stack:
            self._stack[-1].add_child(scope)

        else:
            self._roots.append(scope)

        self._stack.append(scope)

        try:
            yield scope

        finally:
            scope.finish()
            self._stack.pop()
