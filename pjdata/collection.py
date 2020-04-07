from functools import lru_cache
from typing import Iterator

from pjdata.abc.abstractdata import AbstractData
from pjdata.history import History


class Collection(AbstractData):
    """An optimized list of Data objects (TODO: optimize).

    To be used through concurrent transformers:
        Expand, Map, Reduce


    Attributes
    ----------

    Parameters
    ----------
    datas
        Usually, a list of Data objects.
        When 'datas' is a single Data object, this collection will replicate it
        infinitelly.
    history
        History object of transformations.
    failure
        The cause, when the provided history leads to a failure.
    dataset
        The user can set a dataset if convenient.
    """

    def __init__(self, history, failure, dataset, original_data):
        # TODO: is collection printable?
        if history is None:
            history = History([])
        self.history = history
        self.failure = failure
        from pjdata.dataset import NoDataset
        self.dataset = NoDataset if dataset is None else dataset
        self.next_index = 0
        self.original_data = original_data
        self._all_nones = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_index == self.size:
            self.next_index = 0
            raise StopIteration('No more Data objects left. Restarted!')
        nex = next(self._datas) if isinstance(self._datas, Iterator) else \
            self._datas[self.next_index]
        self.next_index += 1
        return nex

    def _uuid_impl(self):
        if self.history.last is None:
            return 'c', self.dataset.uuid + self.history.uuid + self._uuids
        else:
            return self.history.last.step.upper(), \
                   self.dataset.uuid + self.history.uuid + self._uuids

    @property
    def all_nones(self):
        if self._all_nones is None:
            self._all_nones = not any(self._datas)
        return self._all_nones
