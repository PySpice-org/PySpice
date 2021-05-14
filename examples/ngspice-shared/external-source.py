####################################################################################################

#r#
#r# ===================================
#r#  Simulation using External Sources
#r# ===================================
#r#
#r# This example explains how to plug a voltage source from Python to NgSpice.
#r#

####################################################################################################

# Fixme: Travis CI macOS
#
# Error on line 2 :
#   vinput input 0 dc 0 external
#   parameter value out of range or the wrong type
#
# Traceback (most recent call last):
#     analysis = simulation.transient(step_time=period/200, end_time=period*2)
#   File "/usr/local/lib/python3.7/site-packages/PySpice/Spice/NgSpice/Shared.py", line 1145, in load_circuit
#     raise NgSpiceCircuitError('')

####################################################################################################

import math

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice import Circuit, Simulator, plot
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
from PySpice.Unit import *

####################################################################################################

class MyNgSpiceShared(NgSpiceShared):

    ##############################################

    def __init__(self, amplitude, frequency, **kwargs):

        super().__init__(**kwargs)

        self._amplitude = amplitude
        self._pulsation = float(frequency.pulsation)

    ##############################################

    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        voltage[0] = self._amplitude * math.sin(self._pulsation * time)
        return 0

    ##############################################

    def get_isrc_data(self, current, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        current[0] = 1.
        return 0

####################################################################################################

circuit = Circuit('Voltage Divider')

circuit.V('input', 'input', circuit.gnd, 'dc 0 external')
circuit.R(1, 'input', 'output', 10@u_kΩ)
circuit.R(2, 'output', circuit.gnd, 1@u_kΩ)

amplitude = 10@u_V
frequency = 50@u_Hz
ngspice_shared = MyNgSpiceShared(amplitude=amplitude, frequency=frequency, send_data=False)
simulator = Simulator.factory(simulator='ngspice-shared', ngspice_shared=ngspice_shared)
simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)

period = float(frequency.period)
analysis = simulation.transient(step_time=period/200, end_time=period*2)

####################################################################################################

figure1, ax = plt.subplots(figsize=(20, 10))
ax.set_title('Voltage Divider')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Voltage [V]')
ax.grid()
ax.plot(analysis.input)
ax.plot(analysis.output)
ax.legend(('input', 'output'), loc=(.05,.1))
ax.set_ylim(float(-amplitude*1.1), float(amplitude*1.1))

plt.tight_layout()
plt.show()

#f# save_figure('figure1', 'voltage-divider.png')
