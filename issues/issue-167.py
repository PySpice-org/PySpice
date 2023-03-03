####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

from PySpice.Spice.NgSpice.Shared import NgSpiceShared

####################################################################################################

from pathlib import Path

# libraries_path = find_libraries()
spice_library = SpiceLibrary(Path(__file__).parent) # libraries_path

####################################################################################################

circuit = Circuit('Stator Drive')

circuit.include(spice_library['issue-167'])

circuit.X(1, 'test_netlist', 'gate_drive1', 'sw_node_hs1', 'gate_drive2', 'sw_node_hs2')

print(circuit)

# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=.005E-6, start_time=1E-3, end_time=3.5E-3, use_initial_condition=False)

# NUMBER_PLOTS = '4'
# #plots of circuit components
# figure = plt.figure(1, (10, 5))
# plot1 = plt.subplot(int(NUMBER_PLOTS+'11'))
# plot(analysis.gate_drive1)
# plt.legend(('gate drive 1 [V]', '',''), loc=(.8,.8))
# plt.grid()
# plt.xlabel('t [s]')
# plt.ylabel('[V]')
# plot2 = plt.subplot(int(NUMBER_PLOTS+'12'))
# plot(analysis.sw_node_hs1)
# plt.legend(('Switch Node 1',''), loc=(.05,.1))
# plt.grid()
# plt.xlabel('t [s]')
# plt.ylabel('[V]')
# plot3 = plt.subplot(int(NUMBER_PLOTS+'13'))
# plot(analysis.gate_drive2)
# plt.grid()
# plt.xlabel('t [s]')
# plt.ylabel('[V]')
# plt.legend(('gate drive 2',''), loc=(.05,.1))
# plot4 = plt.subplot(int(NUMBER_PLOTS+'14'))
# plot(analysis.sw_node_hs2)
# plt.grid()
# plt.xlabel('t [s]')
# plt.ylabel('[V]')
# plt.legend(('sw node 2',''), loc=(.05,.1))
# plt.tight_layout()
plt.show()
