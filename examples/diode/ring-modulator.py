#r# This example depicts a ring modulator

#r## .. warning:: It don't simulate
#r#
#r##   doAnalyses: TRAN:  Timestep too small; time = 5.5453e-08, timestep = 1.25e-18: trouble with xring_modulator.xd2:1n4148-instance d.xring_modulator.xd2.d1

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

from RingModulator import RingModulator

#f# literal_include('RingModulator.py')

####################################################################################################

circuit = Circuit('Ring Modulator')

modulator = circuit.SinusoidalVoltageSource('modulator', 'in', circuit.gnd, amplitude=1@u_V, frequency=1@u_kHz)
carrier = circuit.SinusoidalVoltageSource('carrier', 'carrier', circuit.gnd, amplitude=10@u_V, frequency=100@u_kHz)
circuit.R('in', 'in', 1, 50@u_Ω)
circuit.R('carrier', 'carrier', 2, 50@u_Ω)

circuit.include(spice_library['1N4148'])
circuit.subcircuit(RingModulator(outer_inductance=1@u_uH,
                                 inner_inductance=1@u_uH,
                                 coupling=.99,
                                 diode_model='1N4148',
                             ))
circuit.X('ring_modulator', 'RingModulator',
          1, circuit.gnd,
          2, circuit.gnd,
          'output', circuit.gnd,
         )

# outer_inductance = .01
# inner_inductance = .0025
# coupling = .9
# diode_model = '1N4148'
# input_inductor = circuit.L('input', 1, circuit.gnd, outer_inductance)
# top_inductor = circuit.L('input_top', 'input_top', 'carrier', inner_inductance)
# bottom_inductor = circuit.L('input_bottom', 'input_bottom', 'carrier', inner_inductance)
# circuit.CoupledInductor('input_top', input_inductor.name, top_inductor.name, coupling)
# circuit.CoupledInductor('input_bottom', input_inductor.name, bottom_inductor.name, coupling)
# circuit.X('D1', diode_model, 'input_top', 'output_top')
# circuit.X('D2', diode_model, 'output_top', 'input_bottom')
# circuit.X('D3', diode_model, 'input_bottom', 'output_bottom')
# circuit.X('D4', diode_model, 'output_bottom', 'input_top')
# top_inductor = circuit.L('output_top', 'output_top', circuit.gnd, inner_inductance)
# bottom_inductor = circuit.L('output_bottom', 'output_bottom', circuit.gnd, inner_inductance)
# output_inductor = circuit.L('output', 'output', circuit.gnd, outer_inductance)
# circuit.CoupledInductor('output_top', output_inductor.name, top_inductor.name, coupling)
# circuit.CoupledInductor('output_bottom', output_inductor.name, bottom_inductor.name, coupling)

circuit.R('load', 'output', circuit.gnd, 1@u_kΩ)

### simulator = circuit.simulator(temperature=25, nominal_temperature=25)
### # simulator.initial_condition(input_top=0, input_bottom=0, output_top=0, output_bottom=0)
### analysis = simulator.transient(step_time=modulator.period/1000, end_time=modulator.period)
###
### figure = plt.figure(1, (20, 10))
### plt.title('Ring Modulator')
### plt.xlabel('Time [s]')
### plt.ylabel('Voltage [V]')
### plt.grid()
### plot(analysis['Vmodulator'])
### plot(analysis['Vcarrier'])
### # plot(analysis['output'])
### plt.legend(('modulator', 'carrier', 'output'), loc=(.05,.1))

####################################################################################################

plt.show()
