####################################################################################################

import os

from matplotlib import pylab

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(__file__), 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

# circuit = Circuit('Transistor')

# Vemitter = circuit.V('emitter', 'emitter', circuit.gnd, 1)
# Vcollector = circuit.V('collector', circuit.gnd, 'collector', 10)
# circuit.BJT(1, 'collector', circuit.gnd, 'emitter', 'generic')
# circuit.model('generic', 'npn')

# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.dc(Vemitter=slice(-1, 2, .1))

# # Fixme: Vemitter -> vemitter .i
# pylab.plot(analysis.emitter, analysis.vemitter)
# # pylab.axvline(x=-5.6, color='blue')
# pylab.legend(('Diode curve',), loc=(.1,.8))
# pylab.grid()
# pylab.xlabel('Voltage [V]')
# pylab.ylabel('Current [A]')
# pylab.show()

####################################################################################################

circuit = Circuit('Transistor')

Vbase = circuit.V('base', '1', circuit.gnd, 3)
circuit.R('base', 1, 'base', kilo(100))
Vcollector = circuit.V('collector', 'collector', circuit.gnd, 10)
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'generic')
circuit.model('generic', 'npn')

print str(circuit)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vcollector=slice(-1, 5, .01), Vbase=slice(-1, 5, 1))
# analysis = simulator.dc(Vbase=slice(-1, 10, .1))

# Fixme: lower case 
# pylab.plot(analysis.vbase, analysis.vcollector)
pylab.plot(analysis.collector, -analysis.vcollector, 'o')
pylab.grid()
pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
