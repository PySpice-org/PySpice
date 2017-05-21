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

from . import BasicElement
from . import HighLevelElement
from .Netlist import Netlist, ElementParameterMetaClass

####################################################################################################

def _get_elements(module):
    element_classes = []
    for item  in module.__dict__.values():
        if (type(item) is ElementParameterMetaClass
            and item.prefix is not None
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
            element = element_class(*args, **kwargs)
            self._add_element(element)
            return element
        return function

    if element_class in spice_elements and hasattr(element_class, 'alias'):
        function_name = element_class.alias
    else:
        function_name = element_class.__name__

    setattr(Netlist, function_name, _make_function(element_class))
