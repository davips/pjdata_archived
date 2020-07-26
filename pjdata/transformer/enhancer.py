from __future__ import annotations

from abc import abstractmethod
from functools import lru_cache
from typing import Callable, TYPE_CHECKING, Union, Dict, Any

from pjdata.mixin.serialization import withSerialization
from pjdata.transformer.info import Info
from pjdata.transformer.transformer import Transformer

if TYPE_CHECKING:
    import pjdata.types as t

from pjdata.aux.util import Property


class Enhancer(Transformer):
    def __init__(self, component: withSerialization, *args):
        # info_func: Callable[[t.Data], Union[Info, Dict[str, Any]]]
        self._uuid = component.cfuuid()
        super().__init__(component)

    @Property
    @lru_cache()
    def info(self, data: t.Data) -> Info:
        info = self._info_impl(data)
        return info if isinstance(info, Info) else Info(items=info)

    @abstractmethod
    def _info_impl(self, data):
        pass

    def _uuid_impl(self):
        return self._uuid
