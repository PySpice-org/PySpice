
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


# adding current probe

circuit = Circuit('wheatstone bridge')
circuit.V('input', 'inp', circuit.gnd, 5@u_V)

circuit.R(1, 'inp', 'n1', 5@u_Ω)
circuit.R(2, 'inp', 'n2', 5@u_Ω)
circuit.R(3, 'n1', circuit.gnd, 5@u_Ω)
circuit.R(4, 'n2', circuit.gnd, 5@u_Ω)

# middle resistor
circuit.R(5, 'n1', 'n2', 5@u_Ω)

# adding current probe
circuit.R5.plus.add_current_probe(circuit)

simulator = circuit.simulator(simulator='ngspice-subprocess', temperature=25, nominal_temperature=25)
analysis = simulator.operating_point()


# current ouputs zero
print(analysis.branches)