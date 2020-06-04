from typing import Union, Tuple

import pjdata.collection as c
import pjdata.data as d
import pjdata.specialdata as s

DataT = Union[s.NoData, d.Data]
DataCollTupleT = Union[
    Tuple[s.NoData, ...], Tuple[DataT, ...], Tuple[c.Collection, ...],
    DataT, c.Collection
]
DataCollT = Union[DataT, c.Collection]
DataNoDataT = Union[s.NoData, d.Data]


#  UUIDData

def flatten(lst):
    return [item for sublist in lst for item in sublist]


class Property(object):
    """Substitute for the @property decorator due mypy conflicts"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
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
