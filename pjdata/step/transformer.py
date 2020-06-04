from __future__ import annotations

from typing import Union, Callable, Optional

import pjdata.aux.util as u


class Transformer:
    def __init__(
            self,
            func: Optional[Callable[[u.DataT], u.DataT]],  # problema
            info: Optional[
                Union[dict,
                      Callable[[], dict],
                      Callable[[u.DataT], dict]]]
    ):
        self.func = func if func else lambda data: data

        # Note:
        # Callable returns True, if the object appears to be callable
        # Yes, that appears!
        if callable(info):
            self.info = info
        elif isinstance(info, dict):
            self.info = lambda: info
        elif info is None:
            self.info = lambda: {}
        else:
            raise TypeError('Unexpected info type. You should use, callable, '
                            'dict or None.')

    def transform(self, data: u.DataCollTupleT) -> u.DataCollTupleT:
        if isinstance(data, tuple):
            return tuple((dt.transformedby(self.func) for dt in data))
        # Todo: We should add exception handling here because self.func can
        #  raise an error
        return data.transformedby(self.func)
