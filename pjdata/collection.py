from dataclasses import dataclass
from functools import lru_cache
from typing import Iterator

from pjdata.abc.abstractdata import AbstractData


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

    def __init__(self, history, failure, original_data, uuid, fields=None):
        if uuid is None:
            raise Exception('Collection child classes should be instantiated'
                            ' by experts only!')
        # TODO: is collection Printable?
        self.history = history
        self.failure = failure
        self.next_index = 0
        self.original_data = original_data
        self._allfrozen = None
        self._uuid = uuid
        self.fields = {} if fields is None else fields

    def updated(self, transformations, datas=None, failure='keep', fields=None):
        """Recreate Collection object with updated history, failure and datas.

        Parameters
        ----------
        transformations
            List of Transformation objects.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        datas
            New list of Data object.

        Returns
        -------
        New Collection object (it may keep some references for performance).
        """
        if failure == 'keep':
            failure = self.failure

        if not datas:
            if not self.isfinite:
                raise Exception(
                    'Infinite collection cannot be updated without datas!'
                )
            datas = self._datas

        if fields is None:
            fields = self.fields

        # TODO: to require changes on Xt and Xd when X is changed.

        # Update UUID.
        new_uuid = self.uuid00
        for transformation in transformations:
            new_uuid += transformation.uuid00

        from pjdata.finitecollection import FiniteCollection
        return FiniteCollection(
            datas=datas,
            history=self.history + transformations,
            failure=failure,
            original_data=self.original_data,
            uuid=new_uuid,
            fields=fields
        )

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_index == self.size:
            self.next_index = 0
            raise StopIteration('No more Data objects left. Restarted!')
        if isinstance(self._datas, Iterator):
            nex = next(self._datas)
        else:
            nex = self._datas[self.next_index]
        self.next_index += 1
        return nex

    def _uuid_impl00(self):
        return self._uuid

    # Collection not hashable! That's why we memoize it by hand here.
    @property
    def allfrozen(self):
        if self._allfrozen is None:
            self._allfrozen = all(data.isfrozen for data in self._datas)
        return self._allfrozen

    @property
    @lru_cache()
    def frozen(self):
        return FrozenCollection(self)

    @property
    @lru_cache()
    def isfinite(self):
        from pjdata.finitecollection import FiniteCollection
        return isinstance(self, FiniteCollection)


@dataclass
class FrozenCollection:
    collection: Collection
    isfrozen = True

    def __post_init__(self):
        self.failure = self.collection.failure

    def field(self, field, component=None):
        raise Exception('This is a result from an early ended pipeline!\n'
                        'Access field() through FrozenCollection.collection\n'
                        'HINT: probably an ApplyUsing is missing around a '
                        'Predictor')
