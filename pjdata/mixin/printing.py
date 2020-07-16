"""Mixin class for printing components."""
import json
from abc import abstractmethod
from functools import cached_property

from pjdata import glconfig


def enable_global_pretty_printing():
    """Enable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = True


def disable_global_pretty_printing():
    """Disable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = False


class withPrinting:
    """Mixin class to deal with string printing style"""

    pretty_printing = glconfig.PRETTY_PRINTING

    @cached_property
    def jsonable(self):
        return self._jsonable_impl()

    @abstractmethod
    def _jsonable_impl(self):
        pass

    def enable_pretty_printing(self):
        """Enable the pretty-printing."""
        self.pretty_printing = True

    def disable_pretty_printing(self):
        """Disable the pretty-printing."""
        self.pretty_printing = False

    def __str__(self, depth: str = ""):
        # pylint: disable=import-outside-toplevel
        from pjdata.transformer.transformer import Transformer

        # pylint: disable=import-outside-toplevel
        from pjdata.aux.customjsonencoder import CustomJSONEncoder

        if isinstance(self, Transformer):
            # Taking component out of string for a better printing.
            # jsonable = self.jsonable.copy()
            # jsonable["component"] = json.loads(jsonable["component"])
            jsonable = self.jsonable  # TODO: improve this
        else:
            jsonable = self.jsonable

        if not self.pretty_printing:
            js_str = json.dumps(
                jsonable,
                cls=CustomJSONEncoder,
                sort_keys=False,
                indent=0,
                ensure_ascii=False,
            )
            return js_str.replace("\n", "")

        js_str = json.dumps(
            jsonable,
            cls=CustomJSONEncoder,
            sort_keys=False,
            indent=4,
            ensure_ascii=False,
        )
        return js_str.replace("\n", "\n" + depth)

    __repr__ = __str__
    # def __repr__(self):
    #     return 'Object: ' + super().__repr__() + '\nContent:' + str(self)
