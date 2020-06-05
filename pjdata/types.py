from __future__ import annotations

from typing import Union, Tuple, List, Literal, Callable, Type, Dict

from numpy import ndarray  # type: ignore

import pjdata.content.collection as c
import pjdata.content.data as d
import pjdata.content.specialdata as s

Data = Union[Type[s.NoData], d.Data]
DataOrColl = Union[Data, c.Collection]
# HINT: Multi containing a Sink can produce heterogeneous tuples
DataTup = Tuple[Data, ...]
CollTup = Tuple[c.Collection, ...]
DataOrTup = Union[Data, DataTup]
CollOrTup = Union[c.Collection, CollTup]
DataOrCollOrTup = Union[DataOrTup, CollOrTup]

Field = Union[List[str], ndarray]  # For Data fields.
Status = Union[str, bool, Literal["keep"]]  # For frozen and hollow updates.
# Type of function transform(). Can return NoData because of Sink.
Transformation = Callable[[Data], Data]
Acc = Union[List[ndarray], float]
