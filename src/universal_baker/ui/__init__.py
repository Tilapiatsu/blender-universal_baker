from . import map_list, object_list, panel

modules = (map_list, object_list, panel)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
