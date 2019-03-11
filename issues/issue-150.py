####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

thevenin_circuit = Circuit('Thevenin Representation')

thevenin_circuit.V('input', 1, thevenin_circuit.gnd, 10@u_V)
thevenin_circuit.R('generator', 1, 'load', 10@u_Ω)
thevenin_circuit.R('load', 'load', thevenin_circuit.gnd, 1@u_kΩ)

simulator = thevenin_circuit.simulator(simulator='xyce-serial', temperature=25, nominal_temperature=25)
# simulator._spice_server._xyce_command = "C:\\Program Files\\Xyce 6.10 OPENSOURCE\\bin\\Xyce.exe"
analysis = simulator.operating_point()

load_node = analysis.load
print('Node {}: {:5.2f} V'.format(str(load_node), float(load_node)))
#o#
