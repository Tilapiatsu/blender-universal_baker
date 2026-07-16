from . import (
    object_add,
    object_remove,
    map_add,
    map_remove,
    bake_all,
    bake_object,
    bake_map,
    pack_add,
    pack_remove,
    pack_all,
    pack_selected,
    pack_mapping_fix,
)

modules = (
    object_add,
    object_remove,
    map_add,
    map_remove,
    bake_all,
    bake_object,
    bake_map,
    pack_add,
    pack_remove,
    pack_all,
    pack_selected,
    pack_mapping_fix,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
