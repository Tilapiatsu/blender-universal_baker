from . import object_add, object_remove, map_add, map_remove, bake_all, bake_object, bake_map

modules = (object_add, object_remove, map_add, map_remove, bake_all, bake_object, bake_map)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
