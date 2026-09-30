from . import (
    bake_all,
    bake_and_pack_all,
    bake_group,
    bake_map,
    baker_add,
    baker_library_add,
    baker_library_refresh,
    baker_library_remove,
    baker_remove,
    custom_baker_refresh,
    group_add,
    group_remove,
    pack_all,
    pack_mapping_fix,
    pack_selected,
    packer_add,
    packer_remove,
    skew_correction_remove,
    source_object_add,
    source_object_remove,
    target_object_add,
    target_object_remove,
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
    skew_correction_remove,
    custom_baker_refresh,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
