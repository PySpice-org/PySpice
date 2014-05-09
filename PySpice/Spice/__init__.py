####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from . import BasicElement
from . import HighLevelElement
from .Netlist import Netlist, Element

####################################################################################################

def _get_elements(module):
    element_classes = []
    for item  in module.__dict__.itervalues():
        if (type(item) is type
            and issubclass(item, Element)
            and item.prefix is not None):
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

    # Fixme: do something more flexible
    # generalise alias usage ?
    if element_class in spice_elements and not hasattr(element_class, '__dont_register_prefix__'):
        function_name = element_class.prefix
    else:
        function_name = element_class.__name__

    setattr(Netlist, function_name, _make_function(element_class))

    if hasattr(element_class, 'alias'):
        function_name = element_class.alias
        setattr(Netlist, function_name, _make_function(element_class))

####################################################################################################
# 
# End
# 
####################################################################################################
