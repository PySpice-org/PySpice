####################################################################################################

from PySpice.Spice.Netlist import SubCircuit
from PySpice.Unit.Units import *

####################################################################################################

# Fixme: as class

basic_operational_amplifier = SubCircuit('BasicOperationalAmplifier',
                                         'non_inverting_input', 'inverting_input', 'output')
# Fixme: simpler ...
circuit = basic_operational_amplifier

# Input impedance
circuit.R('input', 'non_inverting_input', 'inverting_input', mega(10))

# dc gain=100k and pole1=100hz
# unity gain = dcgain x pole1 = 10MHZ
circuit.VCVS('gain', 'non_inverting_input', 'inverting_input', 1, circuit.gnd, voltage_gain=kilo(100))
circuit.R('P1', 1, 2, kilo(1))
circuit.C('P1', 2, circuit.gnd, micro(1.5915))

# Output buffer and resistance
circuit.VCVS('buffer', 2, circuit.gnd, 3, circuit.gnd, 1)
circuit.R('out', 3, 'output', 10)

# print str(basic_operational_amplifier)

####################################################################################################

# Fixme: ngspice is buggy with such subcircuit

basic_comparator = SubCircuit('BasicComparator',
                              'non_inverting_input', 'inverting_input',
                              'voltage_plus', 'voltage_minus',
                              'output')
circuit = basic_comparator

# Fixme: how to pass voltage_plus, voltage_minus ?
output_voltage_minus, output_voltage_plus = 0, 15

# to plug the voltage source
circuit.R(1, 'voltage_plus', 'voltage_minus', mega(1))
circuit.NonLinearVoltageSource(1, 'output', 'voltage_minus',
                               expression='V(non_inverting_input, inverting_input)',
                               # table=((-micro(1), output_voltage_minus),
                               #       (micro(1), output_voltage_plus))
                               table=(('-1uV', '0V'), ('1uV', '15V'))
                               )

####################################################################################################
# 
# End
# 
####################################################################################################
