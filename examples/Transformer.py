####################################################################################################

from PySpice.Spice.Netlist import SubCircuit
from PySpice.Unit.Units import *

####################################################################################################

# Fixme: as class
# Fimxe: how to set parameters

transformer = SubCircuit('Transformer',
                         'input_plus', 'input_minus',
                         'output_plus', 'output_minus')
# Fixme: simpler ...
circuit = transformer

# L_primary / L_secondary = (N1/N2)^2 
#
# For an ideal transformer you can reduce the values for the flux leakage inductances, the copper
# resistors and the winding capacitances.

# Primary
circuit.C('primary', 'input_plus', 'input_minus', pico(20))
circuit.L('primary_leakage', 'input_plus', 1, milli(1))
primary_inductor = circuit.L('primary', 1, 2, 1)
circuit.R('primary', 2, 'output_minus', 1)

# Secondary
circuit.C('secondary', 'output_plus', 'output_minus', pico(20))
circuit.L('secondary_leakage', 'output_plus', 3, milli(1))
secondary_inductor = circuit.L('secondary', 3, 4, .5)
circuit.R('secondary', 4, 'output_minus', 1)

# Coupling
circuit.CoupledInductor('coupling', primary_inductor.name, secondary_inductor.name, .999)

####################################################################################################
# 
# End
# 
####################################################################################################
