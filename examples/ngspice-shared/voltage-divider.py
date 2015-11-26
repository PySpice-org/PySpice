####################################################################################################

import math

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
from PySpice.Unit.Units import *

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

# source = circuit.Sinusoidal('input', 'input', circuit.gnd, amplitude=10, frequency=50)
circuit.V('input', 'input', circuit.gnd, 'dc 0 external')
circuit.R(1, 'input', 'output', kilo(10))
circuit.R(2, 'output', circuit.gnd, kilo(1))

# simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# analysis = simulator.transient(step_time=source.period/200, end_time=source.period*2)

####################################################################################################

circuit_str = str(circuit)
circuit_str += '''
.options TEMP = 25
.options TNOM = 25
.tran 0.0001 0.04
.end
'''

ngspice_shared = MyNgSpiceShared(amplitude=10, frequency=Frequency(50), send_data=False)
ngspice_shared.load_circuit(circuit_str)
ngspice_shared.run()

print('Generated plots:', ngspice_shared.plot_names)
# plot_names = ['tran1', 'const']
tran_plot = ngspice_shared.plot('tran1')
print('Plot name:', tran_plot.plot_name)
for vector in tran_plot.values():
    print('Vector:', vector.name, '[{}]'.format(vector.unit))
analysis = tran_plot.to_analysis()

####################################################################################################

figure1 = plt.figure(1, (20, 10))
plt.title('Voltage Divider')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.grid()
plot(analysis.input)
plot(analysis.output)
plt.legend(('input', 'output'), loc=(.05,.1))
# plt.ylim(-source.amplitude*1.1, source.amplitude*1.1)

plt.tight_layout()
plt.show()
#fig# save_figure(figure1, 'voltage-divider.png')

####################################################################################################
#
# End
#
####################################################################################################
