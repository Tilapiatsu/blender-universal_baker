from __future__ import annotations

import bpy

from ..constant import LOG


class ModifierInjectionService:
    @classmethod
    def inject(cls, source: bpy.types.Object, target: bpy.types.Object) -> None:
        for source_modifier in source.modifiers:
            LOG.debug(f"Copying modifier {source_modifier.name} to {target.name}")
            modifier = target.modifiers.new(
                name=source_modifier.name,
                type=source_modifier.type,
            )

            cls._copy_rna_properties(
                source_modifier,
                modifier,
            )

    @staticmethod
    def _copy_rna_properties(source, destination) -> None:
        is_node = source.type == "NODES"

        for prop in source.bl_rna.properties:
            identifier = prop.identifier

            if identifier in {"rna_type", "name", "type"}:
                continue

            if prop.is_readonly:
                continue

            try:
                setattr(
                    destination,
                    identifier,
                    getattr(
                        source,
                        identifier,
                    ),
                )

            except (AttributeError, TypeError, ValueError):
                # Some RNA properties cannot be copied
                # generically. Ignore them for the MVP.
                continue

            if is_node:
                for prop in dir(source.properties.inputs):
                    if not prop.startswith("Socket"):
                        continue

                    try:
                        value = getattr(source.properties.inputs, prop)

                        if value is None:
                            continue

                        dst = getattr(destination.properties.inputs, prop)

                        if dst is None:
                            continue

                        dst.value = value.value

                    except AttributeError:
                        continue
