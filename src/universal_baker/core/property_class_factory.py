### from https://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class
class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype


def ClassFactory(name, argnames, BaseClass=BaseClass):
    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)

    newclass = type(name, (BaseClass,), {"__init__": __init__})
    return newclass
