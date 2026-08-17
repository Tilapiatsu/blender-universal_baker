from . import (
    execution_target_internal,
    executor_bake,
    executor_ownership,
    executor_mask,
    executor_pack,
    executor_accumulate,
    executor_external,
)

modules = (
    execution_target_internal,
    executor_bake,
    executor_ownership,
    executor_mask,
    executor_pack,
    executor_accumulate,
    executor_external,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
