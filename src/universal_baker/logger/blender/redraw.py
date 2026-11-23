from __future__ import annotations

import bpy


class BlenderRedrawAdapter:
    """
    Connects a UISink to Blender's area redraw system.

    The adapter must be notified from Blender's main thread.
    """

    def __init__(
        self,
        sink,
        space_types: set[str] | None = None,
    ):
        self.sink = sink

        # None means redraw all available editor areas.
        self.space_types = set(space_types) if space_types is not None else None

        self._closed = False
        self._timer_pending = False

        self.sink.add_listener(self.request_redraw)

    # ---------------------------------------------------------
    # Redraw requests
    # ---------------------------------------------------------

    def request_redraw(self):
        if self._closed or self._timer_pending:
            return

        self._timer_pending = True

        try:
            bpy.app.timers.register(
                self._redraw,
                first_interval=0.0,
            )
        except (RuntimeError, ValueError):
            self._timer_pending = False
            raise

    def _redraw(self):
        self._timer_pending = False

        if self._closed:
            return None

        window_manager = bpy.context.window_manager

        if window_manager is None:
            return None

        for window in window_manager.windows:
            screen = window.screen

            if screen is None:
                continue

            for area in screen.areas:
                if self.space_types is not None and area.type not in self.space_types:
                    continue

                area.tag_redraw()

        return None

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def close(self):
        if self._closed:
            return

        self._closed = True

        self.sink.remove_listener(self.request_redraw)

        if bpy.app.timers.is_registered(self._redraw):
            bpy.app.timers.unregister(self._redraw)

        self._timer_pending = False
