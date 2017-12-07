#!/usr/bin/env python
#!# ======================
#!#  AC Coupled Amplifier
#!# ======================

#!# This example shows the simulation of an AC coupled amplifier using a NPN bipolar transistor.

####################################################################################################

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

spice_library = SpiceLibrary(SpiceLibrary.env_or_relative_to(__file__))

####################################################################################################

#cm# ac-coupled-amplifier.m4

circuit = Circuit('Transistor')

circuit.V('power', 5, circuit.gnd, 15@u_V)
source = circuit.Sinusoidal('in', 'in', circuit.gnd, amplitude=.5@u_V, frequency=1@u_kHz)
circuit.C(1, 'in', 2, 10@u_uF)
circuit.R(1, 5, 2, 100@u_kΩ)
circuit.R(2, 2, 0, 20@u_kΩ)
circuit.R('C', 5, 4, 10@u_kΩ)
circuit.BJT(1, 4, 2, 3, 'bjt') # Q is mapped to BJT !
circuit.model('bjt', 'npn', bf=80, cjc=pico(5), rb=100)
circuit.R('E', 3, 0, 2@u_kΩ)
circuit.C(2, 4, 'out', 10@u_uF)
circuit.R('Load', 'out', 0, 1@u_MΩ)

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
