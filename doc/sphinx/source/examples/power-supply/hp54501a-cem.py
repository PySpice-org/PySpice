# -*- coding: utf-8 -*-

#!# ...

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
from PySpice.Unit.Units import *

####################################################################################################

libraries_path = os.path.join(os.environ['PySpice_examples_path'], 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

from HP54501A import HP54501A

####################################################################################################

circuit = Circuit('HP54501A CEM')
circuit.include(spice_library['1N4148'])
diode_model = '1N4148'
ac_line = circuit.AcLine('input', 'input', circuit.gnd, rms_voltage=230, frequency=50)
# circuit.subcircuit(HP54501A(diode_model='1N4148'))
# circuit.X('hp54501a', 'HP54501A', 'input', circuit.gnd)
circuit.C(1, 'input', circuit.gnd, micro(1))
circuit.X('D1', diode_model, 'line_plus', 'top')
circuit.X('D2', diode_model, 'scope_ground', 'input')
circuit.X('D3', diode_model, circuit.gnd, 'top')
circuit.X('D4', diode_model, 'scope_ground', circuit.gnd)
circuit.R(1, 'top', 'output', 10)
circuit.C(2, 'output', 'scope_ground', micro(50))
circuit.R(2, 'output', 'scope_ground', 900)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=ac_line.period/100, end_time=ac_line.period*3)

plot(analysis.input)
plot(analysis.Vinput)
plot(analysis.output - analysis.scope_ground)
plt.legend(('Vin [V]', 'I [A]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.show()

####################################################################################################
# 
# End
# 
####################################################################################################
