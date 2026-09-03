from . import (
    source_object_add,
    source_object_remove,
    target_object_add,
    target_object_remove,
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
    baker_library_add,
    baker_library_remove,
    baker_library_refresh,
    custom_baker_refresh,
)

modules = (
    source_object_add,
    source_object_remove,
    target_object_add,
    target_object_remove,
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
