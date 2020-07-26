from __future__ import annotations

from typing import TYPE_CHECKING

import pjdata.mixin.serialization as ser

if TYPE_CHECKING:
    import pjdata.types as t
import pjdata.aux.uuid as u
import pjdata.transformer.transformer as tr


class PHolder(tr.Transformer):  # TODO: Find a better name? Skiper?
    """Placeholder for a component to appear in history but do nothing.

    Optionally a transformation 'idholder_func' can be passed, e.g. to freeze data.
    """
    ispholder = True

    def __init__(self, component: t.Union[str, ser.withSerialization], idholder_func: t.Transformation = None):
        self._uuid = u.UUID.identity
        self._rawtransform = (lambda _: {}) if idholder_func is None else idholder_func
        super().__init__(component)

    def rawtransform(self, content: t.Data) -> t.Result:
        return self._rawtransform(content)

    def _uuid_impl(self):
        return self._uuid
