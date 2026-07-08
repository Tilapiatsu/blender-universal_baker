from . import object_add, object_remove, map_add, map_remove

modules = (object_add, object_remove, map_add, map_remove)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
