from __future__ import annotations

from ..constant import ICON_BAKE, ICON_SOURCE_OBJECT, ICON_TARGET_OBJECT


def draw_target_objects(layout, bake_group, prop_name: str, indent: int):
    for target in bake_group.target_objects:
        row = layout.row()
        draw_indent(target, row, prop_name, indent, len(bake_group.source_objects))

        row.prop(target, "enabled", text="")
        row = row.row(align=True)
        row.enabled = target.enabled
        row.label(text=target.object.name, icon=ICON_TARGET_OBJECT)
        row = row.row(align=True)
        row.alignment = "RIGHT"
        row.operator("ubk.bake_target", text="", icon=ICON_BAKE)

        if not getattr(target, prop_name):
            continue

        draw_source_objects(layout, target, indent + 1)


def draw_source_objects(layout, target_object, indent: int):
    for source in target_object.source_objects:
        row = layout.row()
        draw_indent(source, row, "expanded", indent, 0, draw_indent=False)

        row.prop(source, "enabled", text="")
        row = row.row(align=True)
        row.enabled = source.enabled
        row.label(text=source.object.name, icon=ICON_SOURCE_OBJECT)


def draw_indent(item, layout, prop_name: str, indent: int, sub_item_count: int, draw_indent: bool = True):
    for _ in range(indent):
        layout.label(text="", icon="BLANK1")

    if sub_item_count > 0:
        if draw_indent:
            icon_type = "TRIA_DOWN" if getattr(item, prop_name) else "TRIA_RIGHT"
            layout.prop(
                item,
                prop_name,
                text="",
                icon=icon_type,
                emboss=False,
            )
        else:
            layout.label(text="", icon="BLANK1")
    else:
        layout.label(text="", icon="BLANK1")

    indent += 1
