from . import map, packing, object, output, project

modules = (map, packing, object, output, project)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
