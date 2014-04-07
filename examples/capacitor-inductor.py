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

circuits = {}
for element_type in 'capacitor', 'inductor':

    circuit = Circuit(element_type.title())
    # Fixme: compute value
    circuit.Pulse('input', 'in', circuit.gnd,
                  initial_value=0, pulsed_value=10,
                  pulse_width=milli(10), period=milli(20))
    circuit.R(1, 'in', 'out', kilo(1))
    if element_type == 'capacitor':
        element = circuit.C
        value = micro(1) # F
    else:
        element = circuit.L
        value = 1 # H
    element(1, 'out', circuit.gnd, value)
    # circuit.R(2, 'out', circuit.gnd, kilo(1)) # for debug

    simulation = circuit.simulation(temperature=25, nominal_temperature=25)
    simulation.save('V(in)', 'V(out)')
    simulation.transient(step_time=micro(1),
                         end_time=milli(60))

    print str(simulation)

    raw_file = spice_server(simulation)

    figure = pylab.figure()
    axe = pylab.subplot(111)
    axe.grid()

    data = raw_file.data
    current_scale = 1000
    axe.plot(data['time'], data['v(in)'],
             data['time'], data['v(out)'],
             # Fixme: resistor current, scale
             data['time'], current_scale*(data['v(in)']-data['v(out)'])/1000)
    axe.set_ylim(-11, 11)
    axe.set_title(element_type.title())
    axe.set_xlabel('t [s]')
    axe.set_ylabel('[V]')
    axe.legend(('Vin [V]', 'Vout [V]', 'I'), loc=(.8,.8))
    figure.show()

    circuits[element_type] = {'circuit':circuit, 'data':data, 'figure':figure}

pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
