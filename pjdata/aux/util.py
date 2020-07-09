from __future__ import annotations

from compose import compose


class _meta(type):
    def __getattr__(self, item):
        return lambda x: x.__getattribute__(item)


class _(metaclass=_meta):
    """Shortcut for functional handling of iterables.
 
    _.m = apply map and convert to list (useful for easy printing while debugging)
    _ = item inside iterable (to provide as a function to map)

    Example:
        map(_[4], tuples)
        map(_('My class name applied for all new instances'), classes)
        _.m(_.id, users)

    ps. Mostly for development.
    """

    def __new__(cls, *args, **kwargs):
        return lambda x: x(*args, **kwargs)

    def __class_getitem__(cls, item):
        return lambda x: x[item]

    m = compose(list, map)


def flatten(lst):
    return [item for sublist in lst for item in sublist]


class Property(object):
    """Substitute for the @property decorator due mypy conflicts.

    More information can be found on mypy's
    Github, issue #1362
    """

    def __init__(self, fget=None, doc=None):
        self.fget = fget
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)


class Classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
