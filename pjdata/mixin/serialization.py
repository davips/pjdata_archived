from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from functools import lru_cache

if typing.TYPE_CHECKING:
    pass

from pjdata.aux.serialization import serialize
from pjdata.aux.util import Property
from pjdata.mixin.identification import withIdentification


class withSerialization(withIdentification, ABC):
    path = None

    @lru_cache()
    def cfuuid(self, data=None):
        """UUID excluding 'model' and 'enhance' flags. Identifies the *transformer*."""
        return self._cfuuid_impl(data)

    @Property
    @lru_cache()
    def serialized(self):
        # print('TODO: aproveitar processamento do cfserialized()!')  # <-- TODO
        return serialize(self)

    @abstractmethod
    def _cfuuid_impl(self, data=None):
        pass
