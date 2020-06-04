from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Iterator, Callable, Union, Any

import pjdata.data as d
import pjdata.specialdata as s


class Collection:
    """ Evidently, a iterator cannot be shared between Collection objects!
    """
    isfrozen = False

    def __init__(
            self,
            iterator: Iterator,
            finalizer: Callable[[Any], d.Data],
            finite: bool = True,
            debug_info: Optional[str] = None
    ):
        # TODO: it is possible to restart a collection, but I am not sure it
        #  has any use.
        #  if finite:
        #     iterator = cycle(chain(iterator, (x for x in [End])))
        self.iterator: Iterator = iterator
        self.finalizer: Callable[[Any], d.Data] = finalizer
        self.finite: bool = finite
        self._last_args: tuple = ()
        self._finished: bool = False
        self.debug_info: Optional[str] = debug_info

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.debug_info:
                print()
            self.debug('asks for next data...')
            data = next(self.iterator)

            # TODO: the second part of restarting mode
            # if data is End:
            #     raise StopIteration

            self.debug('...and got', type(data), '\n')
            if isinstance(data, AccResult):
                self.debug('has', type(data.value), 'and', type(data.acc))
                data, *self._last_args = data.both
            return data
        except StopIteration as e:
            if self.debug_info:
                self.debug('...no more data available\n')
            self._finished = True
            raise e from None

    @property  # type: ignore
    @lru_cache()
    def data(self) -> d.Data:
        self.debug('asks for pendurado... Tipo:', str(type(self._last_args)),
                   'Parametros:', self._last_args)
        self._check_consumption()
        result = self.finalizer(*self._last_args)
        self.debug('...got pendurado.')
        return result

    # Onde o data está sendo criado?
    # @property  # type: ignore
    # @lru_cache()
    # def uuid(self) -> str:
    #     return self.data.uuid

    def _check_consumption(self):
        if self.finite and not self._finished:
            try:
                # Check consumed iterators, but not marked as ended.
                print(type(self.iterator), self.iterator)
                next(self.iterator)
                raise Exception('Data object not ready!')
            except StopIteration as e:
                pass

    def debug(
            self,
            *msg: Union[tuple, str]
    ) -> None:
        if self.debug_info:
            print(self.debug_info, '>>>', *msg)


@dataclass(frozen=True)
class AccResult:
    """Accumulator for iterators that send args to finalizer()."""
    value: Optional[Union[d.Data, s.NoData]] = None
    acc: Optional[list] = None

    @property
    def both(self):
        return self.value, self.acc
