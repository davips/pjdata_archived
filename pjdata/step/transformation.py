from functools import lru_cache

from pjdata.aux.encoders import UUID
from pjdata.aux.serialization import deserialize
from pjdata.mixin.identifyable import Identifyable
from pjdata.mixin.printable import Printable


class Transformation(Identifyable, Printable):
    def __init__(self, transformer, step):
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.name, self.path = transformer.name, transformer.path
        self.transformer_uuid00 = transformer.uuid00
        self._serialized_transformer = transformer.serialized
        super().__init__(self._serialized_transformer)
        self.step = step

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._serialized_transformer)

    def _uuid_impl00(self):
        return self.transformer_uuid00 + UUID(self.step.encode())


# class NoTransformation(type):
#     transformer = None
#     step = None
#     name = None
#     path = None
#     config = None
#     from pjdata.aux.encoders import int2pretty
#     uuid = 'T' + int2pretty(0)
#
#     def __new__(cls, *args, **kwargs):
#         raise Exception(
#             'NoTransformation is a singleton and shouldn\'t be instantiated')
#
#     def __bool__(self):
#         return False
