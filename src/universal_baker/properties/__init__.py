from . import settings_bake, settings_cage, settings_pack, map, packer, object, project

modules = (settings_bake, settings_cage, settings_pack, map, packer, object, project)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
