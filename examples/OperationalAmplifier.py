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
# Fixme: gain=...
circuit.VCVS('gain', 'non_inverting_input', 'inverting_input', 1, circuit.gnd, kilo(100))
circuit.R('P1', 1, 2, kilo(1))
circuit.C('P1', 2, circuit.gnd, '1.5915UF')

# Output buffer and resistance
circuit.VCVS('buffer', 2, circuit.gnd, 3, circuit.gnd, 1)
circuit.R('out', 3, 'output', 10)

# print str(basic_operational_amplifier)

####################################################################################################
# 
# End
# 
####################################################################################################
