from . import (
    output_tokens,
    output_transforms,
)

modules = (
    output_tokens,
    output_transforms,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
