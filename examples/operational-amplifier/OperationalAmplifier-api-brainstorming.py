#skip#

####################################################################################################

from PySpice.Spice.Netlist import SubCircuit
from PySpice.Unit import *

####################################################################################################

class BasicOperationalAmplifier(SubCircuit): # SubCircuitFactory

    #
    # __init__(self, name, subcircuit_name, *nodes)
    #
    # name = class name
    # node = __nodes__ = interface
    #

    __nodes__ = ('non_inverting_input', 'inverting_input', 'output')

    ##############################################

    def __init__(self):

        # comment: we could pass parameters using ctor

        # Input impedance
        # comment: 'R'+'2' but for other devices ? name/attribute versus spice name
        self.R('input', 'non_inverting_input', 'inverting_input', 10@u_MΩ)

        # dc gain=100k and pole1=100hz
        # unity gain = dcgain x pole1 = 10MHZ
        # Fixme: gain=...
        self.VCVS('gain', 'non_inverting_input', 'inverting_input', 1, self.gnd, kilo(100))
        self.R('P1', 1, 2, 1@u_kΩ)
        self.C('P1', 2, self.gnd, 1.5915@u_uF)

        # Output buffer and resistance
        self.VCVS('buffer', 2, self.gnd, 3, self.gnd, 1)
        self.R('out', 3, 'output', 10@u_Ω)

####################################################################################################

class BasicOperationalAmplifier(SubCircuit): # SubCircuitFactory

    __nodes__ = ('non_inverting_input', 'inverting_input', 'output')

    # Comment: R doesn't know its name, R prefix is redundant
    Rinput = R('non_inverting_input', 'inverting_input', 10@u_MΩ)

    gain = VCVS('non_inverting_input', 'inverting_input', 1, self.gnd, kilo(100))
    RP1 = R(1, 2, 1@u_kΩ)
    CP1 = C(2, self.gnd, 1.591@u_uF)

    # Comment: buffer is a Python name
    buffer = VCVS(2, self.gnd, 3, self.gnd, 1)
    Rout = R(3, 'output', 10@u_Ω)
