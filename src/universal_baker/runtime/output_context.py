from __future__ import annotations

from dataclasses import dataclass

from .settings_output import OutputSettings

from typing import Any


@dataclass(slots=True)
class OutputContext:
    """Stores all informations to write a file to disk and properly name it"""

    directory_template: str
    filename_template: str
    extension: str
    variables: dict[str, Any]
    output_settings: OutputSettings
