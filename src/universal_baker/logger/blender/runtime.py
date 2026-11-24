from __future__ import annotations

from ..logger import Logger
from .operators import register_sink, unregister_sink
from .redraw import BlenderRedrawAdapter


class BlenderLoggerRuntime:
    """
    Owns only the Blender-specific integration for an already configured Logger.

    Configure the Logger before passing it here: register middleware and sinks
    on the Logger itself, then pass the UISink separately when Blender UI
    integration is required.

    This class deliberately does NOT:
      - create a Logger;
      - register middleware;
      - create or register sinks with the Logger;
      - close the Logger or its sinks.

    The addon remains responsible for the Logger's configuration and lifetime.
    The runtime only manages the Blender operator's UISink registry entry and
    the redraw adapter.
    """

    def __init__(
        self,
        logger: Logger,
        *,
        ui_sink=None,
        filter_property_name: str = "logger_filter",
        space_types: set[str] | None = None,
    ):
        if logger is None:
            raise TypeError("BlenderLoggerRuntime requires a configured Logger")

        self.logger = logger
        self.ui_sink = ui_sink
        self.filter_property_name = filter_property_name

        self.ui_sink_key = None
        self.redraw_adapter = None
        self._closed = False

        if ui_sink is not None:
            # The exact same UISink instance must already be registered on
            # logger.dispatcher. This runtime does not register it a second time.
            self.ui_sink_key = register_sink(ui_sink)

            try:
                self.redraw_adapter = BlenderRedrawAdapter(
                    sink=ui_sink,
                    space_types=space_types,
                )
            except Exception:
                unregister_sink(self.ui_sink_key)
                self.ui_sink_key = None
                raise

    def close(self):
        """
        Release Blender-specific resources.

        This does not close the Logger or its sinks. The addon owns those and
        should call logger.close() separately when it is finished with them.
        """
        if self._closed:
            return

        self._closed = True

        if self.redraw_adapter is not None:
            self.redraw_adapter.close()
            self.redraw_adapter = None

        if self.ui_sink_key is not None:
            unregister_sink(self.ui_sink_key)
            self.ui_sink_key = None
