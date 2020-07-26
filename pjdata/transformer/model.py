from __future__ import annotations

from typing import Any, TYPE_CHECKING, Union, Dict

from pjdata.mixin.serialization import withSerialization
from pjdata.transformer.info import Info
from pjdata.transformer.transformer import Transformer

if TYPE_CHECKING:
    import pjdata.types as t


class Model(Transformer):
    def __init__(
        self, component: withSerialization, func: t.Transformation, info: Union[Info, Dict[str, Any]], data: t.Data
    ):
        self._rawtransform = func
        self.info = info if isinstance(info, Info) else Info(items=info)

        # The multiplication order here cannot be otherwise, because it would mean "data output from enhancer".
        # PCA is an example where enhUUID != modUUID; apesar de que ambos deveriam ser modUUID/ mas é impossível, pois enh não conhece o data futuro
        self._uuid = component.cfuuid(data) * data.uuid
        super().__init__(component)

    def rawtransform(self, content: t.Data) -> t.Result:
        return self._rawtransform(content)

    def _uuid_impl(self):
        return self._uuid
