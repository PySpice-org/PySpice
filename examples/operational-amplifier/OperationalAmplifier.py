####################################################################################################

from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

class BasicOperationalAmplifier(SubCircuitFactory):

    __name__ = 'BasicOperationalAmplifier'
    __nodes__ = ('non_inverting_input', 'inverting_input', 'output')

    ##############################################

    def __init__(self):

        super().__init__()

        # Input impedance
        self.R('input', 'non_inverting_input', 'inverting_input', 10@u_MΩ)

        # dc gain=100k and pole1=100hz
        # unity gain = dcgain x pole1 = 10MHZ
        self.VCVS('gain', 1, self.gnd, 'non_inverting_input', 'inverting_input', voltage_gain=kilo(100))
        self.R('P1', 1, 2, 1@u_kΩ)
        self.C('P1', 2, self.gnd, 1.5915@u_uF)

        # Output buffer and resistance
        self.VCVS('buffer', 3, self.gnd, 2, self.gnd, 1)
        self.R('out', 3, 'output', 10@u_Ω)

####################################################################################################

class BasicComparator(SubCircuitFactory):

    __name__ = 'BasicComparator'
    __nodes__ = ('non_inverting_input', 'inverting_input',
                 'voltage_plus', 'voltage_minus',
                 'output')

    ##############################################

    def __init__(self,):

        super().__init__()

        # Fixme: ngspice is buggy with such subcircuit

        # Fixme: how to pass voltage_plus, voltage_minus ?
        # output_voltage_minus, output_voltage_plus = 0, 15

        # to plug the voltage source
        self.R(1, 'voltage_plus', 'voltage_minus', 1@u_MΩ)
        self.NonLinearVoltageSource(1, 'output', 'voltage_minus',
                                    expression='V(non_inverting_input, inverting_input)',
                                    # table=((-micro(1), output_voltage_minus),
                                    #       (micro(1), output_voltage_plus))
                                    table=(('-1uV', '0V'), ('1uV', '15V'))
                                )
