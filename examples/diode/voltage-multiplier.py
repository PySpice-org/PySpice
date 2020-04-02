#r# This example depicts a voltage multiplier using diodes and capacitors.  To go further, you can
#r# read this `page <http://en.wikipedia.org/wiki/Voltage_multiplier>`_ on Wikipedia.

####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#f# circuit_macros('voltage-multiplier-circuit.m4')

circuit = Circuit('Voltage Multiplier')
circuit.include(spice_library['1N4148'])
source = circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd, amplitude=10@u_V, frequency=50@u_Hz)

multiplier = 5
for i in range(multiplier):
    if i:
        top_node = i - 1
    else:
        top_node = 'in'
    midlle_node, bottom_node = i + 1, i
    circuit.C(i, top_node, midlle_node, 1@u_mF)
    circuit.X(i, '1N4148', midlle_node, bottom_node)
circuit.R(1, multiplier, multiplier+1, 1@u_MΩ)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=source.period/200, end_time=source.period*20)

####################################################################################################

figure = plt.figure(1, (20, 10))

axe = plt.subplot(111)
axe.set_title('Voltage Multiplier')
axe.set_xlabel('Time [s]')
axe.set_ylabel('Voltage [V]')
axe.grid()
# Fixme: axis vs axe ...
plot(analysis['in'], axis=axe)
for i in range(1, multiplier+1):
    y = analysis[str(i)]
    if i & 1: # for odd multiplier the ground is permuted
        y -= analysis['in']
    plot(y, axis=axe)
# axe.axhline(-multiplier*source.amplitude)
axe.set_ylim(float(-multiplier*1.1*source.amplitude), float(1.1*source.amplitude))
axe.legend(['input'] + ['*' + str(i) for i in range(1, multiplier+1)] ,
           loc=(.2,.8))

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'voltage-multiplier.png')
