from __future__ import annotations

import json
import typing
from abc import ABC, abstractmethod
from functools import lru_cache

from pjdata.mixin.withserialization import WithSerialization

if typing.TYPE_CHECKING:
    import pjdata.types as t

from pjdata.aux.serialization import serialize, deserialize
from pjdata.aux.util import Property
from pjdata.aux.uuid import UUID
from pjdata.mixin.withidentification import WithIdentification
from pjdata.mixin.printable import Printable


class Transformer(WithIdentification, Printable, ABC):
    def __init__(self, component: WithSerialization):
        """Base class for all transformers.

        ps. Assumes all components are symmetric. This class uses the same component details for both enhance and model.
        """
        # I.e. the transformation is always the same, no matter at which step (modeling/enhancing) we are.
        self._name, self.path = component.name, component.path
        self.component_uuid = component.uuid
        self._serialized_component = component.serialized
        self._jsonable = {
            'uuid': self.uuid,
            'name': self.name,
            'path': self.path,
            'component_uuid': component.uuid,
            'component': self._serialized_component
        }

    @Property
    @lru_cache()
    def longname(self):
        return self.__class__.__name__ + f"[{self.name}]"

    @Property
    @lru_cache()
    def serialized(self):
        return serialize(self)

    @Property
    @lru_cache()
    def config(self):
        return deserialize(self._serialized_component)

    @staticmethod
    def materialize(serialized):
        jsonable = json.loads(serialized)

        class FakeComponent:
            name = jsonable['name']
            path = jsonable['path']
            uuid = UUID(jsonable['component_uuid'])
            serialized = jsonable['component']

        component = FakeComponent()
        return Transformer(component, )  # TODO: how to materialize func?

    def transform(self, content: t.DataOrTup, exit_on_error=True) -> t.DataOrTup:
        if isinstance(content, tuple):
            return tuple((dt.transformedby(self) for dt in content))
        # Todo: We should add exception handling here because self.func can raise errors
        # print(' transform... by', self.name)
        return content.transformedby(self)

    @abstractmethod
    def rawtransform(self, content: t.Data) -> t.Result:
        pass

    @Property
    def _jsonable_impl(self):
        return self._jsonable

    def _name_impl(self):
        return self._name

