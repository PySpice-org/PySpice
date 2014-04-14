####################################################################################################

import os

from matplotlib import pylab

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Netlist import Circuit
from PySpice.SpiceLibrary import SpiceLibrary
from PySpice.Pipe import SpiceServer
from PySpice.Units import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(__file__), 'libraries')
spice_library = SpiceLibrary(libraries_path)
spice_server = SpiceServer()

####################################################################################################

circuit = Circuit('Diode DC Curve')

circuit.include(spice_library['1N4148'])
# 1N5919B: 5.6 V, 3.0 W Zener Diode Voltage Regulator
circuit.include(spice_library['d1n5919brl'])

circuit.V('input', 'in', circuit.gnd, '10V')
circuit.R(1, 'in', 'out', kilo(1))
# circuit.X('D1', '1N4148', 'out', circuit.gnd)
circuit.X('DZ1', 'd1n5919brl', 'out', circuit.gnd)

simulation = circuit.simulation(temperature=25, nominal_temperature=25)
simulation.dc(Vinput=slice(-20, 20, .1))
print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

analysis = raw_file.analysis
# pylab.plot(data['v(out)'], (data['v(in)'] - data['v(out)'])/1000)
pylab.plot(analysis.out.v, -analysis.vinput.v) # .i
pylab.axvline(x=-5.6, color='blue')
pylab.legend(('Diode curve',), loc=(.1,.8))
pylab.grid()
pylab.xlabel('Voltage [V]')
pylab.ylabel('Current [A]')
pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
