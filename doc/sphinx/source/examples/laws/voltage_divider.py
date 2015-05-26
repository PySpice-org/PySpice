####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

####################################################################################################

circuit = Circuit('Voltage Divider')

circuit.V('input', 1, circuit.gnd, 10) # Fixme: V(10) uV(10) 10*V
circuit.R(1, 1, 2, kilo(2))
circuit.R(2, 2, circuit.gnd, kilo(1))

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {} V'.format(str(node), float(node))) # Fixme: format value + unit

####################################################################################################
#
# End
#
####################################################################################################
