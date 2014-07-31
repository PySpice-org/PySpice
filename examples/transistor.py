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

circuit = Circuit('Transistor')

Vbase = circuit.V('base', '1', circuit.gnd, 1)
circuit.R('base', 1, 'base', kilo(1))
Vcollector = circuit.V('collector', '2', circuit.gnd, 0)
circuit.R('collector', 2, 'collector', kilo(1))
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'generic')
circuit.model('generic', 'npn')

####################################################################################################

figure = pylab.figure()

####################################################################################################

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vbase=slice(-1, 3, .01))

axe = pylab.subplot(121)
# Fixme: i(vinput) -> analysis.vinput
axe.plot(analysis.base, -analysis.vbase*1000)
axe.axvline(x=.65, color='red')
axe.legend(('Base-Emitter Diode curve',), loc=(.1,.8))
axe.grid()
axe.set_xlabel('Voltage [V]')
axe.set_ylabel('Current [mA]')

####################################################################################################

circuit = Circuit('Transistor')
Ibase = circuit.I('base', circuit.gnd, 'base', micro(10)) # take care to the orientation
Vcollector = circuit.V('collector', 'collector', circuit.gnd, 5)
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'generic')
circuit.model('generic', 'npn')

# Fixme: ngspice doesn't support multi-sweep ???
#   it works in interactive mode
# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.dc(Vcollector=slice(0, 5, .1), Ibase=slice(micro(10), micro(100), micro(10)))
# 0 v(i-sweep)    voltage # Vcollector in fact
# 1 v(collector)  voltage
# 2 v(base)       voltage
# 3 i(vcollector) current
# 0.00000000e+00,   1.00000000e-01,   2.00000000e-01, 3.00000000e-01,   4.00000000e-01,   5.00000000e-01, 6.00000000e-01,   7.00000000e-01,   8.00000000e-01, 9.00000000e-01
# 0.00000000e+00,   1.00000000e-01,   2.00000000e-01, 3.00000000e-01,   4.00000000e-01,   5.00000000e-01, 6.00000000e-01,   7.00000000e-01,   8.00000000e-01, 9.00000000e-01
# 6.50478604e-01,   7.40522920e-01,   7.68606463e-01, 7.69192913e-01,   7.69049191e-01,   7.69050844e-01, 7.69049584e-01,   7.69049559e-01,   7.69049559e-01, 7.69049559e-01
# 9.90098946e-06,  -3.15540984e-04,  -9.59252614e-04, -9.99134834e-04,  -9.99982226e-04,  -1.00005097e-03, -1.00000095e-03,  -9.99999938e-04,  -9.99999927e-04, -9.99999937e-04

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

axe = pylab.subplot(122)
axe.grid()
# axe.legend(('Ic(Vce, Ib)',), loc=(.5,.5))
axe.set_xlabel('Vce [V]')
axe.set_ylabel('Ic [mA]')
for base_current in np.arange(0, 100, 10):
    Ibase.dc_value = micro(base_current)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.dc(Vcollector=slice(0, 5, .01))
    # Fixme: lower case 
    axe.plot(analysis.collector, -analysis.vcollector*1000)

####################################################################################################

pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
