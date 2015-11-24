####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit.Units import *

####################################################################################################

circuit = Circuit('Test')

summer = SubCircuit('Sum', 1, 2, 3, K1=1.0, K2=1.0)
summer.BehavorialSource(1, 3, summer.gnd, v='{K1}*V(1) + {K2}*V(2)')
summer.BehavorialSource(2, 3, summer.gnd, voltage_expression='{K1}*V(1) + {K2}*V(2)')

print(summer.B1.v)
print(summer.B1.voltage_expression)

print(str(summer))

####################################################################################################
#
# End
#
####################################################################################################
