####################################################################################################

import logging

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

from PySpice.Netlist import Circuit
from PySpice.Pipe import SpiceServer
from PySpice.Units import *

####################################################################################################

spice_server = SpiceServer()

####################################################################################################

circuit = Circuit('Voltage Divider')

circuit.V('input', 'in', circuit.gnd, '10V')
circuit.R(1, 'in', 'out', kilo(9))
circuit.R(2, 'out', circuit.gnd, kilo(1))

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.operating_point()

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

data = raw_file.data
for node in ('in', 'out'):
    print 'Node {}: {} V'.format(node, data['v({})'.format(node)][0])

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.dc_sensitivity('v(out)')

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field, raw_file.data[field.name]

####################################################################################################
# 
# End
# 
####################################################################################################
