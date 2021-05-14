#r# This example shows the computation of the DC bias and sensitivity in a voltage divider.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice import Circuit, Simulator
from PySpice.Unit import *

####################################################################################################

#f# circuit_macros('voltage-divider.m4')

circuit = Circuit('Voltage Divider')

circuit.V('input', 'in', circuit.gnd, 10@u_V)
circuit.R(1, 'in', 'out', 9@u_kΩ)
circuit.R(2, 'out', circuit.gnd, 1@u_kΩ)

####################################################################################################

simulator = Simulator.factory()
simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)

analysis = simulation.operating_point()
for node in (analysis['in'], analysis.out): # .in is invalid !
    print('Node {}: {} V'.format(str(node), float(node)))
#o#

# Fixme: Xyce sensitivity analysis
analysis = simulation.dc_sensitivity('v(out)')
for element in analysis.elements.values():
    print(element, float(element))
#o#
