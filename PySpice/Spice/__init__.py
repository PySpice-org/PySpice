####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = []

####################################################################################################

import logging

from . import BasicElement
from . import HighLevelElement
from .Element import ElementParameterMetaClass
from .Netlist import Netlist

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def _get_elements(module):
    return [
        _
        for _ in module.__dict__.values()
        if type(_) is ElementParameterMetaClass and _.PREFIX is not None
    ]

####################################################################################################

def _init():
    """Add a method to create elements to the Netlist class.

    .. code-block::

        circuit.R(*args, **kwargs)
        # =>
        R(circuit, *args, **kwargs)

    """

    spice_elements = _get_elements(BasicElement)
    high_level_elements = _get_elements(HighLevelElement)

    for element_class in spice_elements + high_level_elements:

        def make_wrapper(element_class):
            def function(self, *args, **kwargs):
                return element_class(self, *args, **kwargs)
            # Preserve docstrings for element shortcuts
            # Fixme: But Sphinx redumps it...
            function.__doc__ = element_class.__doc__
            function.ELEMENT_CLASS = element_class
            return function

        wrapper = make_wrapper(element_class)

        def register(name):
            # _module_logger.debug("Add device shortcut {} for class {}".format(name, element_class))
            setattr(Netlist, name, wrapper)

        register(element_class.__name__)
        if element_class in spice_elements:
            if hasattr(element_class, 'ALIAS'):
                register(element_class.ALIAS)
            if hasattr(element_class, 'LONG_ALIAS'):
                register(element_class.LONG_ALIAS)

_init()
