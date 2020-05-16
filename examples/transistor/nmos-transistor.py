#r# =====================
#r#  n-MOSFET Transistor
#r# =====================

#r# This example shows how to simulate the characteristic curves of an nmos transistor.

####################################################################################################

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
spice_library  = SpiceLibrary(libraries_path)

####################################################################################################

figure = plt.figure(1, (20, 10))

####################################################################################################

#r# We define a basic circuit to drive an nmos transistor using two voltage sources. 
#r# The nmos transistor demonstrated in this example is a low-level device description.

#TODO: Write the : circuit_macros('nmos_transistor.m4')

circuit = Circuit('NMOS Transistor')
circuit.include(spice_library['ptm65nm_nmos'])

# Define the DC supply voltage value
Vdd = 1.1

# Instanciate circuit elements
Vgate   = circuit.V('gate', 'gatenode'  , circuit.gnd, 0@u_V)
Vdrain  = circuit.V('drain',   'vdd'    , circuit.gnd, u_V(Vdd))
# M <name> <drain node> <gate node> <source node> <bulk/substrate node>
circuit.MOSFET(1, 'vdd', 'gatenode', circuit.gnd, circuit.gnd, model='ptm65nm_nmos')

#r# We plot the characteristics :math:`Id = f(Vgs)` using a DC sweep simulation.

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis  = simulator.dc(Vgate=slice(0, Vdd, .01))

plt.plot(analysis['gatenode'], u_mA(-analysis.Vdrain)) 
plt.legend('NMOS characteristic')
plt.grid()
plt.xlabel('Vgs [V]')
plt.ylabel('Id [mA]')

####################################################################################################

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'transistor-nmos-plot.png')
