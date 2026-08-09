from . import (
    executor_internal_bake,
    executor_internal_uv_mask,
    executor_internal_mask,
    executor_internal_pack,
    executor_internal_accumulate,
    executor_external,
)

modules = (
    executor_internal_bake,
    executor_internal_uv_mask,
    executor_internal_mask,
    executor_internal_pack,
    executor_internal_accumulate,
    executor_external,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
