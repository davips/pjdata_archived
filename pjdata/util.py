"""This module keep util function used in pjdata."""
import warnings

import pjdata.glconfig as mconfig


def gl_config(**kwargs):
    """Handle global variables values.

    Parameters
    ----------
    **kwargs : Global variables and their respective new values.

    Notes
    -----
    Use 'ls_gl_config()' to see all global variables available.
    For more information see `global_configuration_handler`.
    """
    global_configuration_handler(module=mconfig, **kwargs)


def ls_gl_config():
    """List global variables from `glconfig` module.

    Notes
    -----
    See `ls_global_configuration_handler` for more information.
    """
    return ls_global_configuration_handler(mconfig)


def ls_global_configuration_handler(module):
    """List global variables from a givem module.

    Parameters
    ----------
    module : module
        A python module.

    Notes
    -----
    Global variables should follow PEP8 format.
    """
    return [item for item in module.__dict__.keys() if item.isupper()]


def global_configuration_handler(module, **kwargs):
    """Handle global variables values.

    Parameters
    ----------
    module : module
        A python module.
    **kwargs
        Global variables and their respective new values.

    Examples
    --------
    >>> from pjdata.util import gl_config
    >>> gl_config(pretty_printing=True, does_nothing=False)

    Notes
    -----
    Use 'ls_global_configuration_handler()' to see all global variables
    available from a given python module.
    """
    gl_var = ls_global_configuration_handler(module)
    for key, value in kwargs.items():
        key = key.upper()
        if key in gl_var:
            module.__dict__[key] = value
        else:
            warnings.warn(f'Variable {key} not found.'
                          f'This configuration was ignored!')
