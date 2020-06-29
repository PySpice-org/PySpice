#r# =======================
#r#  Netlist Manipulations
#r# =======================

#r# This example shows how to manipulate netlist.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

class SubCircuit1(SubCircuitFactory):
    __name__ = 'sub_circuit1'
    __nodes__ = ('n1', 'n2')
    def __init__(self):
        super().__init__()
        self.R(1, 'n1', 'n2', 1@u_Ω)
        self.R(2, 'n1', 'n2', 2@u_Ω)

#r# Let define a circuit.

circuit = Circuit('Test')

#r# When we add an element to a circuit, we can get a reference to it or ignore it:

C1 = circuit.C(1, 0, 1, 1@u_uF)

circuit.C(2, 1, 2, 2@u_uF)
circuit.subcircuit(SubCircuit1())
circuit.X('1', 'sub_circuit1', 2, 0)

#r# We can get back an element of a circuit using its name, either as a class attribute or using the
#r# dictionary interface:

C1 = circuit.C1
C1 = circuit['C1']

#r# and modify it

C1.capacitance = 10@u_F

#r# To get the SPICE netlist of a citcuit, we just have to convert it to a string:

print(circuit) # str(circuit) is implicit here

#r# same apply to an element

print(C1)

#r# We can disable an element in the circuit

C1.enabled = False
print(circuit)

#r# We can clone a circuit to another one

circuit2 = circuit.clone(title='A clone') # title is optional
print(circuit2)

#r# We can remove an element

C2 = circuit2.C2.detach()
print(circuit2)
