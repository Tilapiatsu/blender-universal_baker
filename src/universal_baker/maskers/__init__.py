from . import (
    uv_boundry,
)

modules = (uv_boundry,)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
