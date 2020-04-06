from abc import ABC
from functools import lru_cache

from pjdata.mixin.identifyable import Identifyable
from pjdata.aux.serialization import serialize, deserialize


class Transformation(Identifyable):
    def __init__(self, transformer, step):
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.step = step
        self._config = transformer.serialized
        self._uuid = transformer.uuid

    def _uuid_impl(self):
        return self.step, self.uuid

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._config)
