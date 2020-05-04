"""Sanity tests"""

# global handler
from pjdata.util import gl_config, ls_gl_config
print(ls_gl_config())
gl_config(pretty_printing=True, does_nothing=False)
