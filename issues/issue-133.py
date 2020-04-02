####################################################################################################

import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

circuit = Circuit('test')

R1 = circuit.R(1, 'p1', 'p2', 4@u_kΩ)
R2 = circuit.R(2, 'p2', 'p6', 1@u_kΩ)
R3 = circuit.R(3, 'p1', 'p5', 1@u_kΩ)
R4 = circuit.R(4, 'p5', 'p6', 1@u_kΩ)
R5 = circuit.R(5, 'p6', 0, 1e-9@u_Ω)

I1 = circuit.I(1, 0, 'p1', 1@u_A)

V1 = circuit.V(1, 'p1', 'p4', -10@u_V)
V2 = circuit.V(2, 'p2', 'p3', -10@u_V)

print(str(circuit))

simulator = circuit.simulator(simulator='xyce-serial')
analysis = simulator.operating_point()

for node in analysis.nodes.values():
    print('Node {}: {:5.2f} V'.format(str(node),  float(node)))
for node in analysis.branches.values():
    print('Node {}: {:5.2f} A'.format(str(node),  float(node)))
