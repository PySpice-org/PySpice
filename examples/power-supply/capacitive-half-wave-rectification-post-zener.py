#!# This example shows a capacitive power supply with a post zener half-rectification, a kind
#!# of transformless power supply.

#!# To go further on this topic, you can read these design notes:
#!#
#!# * Transformerless Power Supply Design, Designer Circuits, LLC
#!# * Low-cost power supply for home appliances, STM, AN1476
#!# * Transformerless Power Supplies: Resistive and Capacitive, Microchip, AN954

####################################################################################################

import os

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

#cm# capacitive-half-wave-rectification-post-zener-circuit.m4

circuit = Circuit('Capacitive Half-Wave Rectification (Post Zener)')

circuit.include(spice_library['1N4148'])
# 1N5919B: 5.6 V, 3.0 W Zener Diode Voltage Regulator
circuit.include(spice_library['d1n5919brl'])

ac_line = circuit.AcLine('input', circuit.gnd, 'L', rms_voltage=u_V(230), frequency=u_Hz(50))
circuit.R('in', 'L', 1, u_Ω(470))
circuit.C('in', 1, 2, u_nF(470))
circuit.X('Dz', 'd1n5919brl', circuit.gnd, 2)
circuit.X('D', '1N4148', 2, 'out')
circuit.C('', circuit.gnd, 'out', u_uF(220))
circuit.R('load', circuit.gnd, 'out', u_kΩ(1))

# # Fixme: circuit.nodes[2].v, circuit.branch.current
# print circuit.nodes

# Simulator(circuit, ...).transient(...)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=ac_line.period/200, end_time=ac_line.period*10)

figure = plt.figure(1, (20, 10))
axe = plt.subplot(111)

plot(analysis['L'] / 100, axis=axe)
plot(analysis.out, axis=axe)
###plot((analysis.out - analysis['L']) / 100, axis=axe)
###plot(analysis.out - analysis['2'], axis=axe)
###plot((analysis['2'] - analysis['1']) / 100, axis=axe)
# or:
#   plt.plot(analysis.out.abscissa, analysis.out)
plt.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
#fig# save_figure(figure, 'capacitive-half-wave-rectification-post-zener.png')
