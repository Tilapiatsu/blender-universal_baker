from . import (
    execution_target_internal,
    executor_bake,
    executor_ownership,
    executor_mask,
    executor_pack,
    executor_accumulate,
)

modules = (
    execution_target_internal,
    executor_bake,
    executor_ownership,
    executor_mask,
    executor_pack,
    executor_accumulate,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
