"""Mixin class for printing components."""
import json
from typing import Dict

from pjdata import glconfig


def enable_global_pretty_printing():
    """Enable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = True


def disable_global_pretty_printing():
    """Disable globally the pretty-printing."""
    glconfig.PRETTY_PRINTING = False


class Printable:
    """Mixin class for deal with string printing style."""

    def __init__(self, jsonable: Dict):
        """Mixin class for deal with string printing style."""
        self.jsonable = jsonable
        self.pretty_printing = glconfig.PRETTY_PRINTING

    def enable_pretty_printing(self):
        """Enable the pretty-printing."""
        self.pretty_printing = True

    def disable_pretty_printing(self):
        """Disable the pretty-printing."""
        self.pretty_printing = False

    def __str__(self, depth=''):
        # pylint: disable=import-outside-toplevel
        from pjdata.step.transformation import Transformation
        # pylint: disable=import-outside-toplevel
        from pjdata.aux.encoders import CustomJSONEncoder

        # TODO: is Transformation still used?
        if isinstance(self, Transformation):
            # Taking transformer out of string for a better printing.
            jsonable = self.jsonable.copy()
            print(111111111111111, jsonable)
            jsonable['transformer'] = json.loads(jsonable['transformer'])
        else:
            jsonable = self.jsonable

        if not self.pretty_printing:
            js_str = json.dumps(jsonable, cls=CustomJSONEncoder,
                                sort_keys=False, indent=0, ensure_ascii=False)
            return js_str.replace('\n', '')

        js_str = json.dumps(jsonable, cls=CustomJSONEncoder,
                            sort_keys=False, indent=4, ensure_ascii=False)
        return js_str.replace('\n', '\n' + depth)

    def __repr__(self):
        return 'Object: ' + super().__repr__() + '\nContent:' + str(self)
