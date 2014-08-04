####################################################################################################

import os

import numpy as np
from matplotlib import pylab
import matplotlib.ticker as ticker

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Unit.Units import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

circuit = Circuit('Diode DC Curve')

circuit.include(spice_library['1N4148'])

circuit.V('input', 'in', circuit.gnd, '10V')
circuit.R(1, 'in', 'out', 1) # not required for simulation
circuit.X('D1', '1N4148', 'out', circuit.gnd)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vinput=slice(-2, 2, .01))

# Fixme: i(vinput) -> analysis.vinput

figure = pylab.figure()

axe = pylab.subplot(121)
axe.set_xlabel('Voltage [V]')
axe.set_ylabel('Current')
axe.grid()
# Scale reverse and forward region
forward_region = analysis.out >= 0
reverse_region = np.invert(forward_region)
scaled_current = - analysis.vinput * (reverse_region*1e11 + forward_region*1e3)
axe.set_ylim(-500, 750) # Fixme: round
axe.plot(analysis.out, scaled_current)
# Update y ticks
# tick_locations = np.array(axe.yaxis.get_ticklocs())
# forward_region = tick_locations >= 0
# reverse_region = np.invert(forward_region)
# tick_locations *= reverse_region/100. + forward_region*1.
# tick_labels = []
# for i, tick_location in enumerate(tick_locations):
#     label = '{:.0f}'.format(tick_location)
#     if reverse_region[i]:
#         label += ' nA'
#     else:
#         label += ' mA'
#     tick_labels.append(label)
# axe.yaxis.set_ticklabels(tick_labels)
# for i, tick in enumerate(axe.yaxis.get_major_ticks()):
#     if reverse_region[i]:
#         tick.label.set_color('red')
def my_tick_formatter(value, position):
    if value >= 0:
        return '{} mA'.format(value)
    else:
        return '{} nA'.format(value/100)
formatter = ticker.FuncFormatter(my_tick_formatter)
axe.yaxis.set_major_formatter(formatter)
axe.legend(('1N4148 Characteristic Curve',), loc=(.1,.8))
axe.axvline(x=0, color='black')
axe.axhline(y=0, color='black')
axe.axvline(x=.7, color='red')

axe = pylab.subplot(122)
axe.grid()
static_resistance = -analysis.out / analysis.vinput
dynamic_resistance = np.diff(-analysis.out) / np.diff(analysis.vinput)
axe.semilogy(analysis.out, static_resistance, basey=10)
axe.semilogy(analysis.out[10:-1], dynamic_resistance[10:], basey=10)
axe.axvline(x=0, color='black')
axe.axvline(x=.7, color='red')
axe.legend(('Static Resistance', 'Dynamic Resistance',), loc=(.1,.5))
axe.set_xlabel('Voltage [V]')
axe.set_ylabel('Resistance [Ohm]')

pylab.tight_layout()

pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
