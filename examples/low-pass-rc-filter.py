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

circuit = Circuit('Low-Pass RC Filter')

circuit.Sinusoidal('input', 'in', circuit.gnd, amplitude=1)
circuit.R('f', 'in', 'out', kilo(1))
circuit.C('f', 'out', circuit.gnd, micro(1))

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.save('V(in)', 'V(out)')
simulation.ac(start_frequency=1, stop_frequency=mega(1), number_of_points=10,  variation='dec')
print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

data = raw_file.data

bode_diagram(frequency=data['frequency'].real,
             gain=20*np.log10(np.absolute(data['v(out)'])),
             phase=np.angle(data['v(out)'], deg=False),
             title="Bode Diagram of a Low-Pass RC Filter",
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
