####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from . import NetlistElement
from .Netlist import Netlist

####################################################################################################

for element in (NetlistElement.Resistor,
                NetlistElement.Capacitor,
                NetlistElement.Inductor,
                NetlistElement.Diode,
                NetlistElement.VoltageSource,
            ):
    def make_function(element):
        def function(self, *args, **kwargs):
            self._add_element(element(*args, **kwargs))
        return function
    setattr(Netlist, element.prefix, make_function(element))

####################################################################################################
# 
# End
# 
####################################################################################################
