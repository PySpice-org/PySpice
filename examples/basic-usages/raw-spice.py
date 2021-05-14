#r# =========================================
#r#  Pass Raw Spice Definitions to a Netlist
#r# =========================================

#Fixme: to be documented, improved

#r# This example shows how to pass raw spice definitions to a netlist.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice import Circuit
from PySpice.Unit import *

####################################################################################################

#r# Let define a circuit.

circuit = Circuit('Test')

#r# Pass raw Spice definitions to a circuit, aka netlist, content is inserted at the beginning of
#r# the netlist.
circuit.raw_spice = '''
Vinput in 0 10V
R1 in out 9kOhm
'''

#r# Pass element parameters as raw Spice, content is concatenated with `R2 out 0`
circuit.R(2, 'out', 0, raw_spice='1k')

print(circuit)
#o#
