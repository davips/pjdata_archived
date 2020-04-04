from abc import ABC
from functools import lru_cache

from pjdata.mixin.identifyable import Identifyable
from pjdata.aux.serialization import serialize, deserialize


class Transformation(Identifyable, ABC):
    def __init__(self, transformer, step):
        """
        Immutable application or use of a Transformer.
        :param transformer: Transformer/Pipeline
        :param step: 'a'pply or 'u'se
        """
        # Precisei retirar referência ao transformer, para que pickle parasse
        # de dar problema ao carregar um objeto Data do PickleServer. Esse
        # problema começar após a unificação ML com CS, sobrescrenvendo
        # __new__ nos containeres. O erro acontecia quando o pickle tentava
        # recriar Containeres do histórico de Data, mas, por algum motivo
        # tentava fazê-lo sem transformers. Serializei config pelo mesmo motivo.
        if step is None:
            raise Exception(
                'Operation cannot be None! Hint: self._transformation() '
                'should be called only during apply() or use() steps!')
        self.serialized = transformer.serialized
        self.step = step
        self.name = transformer.name
        self.path = transformer.path
        self._config = serialize(transformer)

    @property
    @lru_cache()
    def config(self):
        return deserialize(self._config)


class NoTransformation(type):
    transformer = None
    step = None
    name = None
    path = None
    config = None
    from pjdata.aux.encoders import int2tiny
    uuid = 'T' + int2tiny(0)

    def __new__(cls, *args, **kwargs):
        raise Exception(
            'NoTransformation is a singleton and shouldn\'t be instantiated')

    def __bool__(self):
        return False
