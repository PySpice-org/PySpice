####################################################################################################

import os

import numpy as np
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
Vcollector = circuit.V('collector', 'collector', circuit.gnd, 5)
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'generic')
circuit.model('generic', 'npn')

figure = pylab.figure()
axe = pylab.subplot(111)
axe.grid()
for base_voltage in np.arange(-1, 5, 1):
    # Fixme: parameters API
    Vbase.parameters[0] = base_voltage

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vcollector=slice(-5, 5, .01))

    # Fixme: lower case 
    # pylab.plot(analysis.vbase, analysis.vcollector)
    # pylab.plot(analysis.collector, -analysis.vbase*1e6)
    axe.plot(analysis.collector, -analysis.vcollector)

####################################################################################################

circuit = Circuit('Transistor')
# Ibase = circuit.I('base', 'base', circuit.gnd, micro(10))
Ibase = circuit.I('base', '1', circuit.gnd, micro(10))
circuit.R('base', 1, 'base', milli(1))
Vcollector = circuit.V('collector', 'collector', circuit.gnd, 5)
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'generic')
circuit.model('generic', 'npn')

# Fixme: ngspice doesn't support current sweep ???
# analysis = simulator.dc(Vcollector=slice(0, 5, .1), Ibase=slice(micro(10), micro(100), micro(10)))
# 0 v(i-sweep)    voltage
# 1 v(collector)  voltage
# 2 v(base)       voltage
# 3 i(vcollector) current
# [  4.00000000e+00   5.00000000e+00   6.00000000e+00   4.00000000e+00 5.00000000e+00   6.00000000e+00]
# [  4.00000000e+00   5.00000000e+00   6.00000000e+00   4.00000000e+00 5.00000000e+00   6.00000000e+00]
# [ -4.99999800e+06  -4.99999750e+06  -4.99999700e+06  -9.99999800e+06 -9.99999750e+06  -9.99999700e+06]
# [ -5.00000600e-06  -5.00000750e-06  -5.00000900e-06  -1.00000060e-05 -1.00000075e-05  -1.00000090e-05]

# analysis = simulator.dc(Vcollector=slice(0, 10, .1))
# 0 v(v-sweep)      voltage
# 1 v(collector)    voltage
# 2 v(base) voltage
# 3 i(vcollector)   current

# analysis = simulator.dc(Ibase=slice(micro(10), micro(100), micro(10)))
# 0 v(i-sweep)      voltage
# 1 v(collector)    voltage
# 2 v(base) voltage
# 3 i(vcollector)   current

# Fixme: something is wrong Icollector(Vcollector) = cst
figure = pylab.figure()
axe = pylab.subplot(111)
axe.grid()
for base_current in np.arange(1, 50, 10):
    # Fixme: parameters API
    Ibase.parameters[0] = milli(base_current)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vcollector=slice(-1, 5, .01))

    # Fixme: lower case 
    # pylab.plot(analysis.vbase, analysis.vcollector)
    axe.plot(analysis.collector, -analysis.vcollector)

####################################################################################################

pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
