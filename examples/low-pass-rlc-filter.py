####################################################################################################

import numpy as np
from matplotlib import pylab

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Netlist import Circuit
from PySpice.Pipe import SpiceServer
from PySpice.Units import *

from BodeDiagram import bode_diagram

####################################################################################################

spice_server = SpiceServer()

####################################################################################################

circuit = Circuit('Four double-pole Low-Pass RLC Filter')

circuit.Sinusoidal('input', 'in', circuit.gnd, amplitude=1)
# pulse 0 5 10 ms
# Q = .5
circuit.R(1, 'in', 2, 200)
circuit.L(1, 2, 3, milli(10))
circuit.C(1, 3, circuit.gnd, micro(1)) # vout = 3
# Q = 1
circuit.R(2, 'in', 4, 100)
circuit.L(2, 4, 5, milli(10))
circuit.C(2, 5, circuit.gnd, micro(1))
# Q = 2
circuit.R(3, 'in', 6, 50)
circuit.L(3, 6, 7, milli(10))
circuit.C(3, 7, circuit.gnd, micro(1))
# Q = 4
circuit.R(4, 'in', 8, 25)
circuit.L(4, 8, 9, milli(10))
circuit.C(4, 9, circuit.gnd, micro(1))

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.save('V(in)', 'V(1)', 'V(2)', 'V(3)', 'V(4)')
simulation.ac(start_frequency=100, stop_frequency=kilo(10), number_of_points=100,  variation='dec')
print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

analysis = raw_file.analysis

bode_diagram(frequency=analysis.frequency.v,
             gain=20*np.log10(np.absolute(analysis['4'].v)),
             phase=np.angle(analysis['4'].v, deg=False),
             title="Bode Diagram of a Low-Pass RLC Filter",
             marker='.',
             color='blue',
             linestyle='-',
            )
pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
