from __future__ import annotations

from universal_baker.constant import LOG

from ..parameter.baker_custom.definition import CustomBakerDefinition
from ..parameter.baker_local.definition import LocalDefinition
from ..parameter.parameter import Parameter
from ..parameters_definition.baker_settings import UBK_BakerSettings


class BakerSettingsUI:
    @classmethod
    def draw(
        cls,
        layout,
        definition: CustomBakerDefinition | LocalDefinition,
        settings: UBK_BakerSettings,
    ):
        item = getattr(settings, definition.settings_name, None)

        if item is None:
            return

        for parameter in definition.parameters:
            if not parameter.visible:
                continue

            cls._draw_parameter(layout, parameter, item, definition)

    @classmethod
    def _draw_parameter(
        cls,
        layout,
        parameter: Parameter,
        item,
        definition: CustomBakerDefinition | LocalDefinition,
    ):
        layout.prop(item, parameter.identifier, text=parameter.name)
