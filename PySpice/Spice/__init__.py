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

####################################################################################################

import logging

from . import BasicElement
from . import HighLevelElement
from .Netlist import Netlist, ElementParameterMetaClass

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def _get_elements(module):
    element_classes = []
    for item  in module.__dict__.values():
        if (type(item) is ElementParameterMetaClass
            and item.PREFIX is not None
           ):
            element_classes.append(item)
    return element_classes

####################################################################################################
#
# Add a method to create elements to the Netlist class
#

spice_elements = _get_elements(BasicElement)
high_level_elements = _get_elements(HighLevelElement)

for element_class in spice_elements + high_level_elements:

    def _make_function(element_class):
        def function(self, *args, **kwargs):
            return element_class(self, *args, **kwargs)
        # Preserve docstrings for element shortcuts
        function.__doc__ = element_class.__doc__
        return function

    func = _make_function(element_class)

    def _set(name):
        # _module_logger.debug("Add device shortcut {} for class {}".format(name, element_class))
        setattr(Netlist, name, func)

    _set(element_class.__name__)

    if element_class in spice_elements:
        if hasattr(element_class, 'ALIAS'):
            _set(element_class.ALIAS)
        if hasattr(element_class, 'LONG_ALIAS'):
            _set(element_class.LONG_ALIAS)


