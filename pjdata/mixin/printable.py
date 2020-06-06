"""Mixin class for printing components."""
import json
from abc import abstractmethod

from pjdata import glconfig
from pjdata.aux.util import Property


def enable_global_pretty_printing():
    """Enable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = True


def disable_global_pretty_printing():
    """Disable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = False


class Printable:
    """Mixin class to deal with string printing style"""
    pretty_printing = glconfig.PRETTY_PRINTING

    @Property
    @abstractmethod
    def jsonable(self):
        pass

    def enable_pretty_printing(self):
        """Enable the pretty-printing."""
        self.pretty_printing = True

    def disable_pretty_printing(self):
        """Disable the pretty-printing."""
        self.pretty_printing = False

    def __str__(self, depth: str = ''):
        # pylint: disable=import-outside-toplevel
        from pjdata.transformer import Transformer
        # pylint: disable=import-outside-toplevel
        from pjdata.aux.customjsonencoder import CustomJSONEncoder

        # TODO: is Transformation still used?
        if isinstance(self, Transformer):
            # Taking transformer out of string for a better printing.
            jsonable = self.jsonable.copy()
            jsonable['component'] = json.loads(jsonable['component'])
        else:
            jsonable = self.jsonable

        if not self.pretty_printing:
            js_str = json.dumps(jsonable, cls=CustomJSONEncoder,
                                sort_keys=False, indent=0, ensure_ascii=False)
            return js_str.replace('\n', '')

        js_str = json.dumps(jsonable, cls=CustomJSONEncoder,
                            sort_keys=False, indent=4, ensure_ascii=False)
        return js_str.replace('\n', '\n' + depth)

    __repr__ = __str__
    # def __repr__(self):
    #     return 'Object: ' + super().__repr__() + '\nContent:' + str(self)
