#r# This example shows the computation of the DC bias and sensitivity in a voltage divider.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy
from sys import argv

####################################################################################################

#f# circuit_macros('voltage-divider.m4')

circuit = Circuit('Voltage Divider')

circuit.V('input', 'in_node', circuit.gnd, 10@u_V)
circuit.R(1, 'in_node', 'out', 9@u_kΩ)
circuit.R(2, 'out', circuit.gnd, 1@u_kΩ)

####################################################################################################

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

analysis = simulator.operating_point()
for node in (analysis['in_node'], analysis.out): # .in is invalid !
    print('Node {}: {} V'.format(str(node), float(node)))
if len(argv) == 2 and argv[1] == "--dump":
    data = numpy.array([float(analysis['in_node']), float(analysis.out)])
    numpy.save('./results/voltage-divider', data)
#o#

# Fixme: Xyce sensitivity analysis
# TODO Enable DC sensitivity tests
### analysis = simulator.dc_sensitivity('v(out)')
### for element in analysis.elements.values():
###     print(element, float(element))
#o#
