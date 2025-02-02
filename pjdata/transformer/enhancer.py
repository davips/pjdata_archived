from __future__ import annotations

from abc import abstractmethod, ABC
from functools import lru_cache
from typing import TYPE_CHECKING

from pjdata.mixin.serialization import withSerialization
from pjdata.transformer.info import Info
from pjdata.transformer.transformer import Transformer

if TYPE_CHECKING:
    import pjdata.types as t


class Enhancer(Transformer):
    def __init__(self, component: withSerialization, *args):  # args is here just to ignore training data
        self._uuid = component.cfuuid()
        super().__init__(component)

    @lru_cache()
    def info(self, data: t.Data) -> Info:
        info = self._info_impl(data)
        return info if isinstance(info, Info) else Info(items=info)

    @abstractmethod
    def _info_impl(self, data):
        pass

    def _uuid_impl(self):
        return self._uuid


class DSStep(Enhancer, ABC):
    """Data Science Step. Just a meaningful alias for Enhancer, but for non-real-transformers like File, Metric, etc."""

    pass
