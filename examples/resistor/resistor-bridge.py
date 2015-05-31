####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

####################################################################################################

circuit = Circuit('Resistor Bridge')

circuit.V('input', 1, circuit.gnd, 10) # Fixme: V(10) uV(10) 10*V
circuit.R(1, 1, 2, kilo(2))
circuit.R(2, 1, 3, kilo(1))
circuit.R(3, 2, circuit.gnd, kilo(1))
circuit.R(4, 3, circuit.gnd, kilo(2))
circuit.R(5, 3, 2, kilo(2))

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {:4.1f} V'.format(str(node), float(node))) # Fixme: format value + unit
#o#

####################################################################################################
#
# End
#
####################################################################################################
