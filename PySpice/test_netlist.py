from PySpice.Netlist import SubCircuit, Circuit
from PySpice.Units import *

subcircuit_1N4148 = SubCircuit('1N4148', 1, 2)
subcircuit_1N4148.R('1', 1, 2, 5.827E+9)
subcircuit_1N4148.D('1', 1, 2, '1N4148')
subcircuit_1N4148.model('1N4148', 'D',
                        IS=4.352E-9, N=1.906, BV=110, IBV=0.0001, RS=0.6458, CJO=7.048E-13,
                        VJ=0.869, M=0.03, FC=0.5, TT=3.48E-9)
# print str(subcircuit_1N4148)

frequence = 50
perdiod = 1. / frequence
step_time = perdiod/200
end_time = perdiod*10

line_peak_voltage = 10

circuit = Circuit('Simple Rectifier', global_nodes=(0, 'out'))
circuit.subcircuit(subcircuit_1N4148)
circuit.V('input', 'in', circuit.gnd, 'DC 0V', 'SIN(0V {}V {}Hz)'.format(line_peak_voltage, frequence))
circuit.X('D', '1N4148', 'in', 'out')
circuit.C('load', 'out', circuit.gnd, micro(100))
circuit.R('load', 'out', circuit.gnd, kilo(1), ac='1k')

print circuit.nodes
print circuit.Cload
# print circuit.1N4148
print subcircuit_1N4148['1N4148']
print circuit.out

simulation = circuit.simulation(temperature=25, nominal_temperature=25, pipe=True)
simulation.options(filetype='binary')
simulation.save('V(in)', 'V(out)')
simulation.tran(step_time, end_time)

print str(simulation)
# python PySpice/test_netlist.py | ngspice -s > data

####################################################################################################
# 
# End
# 
####################################################################################################
