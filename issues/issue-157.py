import numpy as np
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Parameters
frequency = 1e3
period = 1 / frequency
omega = 2 * np.pi * frequency

I_P1 = 100
L_P1 = 1e-6
L_S1 = 10e-6
K_P1S1 = 0.1

circuit = Circuit('2CoupledInductors')

#Primary Side
circuit.I('I2', circuit.gnd, 'N1', 'AC ' + str(I_P1) + '')
circuit.L('L_P1', circuit.gnd, 'N1', str(L_P1))

# Secondary Side
circuit.L('L_S1', circuit.gnd,  'N2', str(L_S1) )
circuit.K('K_P1S1', 'L_P1', 'L_S1', K_P1S1)
# circuit.K('K_P1S1', 'L_P1', 'LL_S1', K_P1S1)
# circuit.K('K_P1S1', 'LL_P1', 'LL_S1', K_P1S1)

print(circuit)

# Do the simulation
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.ac(variation='lin', number_of_points=1, start_frequency=frequency, stop_frequency=frequency)

# Print the results
print('--- Results ---')
for node in analysis.nodes.values():
  print('Node {}: {:5.2f} V'.format(str(node), float(abs(node))))
