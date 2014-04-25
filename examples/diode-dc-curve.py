####################################################################################################

import os

from matplotlib import pylab

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Unit.Units import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(__file__), 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

circuit = Circuit('Diode DC Curve')

circuit.include(spice_library['1N4148'])
# 1N5919B: 5.6 V, 3.0 W Zener Diode Voltage Regulator
circuit.include(spice_library['d1n5919brl'])

circuit.V('input', 'in', circuit.gnd, '10V')
circuit.R(1, 'in', 'out', kilo(1))
# circuit.X('D1', '1N4148', 'out', circuit.gnd)
circuit.X('DZ1', 'd1n5919brl', 'out', circuit.gnd)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(-20, 20, .1))

# pylab.plot(data['v(out)'], (data['v(in)'] - data['v(out)'])/1000)
pylab.plot(analysis.out, -analysis.vinput) # .i
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
