from . import (
    object_add,
    object_remove,
    group_add,
    group_remove,
    baker_add,
    baker_remove,
    bake_all,
    bake_and_pack_all,
    bake_group,
    bake_map,
    packer_add,
    packer_remove,
    pack_all,
    pack_selected,
    pack_mapping_fix,
    visualization,
    baker_library_add,
    baker_library_remove,
    baker_library_refresh,
    custom_baker_refresh,
)

modules = (
    object_add,
    object_remove,
    group_add,
    group_remove,
    baker_add,
    baker_remove,
    bake_all,
    bake_and_pack_all,
    bake_group,
    bake_map,
    packer_add,
    packer_remove,
    pack_all,
    pack_selected,
    pack_mapping_fix,
    visualization,
    baker_library_add,
    baker_library_remove,
    baker_library_refresh,
    custom_baker_refresh,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
