from . import output, map, packing, object, project

modules = (output, map, packing, object, project)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
