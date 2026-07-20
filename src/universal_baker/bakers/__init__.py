from . import (
    diffuse,
    ao,
)

modules = (
    diffuse,
    ao,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
