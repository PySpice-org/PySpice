#!# ======================
#!#  AC Coupled Amplifier
#!# ======================

#!# This example shows the simulation of an AC coupled amplifier using a NPN bipolar transistor.

####################################################################################################

import os

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#cm# ac-coupled-amplifier.m4

circuit = Circuit('Transistor')

circuit.V('power', 5, circuit.gnd, u_V(15))
source = circuit.Sinusoidal('in', 'in', circuit.gnd, amplitude=u_V(.5), frequency=u_kHz(1))
circuit.C(1, 'in', 2, u_uF(10))
circuit.R(1, 5, 2, u_kΩ(100))
circuit.R(2, 2, 0, u_kΩ(20))
circuit.R('C', 5, 4, u_kΩ(10))
circuit.BJT(1, 4, 2, 3, 'bjt') # Q is mapped to BJT !
circuit.model('bjt', 'npn', bf=80, cjc=pico(5), rb=100)
circuit.R('E', 3, 0, u_kΩ(2))
circuit.C(2, 4, 'out', u_uF(10))
circuit.R('Load', 'out', 0, u_MΩ(1))

####################################################################################################

figure = plt.figure(1, (20, 10))

# .ac dec 5 10m 1G

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=source.period/200, end_time=source.period*2)

axe = plt.subplot(111)
plt.title('')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.grid()
plot(analysis['in'], axis=axe)
plot(analysis.out, axis=axe)
plt.legend(('input', 'output'), loc=(.05,.1))

plt.tight_layout()
plt.show()

#fig# save_figure(figure, 'ac-coupled-amplifier-plot.png')
