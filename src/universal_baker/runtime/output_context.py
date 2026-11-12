from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .settings_output import OutputSettings


@dataclass()
class OutputContext:
    """Stores all informations to write a file to disk and properly name it"""

    directory_template: str
    filename_template: str
    extension: str
    variables: dict[str, Any]
    output_settings: OutputSettings
