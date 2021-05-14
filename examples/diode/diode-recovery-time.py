#r# This example illustrates the diode recovery time and the capacitive behaviour of a PN junction.

# Fixme: Split the plots ? Add some explanations at the end

####################################################################################################

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator, plot
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#r# Let define some parameters

dc_offset = 1@u_V
ac_amplitude = 100@u_mV

####################################################################################################

#r# We will first compute some quiescent points and the corresponding dynamic resistance.

#f# circuit_macros('diode-characteristic-curve-circuit.m4')

#r# Since this circuit is equivalent to a voltage divider, we can write the following relation :
#r#
#r# .. math::
#r#
#r#     V_{out} = \frac{Z_d}{R_1 + Z_d} V_{in}
#r#
#r# where :math:`Z_d` is the diode impedance.

circuit = Circuit('Diode')
circuit.include(spice_library['BAV21'])
# Fixme: Xyce: Device model BAV21: Illegal parameter(s) given for level 1 diode: IKF
source = circuit.V('input', 'in', circuit.gnd, dc_offset)
circuit.R(1, 'in', 'out', 1@u_kΩ)
circuit.D('1', 'out', circuit.gnd, model='BAV21')

simulator = Simulator.factory()

quiescent_points = []
for voltage in (dc_offset - ac_amplitude, dc_offset, dc_offset + ac_amplitude):
    source.dc_value = voltage
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
    analysis = simulation.operating_point()
    # Fixme: handle unit
    quiescent_voltage = float(analysis.out)
    quiescent_current = - float(analysis.Vinput)
    quiescent_points.append(dict(voltage=voltage,
                                 quiescent_voltage=quiescent_voltage,
                                 quiescent_current=quiescent_current))
    print("Quiescent Point {:.1f} mV {:.1f} mA".format(quiescent_voltage*1e3, quiescent_current*1e3))
#o#

dynamic_resistance = ((quiescent_points[ 0]['quiescent_voltage'] -
                       quiescent_points[-1]['quiescent_voltage'])
                      /
                      (quiescent_points[ 0]['quiescent_current'] -
                       quiescent_points[-1]['quiescent_current']))

#?# print("Dynamic Resistance = {:.1f} Ω".format(dynamic_resistance))
#?# #o#

#r# We found a dynamic resistance of @<@dynamic_resistance:.1f@>@ Ω.

####################################################################################################

#r#
#r# We will now drive the diode with a sinusoidal source and perform an AC analysis.

#f# circuit_macros('diode-characteristic-curve-circuit-ac.m4')

circuit = Circuit('Diode')
circuit.include(spice_library['BAV21'])
circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd,
                   dc_offset=dc_offset, offset=dc_offset,
                   amplitude=ac_amplitude)
R = circuit.R(1, 'in', 'out', 1@u_kΩ)
circuit.D('1', 'out', circuit.gnd, model='BAV21')

simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
analysis = simulation.ac(start_frequency=10@u_kHz, stop_frequency=1@u_GHz, number_of_points=10,  variation='dec')

#r# Let plot the voltage across the diode and the dynamic resistance as a function of the frequency.

figure, (ax1, ax2, ax3)  = plt.subplots(ncols=3, figsize=(20, 10))

# Fixme: handle unit in plot (scale and legend)
ax1.semilogx(analysis.frequency, np.absolute(analysis.out)*1e3)
ax1.grid(True)
ax1.grid(True, which='minor')
ax1.set_xlabel("Frequency [Hz]")
ax1.set_ylabel("Vd [mV]")

current = (analysis['in'] - analysis.out) / float(R.resistance)
ax2.semilogx(analysis.frequency, np.absolute(analysis.out/current))
ax2.grid(True)
ax2.grid(True, which='minor')
ax2.set_xlabel("Frequency [Hz]")
ax2.set_ylabel('Rd [Ω]')

####################################################################################################

#r# We will now drive the diode with a pulse generator and perform a transient analysis.

#f# circuit_macros('diode-characteristic-curve-circuit-pulse.m4')

frequency = 1@u_MHz

circuit = Circuit('Diode')
circuit.include(spice_library['BAV21'])
# source = circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd,
#                             dc_offset=dc_offset, offset=dc_offset,
#                             amplitude=ac_amplitude,
#                             frequency=frequency)
source = circuit.PulseVoltageSource('input', 'in', circuit.gnd,
                       initial_value=dc_offset-ac_amplitude, pulsed_value=dc_offset+ac_amplitude,
                       pulse_width=frequency.period/2, period=frequency.period)
circuit.R(1, 'in', 'out', 1@u_kΩ)
circuit.D('1', 'out', circuit.gnd, model='BAV21')

simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
analysis = simulation.transient(step_time=source.period/1e3, end_time=source.period*4)

# Fixme: axis, x scale
# plot(analysis['in'] - dc_offset + quiescent_points[0]['quiescent_voltage'])
# plot(analysis.out)
ax3.plot(analysis.out.abscissa*1e6, analysis.out)
ax3.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
ax3.grid()
ax3.set_xlabel('t [μs]')
ax3.set_ylabel('[V]')
# ax3.set_ylim(.5, 1 + ac_amplitude + .1)

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'diode-recovery-time.png')

#r# We notice the output of the circuit cannot follow the pulse generator.  It is due to the
#r# capacitive behaviour of a PN junction that cut off the highest frequencies of the pulse.  The
#r# plot of the dynamic resistance as a function of the frequency show a typical low pass filter
#r# behaviour where the impedance drop at high frequencies.
