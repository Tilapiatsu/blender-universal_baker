from . import (
    alpha_over,
)

modules = (alpha_over,)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
