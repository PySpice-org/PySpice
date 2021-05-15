#r# =======
#r#  Skidl
#r# =======

# Fixme: elem[a, b, c]

#r# This example explores Skidl...

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from pprint import pprint

####################################################################################################

from PySpice import Circuit, SubCircuitFactory
from PySpice.Unit import *

circuit = Circuit('Test')

# Capacitor > DipoleElement

print("Actual API")
C1 = circuit.C(1, 1, circuit.gnd, 2@u_uF)
print(C1.plus)
# Pin plus of C1 on node 3
print(type(C1.plus))
# <class 'PySpice.Spice.Netlist.Pin'>
print(type(C1.plus.node))
# <class 'PySpice.Spice.Netlist.Node'>
print(C1.pins)
# [Pin plus of C1 on node 3, Pin minus of C1 on node 4]
print(C1.nodes)
# [Node 3, Node 4]

print()
print("Try dangling...")
# PySpice is happy with that...
C2 = circuit.C(2, None, None, 2@u_uF)
# But in fact, it creates a node 'None'
print(C2.minus)
print(C2.minus.dangling)
# Pin minus of C2 on node None
# dangling impl: now it fails
# print(circuit)
# C2 None None 2uF

print()
print("Connect pins...")
# pin.node is getter only
# it works...
C2.plus.connect(circuit.node(1))
print(type(circuit.gnd), circuit.gnd)
C2.minus.connect(circuit.gnd)
print(C2.minus)
print(circuit)

# Element don't implement []
# C2['foo']
# TypeError: 'Capacitor' object is not subscriptable

print()
print("...")

# C > DipoleElement
print(circuit.C.ELEMENT_CLASS)
pprint(circuit.C.ELEMENT_CLASS.__mro__)
# pprint(circuit.C.ELEMENT_CLASS.__dict__)
print(circuit.C.ELEMENT_CLASS.PINS)
print('C3...')
C3 = circuit.C(3, *[None]*len(circuit.C.ELEMENT_CLASS.PINS), 2@u_uF)
# C3 = circuit.C(3, None, None, 2@u_uF)

print('Connect pin to node...')
print(C3.PINS)
print(C3.PIN_NAMES)
# C3.minus.connect(circuit.gnd)
C3.minus += circuit.gnd
print(C3.minus)
node = circuit.get_node(2, create=True)
C3.plus += node
print(circuit)

in_ = circuit.get_node('in', create=True)
out = circuit.get_node('out', create=True)
R1 = circuit.R(1, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R2 = circuit.R(2, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R3 = circuit.R(3, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)

# node <= pin
in_ += R1.minus
# node <= pins
out += R1.plus, R2.plus
# circuit.gnd += R2.minus   # want a setter... !
gnd = circuit.gnd
gnd += R2.minus
# dangling <= pin
R3.plus += R2.plus
R3.minus += gnd
print(circuit)

R11 = circuit.R(11, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R12 = circuit.R(12, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R13 = circuit.R(13, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)

# Create new nodes
R11.plus += R12.plus
R11.minus += circuit.gnd
# pin <= dangling
R11.minus += R13.plus
# merge node
R11.plus += R2.plus

R21 = circuit.R(21, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R22 = circuit.R(22, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)
R23 = circuit.R(23, *[None]*len(circuit.R.ELEMENT_CLASS.PINS), 100@u_Ω)

gnd & ( R21 | R22 ) & R23 & out

####################################################################################################

# PySpice don't have "default circuit"
# Need a way to create dangling element

####################################################################################################
#
# Skidl API
#

# The += operator is the only way to make connections!

# Net-to-Net: Connecting one net to another merges the pins on both nets into a single, larger net.
# Pin-to-Net: A pin is connected to a net, adding it to the list of pins connected to that net. If
#             the pin is already attached to other nets, then those nets are merged with this net.
# Net-to-Pin: This is the same as doing a pin-to-net connection.
# Pin-to-Pin: A net is created and both pins are attached to it. If one or both pins are already
#             connected to other nets, then those nets are merged with the newly-created.

#   node1 += node2
#   el[1] += node
#   node += el1[1], el2[1], ...
#   el[1] += el[2]

# One-to-One:   This is the most frequent type of connection, for example, connecting one pin to
#               another or connecting a pin to a net.
# One-to-Many:  This mainly occurs when multiple pins are connected to the same net, like when
#               multiple ground pins of a chip are connected to the circuit ground net.
# Many-to-Many: This usually involves bus connections to a part, such as connecting a bus to the
#               data or address pins of a processor. For this variant, there must be the same number
#               of things to connect in each set, e.g. you can’t connect three pins to four nets.

# += el[1, 2, 3]
# el[1, 2, 3] +=

# Making Serial, Parallel, and Tee Networks

# https://xess.com/skidl/docs/_site/blog/sweetening-skidl

# ser_ntwk = vcc & r1 & r2 & r3 & r4 & gnd
# par_ntwk = vcc & (r1 | r2 | r3 | r4) & gnd
# combo_ntwk = vcc & ((r1 & r2) | (r3 & r4)) & gnd

# polar_ntwk = vcc & r1 & d1['A,K'] & gnd

# ntwk_ce = vcc & r1 & q1['C,E'] & gnd
# ntwk_b = r2 & q1['B']

# ntwk_ce = vcc & r1 & outp & q1['C,E'] & gnd
# ntwk_b = inp & r2 & q1['B']

# pi_ntwk = inp & tee(cs & gnd) & l & tee(cl & gnd) & outp

# The tee function takes any network as its argument and returns the first node of that network to
# be connected into the higher-level network. The network passed to tee can be arbitrarily complex,
# including any combination of parts, &’s, |’s, and tee’s.
