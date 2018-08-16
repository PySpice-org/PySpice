#r# This example shows the simulation of a capacitor and an inductor.
#r#
#r# To go further, you can read these pages on Wikipedia: `RC circuit <https://en.wikipedia.org/wiki/RC_circuit>`_
#r# and `RL circuit <https://en.wikipedia.org/wiki/RL_circuit>`_.

####################################################################################################

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

from scipy.optimize import curve_fit

####################################################################################################

# Warning: the capacitor/inductor return current in the generator
#  could use switches instead

#r# We will use a simple circuit where both capacitor and inductor are driven by a pulse source
#r# through a limiting current resistor.

#f# circuit_macros('capacitor_and_inductor.m4')

# Fixme: for loop makes difficult to intermix code and text !

#r# We will fit from the simulation output the time constant of each circuit and compare it to the
#r# theoretical value.

figure = plt.figure(1, (20, 10))

element_types = ('capacitor', 'inductor')

for element_type in ('capacitor', 'inductor'):

    circuit = Circuit(element_type.title())
    # Fixme: compute value
    source = circuit.PulseVoltageSource('input', 'in', circuit.gnd,
                           initial_value=0@u_V, pulsed_value=10@u_V,
                           pulse_width=10@u_ms, period=20@u_ms)
    circuit.R(1, 'in', 'out', 1@u_kΩ)
    if element_type == 'capacitor':
        element = circuit.C
        value = 1@u_uF
        # tau = RC = 1 ms
    else:
        element = circuit.L
        # Fixme: force component value to an Unit instance ?
        value = 1@u_H
        # tau = L/R = 1 ms
    element(1, 'out', circuit.gnd, value)
    # circuit.R(2, 'out', circuit.gnd, kilo(1)) # for debug

    if element_type == 'capacitor':
        tau = circuit['R1'].resistance * circuit['C1'].capacitance
    else:
        tau = circuit['L1'].inductance / circuit['R1'].resistance

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    step_time = 10@u_us
    analysis = simulator.transient(step_time=step_time, end_time=source.period*3)

    # Let define the theoretical output voltage.
    if element_type == 'capacitor':
        def out_voltage(t, tau):
            # Fixme: TypeError: only length-1 arrays can be converted to Python scalars
            return float(source.pulsed_value) * (1 -  np.exp(-t / tau))
    else:
        def out_voltage(t, tau):
            return float(source.pulsed_value) * np.exp(-t / tau)
    # Fixme: get step_time from analysis
    # At t = 5 tau, each circuit has nearly reached it steady state.
    i_max = int(5 * tau / float(step_time))
    popt, pcov = curve_fit(out_voltage, analysis.out.abscissa[:i_max], analysis.out[:i_max])
    tau_measured = popt[0]

    # Fixme: use Unit().canonise()
    print('tau {0} = {1}'.format(element_type, tau.canonise().str_space()))
    print('tau measured {0} = {1:.1f} ms'.format(element_type, tau_measured * 1000))

    if element_type == 'capacitor':
        axe = plt.subplot(121)
        title = "Capacitor: voltage is constant"
    else:
        axe = plt.subplot(122)
        title = "Inductor: current is constant"
    axe.set_title(title)
    axe.grid()
    current_scale = 1000
    plot(analysis['in'])
    plot(analysis['out'])
    # Fixme: resistor current, scale
    plot(((analysis['in'] - analysis.out)/circuit['R1'].resistance) * current_scale)
    axe.axvline(x=float(tau), color='red')
    axe.set_ylim(-11, 11)
    axe.set_xlabel('t [s]')
    axe.set_ylabel('[V]')
    axe.legend(('Vin [V]', 'Vout [V]', 'I'), loc=(.8,.8))
#o#

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'capacitor-inductor.png')

# Fixme: Add formulae
