from functools import lru_cache
from typing import Iterator

from pjdata.aux.identifyable import Identifyable
from pjdata.dataset import NoDataset
from pjdata.history import History


class Collection(Identifyable):
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
        if history is None:
            history = History([])
        self.history = history
        self.failure = failure
        self.dataset = NoDataset if dataset is None else dataset
        self.next_index = 0
        self.original_data = original_data

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
    @lru_cache
    def all_nones(self):
        return not any(self._datas)
