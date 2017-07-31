#!# This example shows the computation of the DC biases in a resistor bridge.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

#cm# resistor-bridge.m4

circuit = Circuit('Resistor Bridge')

circuit.V('input', 1, circuit.gnd, u_V(10))
circuit.R(1, 1, 2, u_kΩ(2))
circuit.R(2, 1, 3, u_kΩ(1))
circuit.R(3, 2, circuit.gnd, u_kΩ(1))
circuit.R(4, 3, circuit.gnd, u_kΩ(2))
circuit.R(5, 3, 2, u_kΩ(2))

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {:4.1f} V'.format(str(node), float(node))) # Fixme: format value + unit
#o#

x = 1 + 2

#!# X is @<@x@>@ \frac
