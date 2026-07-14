from . import bake_settings, cage_settings, map, packing, object, project

modules = (bake_settings, cage_settings, map, packing, object, project)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
