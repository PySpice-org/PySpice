####################################################################################################

#r#
#r# =============
#r#  Transformer
#r# =============
#r#
#r# This examples shows how to simulate a transformer.
#r#

####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

from Transformer import Transformer

#f# literal_include('Transformer.py')

####################################################################################################

circuit = Circuit('Transformer')

ac_line = circuit.AcLine('input', 'input', circuit.gnd, rms_voltage=230@u_V, frequency=50@u_Hz)
circuit.subcircuit(Transformer(turn_ratio=10))
circuit.X('transformer', 'Transformer', 'input', circuit.gnd, 'output', circuit.gnd)
circuit.R('load', 'output', circuit.gnd, 1@u_kΩ)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=ac_line.period/200, end_time=ac_line.period*3)

figure = plt.figure(1, (20, 10))
plot(analysis.input)
plot(analysis.output)
plt.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'transformer.png')
