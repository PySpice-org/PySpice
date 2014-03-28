####################################################################################################

import logging
import math

from matplotlib import pylab

####################################################################################################

logging.basicConfig(level=logging.DEBUG)

####################################################################################################

from PySpice.Netlist import Circuit
from PySpice.Pipe import SpiceServer
from PySpice.SpiceLibrary import SpiceLibrary
from PySpice.Units import *

####################################################################################################

spice_library = SpiceLibrary('~/electronic-design-pattern/spice/libraries')
spice_server = SpiceServer()

####################################################################################################

# Fixme: Sin class
frequence = 50
perdiod = 1. / frequence
step_time = perdiod/200
end_time = perdiod*10
line_rms_voltage = 230
line_peak_voltage = line_rms_voltage * math.sqrt(2)

circuit = Circuit('STM AN1476: Low-Cost Power Supply For Home Appliances')

circuit.include(spice_library['1N4148'])
# 1N5919B: 5.6 V, 3.0 W Zener Diode Voltage Regulator
circuit.include(spice_library['d1n5919brl'])

circuit.V('input', 'out', 'in', 'DC 0V', 'SIN(0V {}V {}Hz)'.format(line_peak_voltage, frequence))
circuit.R('load', 'out', circuit.gnd, kilo(1))
circuit.C('load', 'out', circuit.gnd, micro(220))
circuit.X('D1', '1N4148', circuit.gnd, 1)
circuit.X('Dz1', 'd1n5919brl', 1, 'out')
circuit.C('ac', 1, 2, nano(470))
circuit.R('ac', 2, 'in', 470)

simulation = circuit.simulation(temperature=25, nominal_temperature=25, pipe=True)
# Fixme: circuit.nodes[2].v, circuit.branch.current
print circuit.nodes
simulation.save('V(in)', 'V(out)', 'V(1)', 'V(2)')
simulation.tran(step_time, end_time)

print str(simulation)

raw_file = spice_server(simulation)
for field in raw_file.variables:
    print field

data = raw_file.data
pylab.plot(data['time'], data['v(in)']/100,
           data['time'], data['v(out)'],
           data['time'], (data['v(out)'] - data['v(in)'])/10,
           data['time'], data['v(out)'] - data['v(1)'],
           data['time'], (data['v(1)'] - data['v(2)'])/10,
       )
pylab.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
pylab.grid()
pylab.xlabel('t [s]')
pylab.ylabel('[V]')
pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
