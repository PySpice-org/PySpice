#!# =====================================
#!#  Relay drived by a bipolar transistor
#!# =====================================

#!# This example shows the simulation of ...

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

# #cm# relay.m4

period = 50@u_ms
pulse_width = period / 2

circuit = Circuit('Relay')

# circuit.V('digital', 'Vdigital', circuit.gnd, 5@u_V)
circuit.Pulse('clock', 'clock', circuit.gnd, 0@u_V, 5@u_V, pulse_width, period, rise_time=5@u_ms, fall_time=5@u_ms)
circuit.R('base', 'clock', 'base', 100@u_Ω)
circuit.BJT(1, 'collector', 'base', circuit.gnd, 'bjt') # Q is mapped to BJT !
circuit.model('bjt', 'npn', bf=80, cjc=pico(5), rb=100)
circuit.V('analog', 'VccAnalog', circuit.gnd, 8@u_V)
circuit.R('relay', 'VccAnalog', 1, 50@u_Ω)
circuit.L('relay', 1, 'collector', 100@u_mH)
circuit.include(spice_library['1N5822']) # Schottky diode
diode = circuit.X('D', '1N5822', 'collector', 'VccAnalog')
# Fixme: subcircuit node
# diode.minus.add_current_probe(circuit)

####################################################################################################

figure = plt.figure(1, (20, 10))

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=period/1000, end_time=period*1.1)

axe = plt.subplot(111)
plt.title('')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.grid()
plot(analysis.base, axis=axe)
plot(analysis.collector, axis=axe)
# Fixme: current probe
# plot((analysis['1'] - analysis.collector)/circuit.Rrelay.resistance, axis=axe)
plot(analysis['1'] - analysis.collector, axis=axe)
plt.legend(('Vbase', 'Vcollector'), loc=(.05,.1))

plt.tight_layout()
plt.show()

#fig# save_figure(figure, 'relay.png')
