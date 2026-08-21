from . import (
    diffuse,
    ao,
    custom,
)

modules = (
    diffuse,
    ao,
    custom,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
