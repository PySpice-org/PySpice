# from pylab import *
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import BehavioralSource

circuit = Circuit('Pulse')

source = circuit.BehavioralSource('source', 'in', circuit.gnd, voltage_expression = 'time^4*exp(-1000*time)')
# look like a " is simply discarded
# source = circuit.BehavioralSource('source', 'in', circuit.gnd, voltage_expression = '"time^4*exp(-1000*time)')

circuit.R(1, 'in', 'out', u_kOhm(9))
circuit.R(2, 'out', circuit.gnd, u_kOhm(1))

print(circuit)

simulator = circuit.simulator(simulator='ngspice-shared')
# the commented out version next line works
#simulator = circuit.simulator(simulator='ngspice-subprocess')
transient = simulator.transient(step_time=u_ms(1e-3), end_time=u_ms(20), log_desk=True)

# print(type(simulator)) -> PySpice.Spice.NgSpice.Simulation.NgSpiceSharedCircuitSimulator
# circuit must be loaded
print('-'*100)
print(simulator.ngspice.listing())
print('-'*100)

# clf()
plt.grid(True)
plt.plot(transient['out'].abscissa, transient['out'])
plt.show()
