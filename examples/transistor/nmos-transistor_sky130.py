#r# =====================
#r#  n-MOSFET Transistor
#r# =====================

#r# This example shows how to simulate the characteristic curves of an nmos transistor.

####################################################################################################
import os
import pdb

import matplotlib.pyplot as plt
from pint import UnitRegistry
####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
library_sky130 = os.path.abspath("/usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/")
#spice_library = SpiceLibrary(library_sky130, recurse=True)
#for i in spice_library.__dict__['_subcircuits'].keys():
#    print(i)
####################################################################################################

#Unit Registry
u = UnitRegistry()
class SkyNmosNfet1p8(SubCircuitFactory):
    NAME = 'sky130_fd_pr__nfet_01v8 NMOS'
    NODES = ('d', 'g', 's', 'b')

    def __init__(self, w=1*u.m, l=0.15*u.m, nf=1):
        super().__init__()
        self.nameid = 'nfet_01v8'
        # Figure out the allowable ranges sot that assertions can be added to error our for wrong
        self.W = w
        self.L = l
        self.nf = nf
        w_sky, l_sky = self.transform_unit(1e6)
        self.X(f'{self.nameid}_1', 'sky130_fd_pr__nfet_01v8' 'd', 'g', 's', 'b', w_sky, l_sky, self.nf)

    def transform_unit(self, mult: float):
        """Transforming the unit to the model specific unit by applying a multiplier"""
        w_trans = self.W*mult
        L_trans = self.L*mult
        return w_trans, L_trans
#r# We define a basic circuit to drive an nmos transistor using two voltage sources.
#r# The nmos transistor demonstrated in this example is a low-level device description.

#?# TODO: Write the : circuit_macros('nmos_transistor.m4')

circuit = Circuit('NMOS Transistor')
#circuit.include(spice_library['ptm65nm_nmos'])
#circuit.include(spice_library['sky130_fd_pr__nfet_01v8'])
#ngspice = NgSpiceShared.new_instance()
# Define the DC supply voltage value
Vdd = 1.1
circuit.lib("/usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice",section="tt")
# Instanciate circuit elements
Vgate = circuit.V('gate', 'gatenode', circuit.gnd, 0@u_V)
Vdrain = circuit.V('drain', 'vdd', circuit.gnd, u_V(Vdd))
circuit.X(1, 'sky130_fd_pr__nfet_01v8', 'vdd', 'gatenode', circuit.gnd, circuit.gnd, W=4.8, L=0.15, nf=1)

#print(circuit)
#exit()
#circuit.raw_spice = """
#.title NMOS Transistor
#.lib /usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
#Vgate gatenode 0 0V
#Vdrain vdd 0 1.1V
##X1 vdd gatenode 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=4.8 nf=1
#"""
print(circuit)

#r# We plot the characteristics :math:`Id = f(Vgs)` using a DC sweep simulation.
#print(circuit)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vgate=slice(0, Vdd, .1))

figure, ax = plt.subplots(figsize=(20, 10))
#print(analysis.parameters)
ax.plot(analysis['gatenode'], u_mA(-analysis.Vdrain))
ax.legend('NMOS characteristic')
ax.grid()
ax.set_xlabel('Vgs [V]')
ax.set_ylabel('Id [mA]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'transistor-nmos-plot.png')
