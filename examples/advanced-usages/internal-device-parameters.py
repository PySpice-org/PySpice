#r# ============================
#r#  Internal Device Parameters
#r# ============================

#r# This example show how to access internal device parameters.

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

####################################################################################################

class Level2(SubCircuitFactory):
    __name__ = 'level2'
    __nodes__ = ('d4', 'g4', 'v4')
    def __init__(self):
        super().__init__()
        self.M(1, 'd4', 'g4', 'v4', 'v4', model='nmos', w=1e-5, l=3.5e-7)

class Level1(SubCircuitFactory):
    __name__ = 'level1'
    __nodes__ = ('d3', 'g3', 'v3')
    def __init__(self):
        super().__init__()
        self.X('mos2', 'level2', 'd3', 'g3', 'v3')
        self.subcircuit(Level2())

circuit = Circuit('Transistor output characteristics')
circuit.V('dd', 'd1', circuit.gnd, 2)
circuit.V('ss', 'vsss', circuit.gnd, 0)
circuit.V('sig', 'g1', 'vsss', 0)
circuit.X('mos1', 'level1', 'd1', 'g1', 'vsss')

if True:
    circuit.subcircuit(Level1())
else:
    subcircuit_level2 = SubCircuit('level2', 'd4', 'g4', 'v4')
    subcircuit_level2.M(1, 'd4', 'g4', 'v4', 'v4', model='nmos', w=1e-5, l=3.5e-7)

    subcircuit_level1 = SubCircuit('level1', 'd3', 'g3', 'v3')
    subcircuit_level1.X('mos2', 'level2', 'd3', 'g3', 'v3')
    subcircuit_level1.subcircuit(subcircuit_level2)

    circuit.subcircuit(subcircuit_level1)

print(str(circuit))

####################################################################################################

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.dc(Vdd=slice(0, 5, .1)) # Fixme: ,Vsig=slice(1, 5, 1)

####################################################################################################

#?# vdd d1 0 2.0
#?# vss vsss 0 0
#?# vsig g1 vsss 0
#?# xmos1 d1 g1 vsss level1
#?# .subckt level1 d3 g3 v3
#?# xmos2 d3 g3 v3 level2
#?# .ends
#?# .subckt level2 d4 g4 v4
#?# m1 d4 g4 v4 v4 nmos w=1e-5 l=3.5e -007
#?# .ends
#?# .dc vdd 0 5 0.1 vsig 0 5 1
#?# .control
#?# save all @m.xmos1.xmos2.m1[vdsat]
#?# run
#?# plot vss#branch $ current measured at the top level
#?# plot @m.xmos1.xmos2.m1[vdsat]
#?# .endc
#?# .MODEL NMOS NMOS LEVEL=8
#?# +VERSION=3.2.4 TNOM=27 TOX=7.4E-9
#?# .end
