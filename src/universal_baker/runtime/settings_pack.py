from __future__ import annotations
from dataclasses import dataclass

from .settings_output import OutputSettings


@dataclass(slots=True)
class PackSettings(OutputSettings):
    """Settings for packing Images"""
