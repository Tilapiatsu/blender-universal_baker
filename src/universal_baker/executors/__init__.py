from . import executor_internal, executor_external

modules = (executor_internal, executor_external)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
