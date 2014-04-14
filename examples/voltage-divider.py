####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

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

####################################################################################################

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.operating_point()
print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

analysis = raw_file.analysis
for node in (analysis['in'], analysis.out): # .in is invalid !
    print 'Node {}: {} V'.format(str(node), float(node))

####################################################################################################

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.dc_sensitivity('v(out)')
print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

analysis = raw_file.analysis
for element in analysis.elements.itervalues():
    print element, element.v

####################################################################################################
# 
# End
# 
####################################################################################################
