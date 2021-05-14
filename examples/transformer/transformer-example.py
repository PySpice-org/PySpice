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

from PySpice import Circuit, Simulator, plot
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

simulator = Simulator.factory()
simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
analysis = simulation.transient(step_time=ac_line.period/200, end_time=ac_line.period*3)

figure, ax = plt.subplots(figsize=(20, 10))
ax.plot(analysis.input)
ax.plot(analysis.output)
ax.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
ax.grid()
ax.set_xlabel('t [s]')
ax.set_ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'transformer.png')
