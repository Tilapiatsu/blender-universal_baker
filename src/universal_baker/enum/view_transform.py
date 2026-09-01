from __future__ import annotations

from enum import StrEnum

import bpy


def get_available_view_transforms() -> dict:
    view_settings = bpy.context.scene.view_settings
    try:
        # Intentionally trigger an error with an invalid identifier
        view_settings.view_transform = "__INVALID__"
    except TypeError as e:
        # Extract available enum options from the error string
        err_msg = str(e)
        if "(" in err_msg and ")" in err_msg:
            # Parse options out of the error message tuple
            raw_options = err_msg.split("(")[1].split(")")[0]
            options = [opt.strip(" '\"") for opt in raw_options.split(",")]
            view_transforms = {o.upper().replace(" ", "_"): o for o in options}
            return view_transforms
    return {}


# ViewTransform = Enum("ViewTransform", get_available_view_transforms())


class ViewTransform(StrEnum):
    STANDARD = "Standard"
    ACES_1_3 = "ACES 1.3"
    ACES_2_0 = "ACES 2.0"
    KHRONOS = "Khronos PBR Neutral"
    AGX = "AgX"
    FILMIC = "Filmic"
    FILMIC_LOG = "Filmic Log"
    FALSE_COLOR = "False Color"
    RAW = "Raw"


class DisplayDevice(StrEnum):
    SRGB = "sRGB"
    DISPLAY_P3 = "Display P3"
    REC_1886 = "Rec.1886"
    REC_2020 = "Rec.2020"
    REC_2100_PQ = "Rec.2100-PQ"
    REC_2100_HLG = "Rec.2100-HLG"
