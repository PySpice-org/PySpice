
import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Spice.Parser.HighLevelParser import SpiceSource
from PySpice.Spice.Parser.Translator import Builder
from PySpice.Unit import *

class ParallelResistor2(SubCircuit):
    __nodes__ = ('n1', 'n2')
    def __init__(self, name, R1=1@u_Ω, R2=2@u_Ω):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.R(1, 'n1', 'n2', R1)
        self.R(2, 'n1', 'n2', R2)

circuit = Circuit('Test')
circuit.R('1', 'input', 'n1', 1@u_Ω)
circuit.subcircuit(ParallelResistor2('pr1', R2=2@u_Ω))
circuit.X('1', 'pr1', 1, circuit.gnd)
circuit.subcircuit(ParallelResistor2('pr2', R2=3@u_Ω))
circuit.X('2', 'pr2', 1, circuit.gnd)

source = str(circuit)
print(circuit)

parser = SpiceSource(source=source)
circuit_builder = Builder()
bootstrap_circuit = circuit_builder.translate(spice_code=parser)
bootstrap_source = str(bootstrap_circuit)

print(bootstrap_source)

assert bootstrap_source == source
