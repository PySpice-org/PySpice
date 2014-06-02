####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from . import BasicElement
from . import HighLevelElement
from .Netlist import Netlist, Element, ElementParameterMetaClass

####################################################################################################

def _get_elements(module):
    element_classes = []
    for item  in module.__dict__.itervalues():
        if (type(item) is ElementParameterMetaClass
            and item.prefix is not None
           ):
            element_classes.append(item)
    return element_classes

####################################################################################################

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

####################################################################################################
# 
# End
# 
####################################################################################################
