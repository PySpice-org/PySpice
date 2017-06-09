#!# This example shows the simulation of a capacitor and an inductor.
#!#
#!# To go further, you can read these pages on Wikipedia: `RC circuit <https://en.wikipedia.org/wiki/RC_circuit>`_
#!# and `RL circuit <https://en.wikipedia.org/wiki/RL_circuit>`_.

####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

from scipy.optimize import curve_fit

####################################################################################################

# Warning: the capacitor/inductor return current in the generator
#  could use switches instead

#!# We will use a simple circuit where both capacitor and inductor are driven by a pulse source
#!# through a limiting current resistor.

#cm# capacitor_and_inductor.m4

# Fixme: for loop makes difficult to intermix code and text !

#!# We will fit from the simulation output the time constant of each circuit and compare it to the
#!# theoretical value.

figure = plt.figure(1, (20, 10))

element_types = ('capacitor', 'inductor')

for element_type in ('capacitor', 'inductor'):

    circuit = Circuit(element_type.title())
    # Fixme: compute value
    source = circuit.Pulse('input', 'in', circuit.gnd,
                           initial_value=0, pulsed_value=10,
                           pulse_width=milli(10), period=milli(20))
    circuit.R(1, 'in', 'out', kilo(1))
    if element_type == 'capacitor':
        element = circuit.C
        value = micro(1) # F
        # tau = RC = 1 ms
    else:
        element = circuit.L
        # Fixme: force component value to an Unit instance ?
        value = 1 # H
        # tau = L/R = 1 ms
    element(1, 'out', circuit.gnd, value)
    # circuit.R(2, 'out', circuit.gnd, kilo(1)) # for debug

    if element_type == 'capacitor':
        tau = float(circuit['R1'].resistance * circuit['C1'].capacitance )
    else:
        tau = circuit['L1'].inductance / float(circuit['R1'].resistance)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    step_time = micro(10)
    analysis = simulator.transient(step_time=step_time, end_time=source.period*3)

    # Let define the theoretical output voltage.
    if element_type == 'capacitor':
        def out_voltage(t, tau):
            return source.pulsed_value * (1 -  np.exp(-t / tau))
    else:
        def out_voltage(t, tau):
            return source.pulsed_value * np.exp(-t / tau)
    # Fixme: get step_time from analysis
    # At t = 5 tau, each circuit has nearly reached it steady state.
    i_max = int(5 * tau / float(step_time))
    popt, pcov = curve_fit(out_voltage, analysis.out.abscissa[:i_max], analysis.out[:i_max])
    tau_measured = popt[0]

    # Fixme: use Unit().canonise()
    print('tau {0} = {1:.1f} ms'.format(element_type, tau * 1000))
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
    plot((analysis['in'] - analysis.out)/float(circuit['R1'].resistance)*current_scale)
    axe.axvline(x=tau, color='red')
    axe.set_ylim(-11, 11)
    axe.set_xlabel('t [s]')
    axe.set_ylabel('[V]')
    axe.legend(('Vin [V]', 'Vout [V]', 'I'), loc=(.8,.8))
#o#

plt.tight_layout()
plt.show()

#fig# save_figure(figure, 'capacitor-inductor.png')

# Fixme: Add formulae
