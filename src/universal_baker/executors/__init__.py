from . import (
    execution_target_internal,
    executor_accumulate,
    executor_bake,
    executor_evaluate_meshes,
    executor_mask,
    executor_ownership,
    executor_pack,
)

modules = (
    execution_target_internal,
    executor_accumulate,
    executor_bake,
    executor_evaluate_meshes,
    executor_mask,
    executor_ownership,
    executor_pack,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
