from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AccumulateSettings:
    baker_uuid: str
