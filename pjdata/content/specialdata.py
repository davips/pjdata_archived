from __future__ import annotations

from typing import Dict, List, Tuple, Optional

import typing

if typing.TYPE_CHECKING:
    import pjdata.types as t
import pjdata.aux.uuid as u
import pjdata.content.data as d
import pjdata.transformer as tr


class UUIDData(d.Data):
    """Exactly like Data, but without matrices and infos.

     The only available information is the UUID."""

    def __init__(self, uuid: u.UUID):
        super().__init__(tuple(), failure=None, frozen=False, hollow=True)
        self._uuid = uuid

    def _uuid_impl(self) -> u.UUID:
        return self._uuid

    def __getattr__(self, item):
        raise Exception(
            'This a UUIDData object. It has no fields!'
        )
    # else:
    #     return self.__getattribute__(item)


class NoData(type):
    """Singleton to feed Data iterators."""
    uuid = u.UUID()
    id = uuid.id
    uuids: dict = {}
    history: List[tr.Transformer] = []
    matrices: Dict[str, t.Field] = {}
    failure = None
    isfrozen = False
    ishollow = False
    allfrozen = False  # TODO: is allfrozen still a thing
    storage_info = None

    @staticmethod
    def hollow(transformers: Tuple[tr.Transformer]) -> d.Data:
        """A light Data object, i.e. without matrices."""
        # noinspection PyCallByClass
        return d.Data.hollow(NoData, transformers)

    @staticmethod
    def transformedby(transformer: tr.Transformer):
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed."""
        result = transformer.func(NoData)
        return result.updated(transformers=(transformer,))

    @staticmethod
    def updated(transformers: Tuple[tr.Transformer],
                failure: Optional[str] = 'keep',
                **fields) -> d.Data:
        # noinspection PyCallByClass
        return d.Data.updated(NoData, transformers, failure, **fields)

    def __new__(mcs, *args, **kwargs):
        raise Exception('NoData is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False
