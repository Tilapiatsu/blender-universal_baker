from __future__ import annotations

from .. import Logger
from ..sinks.console import ConsoleSink
from ..sinks.ui.sink import UISink
from .operators import register_sink, unregister_sink
from .redraw import BlenderRedrawAdapter


class BlenderLoggerRuntime:
    """
    Owns the Blender-facing logger instance and its UI integration.

    Call logger.blender.register() before constructing this runtime so the
    filter PropertyGroup and toggle operator are registered.
    """

    def __init__(
        self,
        addon_name: str,
        *,
        filter_property_name: str = "logger_filter",
        space_types: set[str] | None = None,
        console_level=None,
    ):
        self.filter_property_name = filter_property_name

        self.logger = Logger(addon=addon_name)

        self.console_sink = ConsoleSink(level=console_level) if console_level is not None else ConsoleSink()
        self.ui_sink = UISink()

        self.logger.dispatcher.add_sink("console", self.console_sink)
        self.logger.dispatcher.add_sink("ui", self.ui_sink)

        self.ui_sink_key = register_sink(self.ui_sink)
        self.redraw_adapter = BlenderRedrawAdapter(
            sink=self.ui_sink,
            space_types=space_types,
        )

        self._closed = False

    def close(self):
        if self._closed:
            return

        self._closed = True

        self.redraw_adapter.close()
        unregister_sink(self.ui_sink_key)
        self.logger.close()
