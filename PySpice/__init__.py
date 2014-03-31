####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from types import ClassType

####################################################################################################

from . import SpiceElement
from . import HighLevelElement
from .Netlist import Netlist, Element

####################################################################################################

def get_elements(module):
    element_classes = []
    for item  in module.__dict__.itervalues():
        if (type(item) is type
            and issubclass(item, Element)
            and item.prefix is not None):
            element_classes.append(item)
    return element_classes

####################################################################################################

spice_elements = get_elements(SpiceElement)
high_level_elements = get_elements(HighLevelElement)

for element_class in spice_elements + high_level_elements:

    def make_function(element_class):
        def function(self, *args, **kwargs):
            element = element_class(*args, **kwargs)
            self._add_element(element)
            return element
        return function

    if element_class in spice_elements:
        function_name = element_class.prefix
    else:
        function_name = element_class.__name__

    setattr(Netlist, function_name, make_function(element_class))

####################################################################################################
# 
# End
# 
####################################################################################################
