#r# =====================
#r#  Skywater 130 n-MOSFET Transistor
#r# =====================

#r# This example shows how to simulate the characteristic curves of an nmos transistor for skywater130 Technology.

####################################################################################################
import os
import argparse
import pdb
import numpy as np
import matplotlib.pyplot as plt
from pint import UnitRegistry
import re
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example python3.8 ./examples/transistor/nmos-transistor_sky130.py"
                                                 " --fet_types sky130_fd_pr__nfet_01v8  sky130_fd_pr__pfet_01v8")
    parser.add_argument("--fet_types", required=True, help="Provide the FET Name list",nargs='+', default=[])
    parser.add_argument("--libpath", required=False, help="path to library",
                        default="/usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice")
    parser.add_argument("--corner", required=False, help="Corner to run the sims on", default='tt')
    args = parser.parse_args()


####################################################################################################

libraries_path = find_libraries()
library_sky130 = os.path.abspath(args.libpath)
####################################################################################################

#Unit Registry
u = UnitRegistry()

#?# TODO: Extend to search for all possible allowable W and L ranges

circuit = Circuit('NMOS Transistor')
# Define the DC supply voltage value
Vdd = 1.2
circuit.lib(args.libpath, args.corner)
# Instantiate circuit elements and transistor
Vgate = circuit.V('gate', 'gatenode', circuit.gnd, 0@u_V)
Vdrain = circuit.V('drain', 'vdrain', circuit.gnd, u_V(Vdd))
Vvdd = circuit.V('vdd', 'vdd', circuit.gnd, u_V(Vdd))

gate_range = np.arange(0, Vdd+0.1, .1)
drain_range = np.arange(0.3, Vdd+0.1, .1)

for num, fet in enumerate(args.fet_types):
    if re.search("nfet", fet):
        circuit.X(num, fet, 'vdrain', 'gatenode', circuit.gnd, circuit.gnd, W=4.8, L=0.15, nf=1)
    elif re.search("pfet", fet):
        circuit.X(num, fet, 'vdrain', 'gatenode', 'vdd', 'vdd', W=4.8, L=0.15, nf=1)

    # Raw Spice Equivalent
    #circuit.raw_spice = """
    #.title NMOS Transistor
    #.lib /usr/bin/miniconda3/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
    #Vgate gatenode 0 0V
    #Vdrain vdrain 0 1.2V
    #Vvdd vdd 0 1.2V
    #X0 vdrain gatenode 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=4.8 nf=1
    #X1 vdrain gatenode vdd vdd sky130_fd_pr__pfet_01v8 L=0.15 W=4.8 nf=1
    #"""

#   Simulation and Plotting
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    # simulator = circuit_raw_spice.simulator(temperature=25, nominal_temperature=25)
    # Passing Slices to the voltages are non-intuitive, need to dig deeper, cant pass ndarrays # TODO Can we pass lists ?
    if re.search("nfet", fet):
        analysis = simulator.dc(Vgate=slice(0, Vdd, 0.1), Vdrain=slice(0.3, Vdd, 0.1))
    elif re.search("pfet", fet):
        analysis = simulator.dc(Vgate=slice(Vdd, 0, -0.1), Vdrain=slice(Vdd-0.3, 0.0, -0.1))
    figure, ax = plt.subplots(figsize=(20, 10))
    # Plotting by slicing the sweep elements on Vsrc2 or Vdrain, Need a better way to access both dimensions
    # Ideally the simulation object saves the object in different indexed arrays for vsrc2
    for num, loopvar in enumerate(range(0, len(drain_range))):
        if re.search("nfet", fet):
            plt.plot(analysis['gatenode'][num*len(gate_range):(num*len(gate_range) + len(gate_range))],
                    u_mA(-analysis._branches['vdrain'])[num*len(gate_range):(num*len(gate_range) + len(gate_range))],
                     label=f'vds={drain_range[loopvar]:.2f}')
        elif re.search("pfet", fet):
            plt.plot(analysis['gatenode'][num*len(gate_range):(num*len(gate_range) + len(gate_range))],
                    u_mA(analysis._branches['vdrain'])[num*len(gate_range):(num*len(gate_range) + len(gate_range))],
                     label=f'vds={drain_range[loopvar]:.2f}')
    ax.set_xlabel('Vgs [V]')
    ax.set_ylabel('Id [mA]')
    plt.title(label=f'{fet} id vgs for vds')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{fet}_igvgs.png')
    #plt.show()