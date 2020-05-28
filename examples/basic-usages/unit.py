#r# This example shows how to use units

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Spice.Netlist import Circuit

####################################################################################################

from PySpice.Unit import *

foo = kilo(1) # unit less

resistance_unit = U_Ω

resistance1 = u_kΩ(1)
resistance1 = u_kOhm(1) # ASCII variant

resistance1 = 1@u_kΩ   # using Python 3.5 syntax
resistance1 = 1 @u_kΩ  # space doesn't matter
resistance1 = 1 @ u_kΩ #

resistance2 = as_Ω(resistance1) # check unit

resistances = u_kΩ(range(1, 11)) # same as [u_kΩ(x) for x in range(1, 11)]
resistances = range(1, 11)@u_kΩ  # using Python 3.5 syntax

capacitance = u_uF(200)
inductance = u_mH(1)
temperature = u_Degree(25)

voltage = resistance1 * u_mA(1) # compute unit

frequency = u_ms(20).frequency
period = u_Hz(50).period
pulsation = frequency.pulsation
pulsation = period.pulsation

#r# According to the Python `operator precedence
#r# <https://docs.python.org/3/reference/expressions.html#operator-precedence>`_, division operators
#r# have a higher priority than the matrix multiplication operator.  In consequence you must had
#r# parenthesis to perform something like :code:`(10@u_s) / (2@_us)`.

####################################################################################################

circuit = Circuit('Resistor Bridge')

resistance = 10@u_kΩ
print(float(resistance))
print(str(resistance))

circuit.V('input', 1, circuit.gnd, 10@u_V)
circuit.R(1, 1, 2, 2@u_kΩ)
circuit.R(2, 1, 3, 1@u_kΩ)
circuit.R(3, 2, circuit.gnd, 1@u_kΩ)
circuit.R(4, 3, circuit.gnd, 2@u_kΩ)
circuit.R(5, 3, 2, 2@u_kΩ)

print(circuit)

####################################################################################################

import pint
u = pint.UnitRegistry()

resistance = 10*u.kΩ
# print(float(resistance))
print(resistance.magnitude)
print(resistance.m)
print(resistance.units)
print(str(resistance))

circuit = Circuit('Resistor Bridge')

circuit.V('input', 1, circuit.gnd, 10*u.V)
circuit.R(1, 1, 2, 2*u.kΩ)
circuit.R(2, 1, 3, 1*u.kΩ)
circuit.R(3, 2, circuit.gnd, 1*u.kΩ)
circuit.R(4, 3, circuit.gnd, 2*u.kΩ)
circuit.R(5, 3, 2, 2*u.kΩ)

print(circuit)
