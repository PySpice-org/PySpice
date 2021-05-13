# https://github.com/xesscorp/skidl/blob/master/examples/spice-sim-intro/spice-sim-intro.ipynb

####################################################################################################

from skidl import *
# Load the SKiDL + PySpice packages and initialize them for doing circuit simulations.
from skidl.pyspice import *
print(lib_search_paths)

# lib_search_paths[SPICE].append('SpiceLib')

####################################################################################################

# reset()   # This will clear any previously defined circuitry.

####################################################################################################

# Create soem nodes
Vin = Net('vin')
print(Vin.name)
Vout = Net('vout')

AcLine = SINEV(ref='input', amplitude=230@u_V, frequency=1@u_kHz)
print(AcLine)
print(AcLine.ref)
print(AcLine[1].name, AcLine[2].aliases)

Remi = R(ref='emi', value=165@u_kΩ)
Rin = R(ref='in', value=94@u_Ω)
R2 = R(ref='2', value=1@u_kΩ)
Rload = R(ref='load', value=1@u_kΩ)

Cin = C(ref='in', value=330@u_uF)
print(Cin.ref)   # Fixme: why Cin_1 ???
C1 = C(ref='1', value=250@u_uF)
print(C1.ref)
C2 = C(ref='2', value=250@u_uF)
print(C2.ref)   # Fixme: why C2_1 ???

print('Diode')   # Fixme: slow...
D1 = Part('1N4148', '1N4148')
D2 = Part('1N4148', '1N4148')
print(D1)
print(D1.ref)
Dz = Part('1N5919B', 'd1n5919brl')
print(Dz)

print('Create connections')
# gnd += AcLine['n'], R2[2], Dz[1], C1[2], Rload[2]
# Vin += AcLine['p'], Cin[2], Remi[2]
# Vout += D1[2], C2[1], Dz[2], C1[1], Rload[1]

# Rin[2] += Cin[1], Remi[1]
# Rin[1] += D1[1], D2[2]
# C2[2] += D2[1], R2[1]

par_ntwk = gnd & AcLine & Vin
print('par_ntwk', par_ntwk)
Vin & (Cin | Remi) & Rin & D1[1,2] & Vout
# Fixme: Dz inverted pin ???
gnd & ((R2 & C2) | Dz[2,1] | C1 | Rload) & Vout
D2[1,2] += C2[1], D1[1]

# ERC()

print('Generate circuit')
circuit = generate_netlist()
print(type(circuit))
print(circuit)

# Get the node of
print(node(C1[1]))
