from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from .settings_output import OutputSettings


@dataclass(slots=True)
class OutputFile:
    directory: Path
    filename: str
    extension: str
    absolute_path: Path
    settings: OutputSettings
