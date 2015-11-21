####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit.Units import *

####################################################################################################

circuit = Circuit('Regulator')

# Netlist.TwoPortElement
# .. warning:: As opposite to Spice, the input nodes are specified before the output nodes.
# circuit.VCVS(1, 1, 0, 2, 0, , milli(50))

gain = SubCircuit('GAIN', 1, 2, K=milli(20))
gain.VCVS(1, 1, 0, 2, 0, '{K}')

circuit.subcircuit(gain)
circuit.X(2, 'GAIN', 7, 6, K=milli(50))

print(str(circuit))

####################################################################################################
#
# End
#
####################################################################################################
