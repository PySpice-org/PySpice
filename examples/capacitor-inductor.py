####################################################################################################

from matplotlib import pylab

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Netlist import Circuit
from PySpice.Pipe import SpiceServer
from PySpice.Units import *

####################################################################################################

spice_server = SpiceServer()

####################################################################################################

# Warning: the capacitor/inductor return current in the generator
#  could use switches instead

for element_type in 'capacitor', 'inductor':

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
        value = 1 # H
        # tau = L/R = 1 ms
    element(1, 'out', circuit.gnd, value)
    # circuit.R(2, 'out', circuit.gnd, kilo(1)) # for debug

    if element_type == 'capacitor':
        print 'tau = ', circuit['R1'].value * circuit['C1'].value 
    else:
        print 'tau = ', circuit['L1'].value  / circuit['R1'].value

    simulation = circuit.simulation(temperature=25, nominal_temperature=25)
    simulation.save('V(in)', 'V(out)')
    simulation.transient(step_time=micro(1), end_time=source.period*3)
    print str(simulation)

    raw_file = spice_server(simulation)

    figure = pylab.figure()
    axe = pylab.subplot(111)
    axe.grid()
    if element_type == 'capacitor':
        title = "Capacitor: voltage is constant"
    else:
        title = "Inductor: current is constant"
    axe.set_title(title)
    data = raw_file.data
    current_scale = 1000
    axe.plot(data['time'], data['v(in)'],
             data['time'], data['v(out)'],
             # Fixme: resistor current, scale
             data['time'], current_scale*(data['v(in)']-data['v(out)'])/1000)
    axe.set_ylim(-11, 11)
    axe.set_xlabel('t [s]')
    axe.set_ylabel('[V]')
    axe.legend(('Vin [V]', 'Vout [V]', 'I'), loc=(.8,.8))
    figure.show()

pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
