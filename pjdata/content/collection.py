from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Iterator, Callable, Union, Any, Tuple

import pjdata.content.data as d
import pjdata.types as t
from pjdata.aux.util import Property
import pjdata.content.content as c


class Collection(c.Content):
    """ Evidently, a iterator cannot be shared between Collection objects!
    """

    def __init__(self,
                 iterator: Iterator,
                 finalizer: Callable[[Any], d.Data],
                 finite: bool = True,
                 failure: Optional[str] = None,
                 frozen: bool = False,
                 hollow: bool = False,
                 debug_info: Optional[str] = None):
        self._jsonable = {'some info to print about colls': None}  # <-- TODO

        # TODO: it is possible to restart a collection, but I am not sure it has any use. Code for that:
        #  if finite:
        #     iterator = cycle(chain(iterator, (x for x in [End])))
        self.iterator: Iterator = iterator
        self.finalizer: Callable[[Any], d.Data] = finalizer
        self.finite: bool = finite
        self._last_args: tuple = ()
        self._finished: bool = False
        self._failure = failure
        self._frozen = frozen
        self._hollow = hollow
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

    def _check_consumption(self) -> None:
        if self.finite and not self._finished:
            try:
                # Check consumed iterators, but not marked as ended.
                print(type(self.iterator), self.iterator)
                next(self.iterator)
                raise Exception('Data object not ready!')
            except StopIteration as e:
                pass

    def debug(self, *msg: Union[tuple, str]) -> None:
        if self.debug_info:
            print(self.debug_info, '>>>', *msg)

    @Property
    def isfrozen(self):
        # TODO: what happens when a frozen Data reach a Streamer? Would it be fooled by outdated fields?
        return self._frozen

    @Property
    def ishollow(self):
        return self._hollow

    def _uuid_impl(self):
        return self.data.uuid


@dataclass(frozen=True)
class AccResult:
    """Accumulator for iterators that send args to finalizer()."""
    value: Optional[t.Data] = None
    acc: Optional[t.Acc] = None

    @Property
    def both(self) -> Tuple[Optional[t.Data], Optional[t.Acc]]:
        return self.value, self.acc
