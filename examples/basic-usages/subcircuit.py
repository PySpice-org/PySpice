#r# =======================
#r#  How to Use SubCircuit
#r# =======================

#r# This example shows how to use subcircuits.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

#r# There is two ways to define subcircuit with PySpice, either using
#r# :class:`PySpice.Spice.Netlist.SubCircuit` or a simpler alternative
#r# :class:`PySpice.Spice.Netlist.SubCircuitFactory`.

#r#
#r# Let define a parallel resistor subcircuit using the :class:`PySpice.Spice.Netlist.SubCircuitFactory`

class ParallelResistor(SubCircuitFactory):
    __name__ = 'parallel_resistor'
    __nodes__ = ('n1', 'n2')
    def __init__(self, R1=1@u_Ω, R2=2@u_Ω):
        super().__init__()
        self.R(1, 'n1', 'n2', R1)
        self.R(2, 'n1', 'n2', R2)

#r# Let define a circuit

circuit = Circuit('Test')

#r# then we can use this subcircuit like this

circuit.subcircuit(ParallelResistor(R2=3@u_Ω))
circuit.X('1', 'parallel_resistor', 1, circuit.gnd)

print(circuit)
#o#

#r# If the above way is not suited for your purpose we can use this second approach

class ParallelResistor2(SubCircuit):
    __nodes__ = ('n1', 'n2')
    def __init__(self, name, R1=1@u_Ω, R2=2@u_Ω):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.R(1, 'n1', 'n2', R1)
        self.R(2, 'n1', 'n2', R2)

circuit = Circuit('Test')
circuit.subcircuit(ParallelResistor2('pr1', R2=2@u_Ω))
circuit.X('1', 'pr1', 1, circuit.gnd)
circuit.subcircuit(ParallelResistor2('pr2', R2=3@u_Ω))
circuit.X('2', 'pr2', 1, circuit.gnd)

print(circuit)
#o#
