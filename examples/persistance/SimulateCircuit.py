####################################################################################################

__all__ = ["simulate_circuit"]

####################################################################################################

from PySpice import SpiceLibrary, Circuit, Simulator
# from PySpice import *
from PySpice.Unit import *

from PySpice.Doc.ExampleTools import find_libraries
libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

def simulate_circuit():
    circuit = Circuit('Capacitive Half-Wave Rectification (Pre Zener)')
    circuit.include(spice_library['1N4148'])
    circuit.include(spice_library['d1n5919brl'])
    ac_line = circuit.AcLine('input', 'L', circuit.gnd, rms_voltage=230@u_V, frequency=50@u_Hz)
    circuit.C('in', 'L', 1, 330@u_nF)
    circuit.R('emi', 'L', 1, 165@u_kΩ)
    circuit.R('in', 1, 2, 2*47@u_Ω)
    circuit.X('D1', '1N4148', 2, 'out')
    circuit.C('2', 'out', 3, 250@u_uF)
    circuit.R('2', 3, circuit.gnd, 1@u_kΩ)
    circuit.X('D2', '1N4148', 3, 2)
    circuit.X('Dz', 'd1n5919brl', circuit.gnd, 'out')
    circuit.C('', 'out', circuit.gnd, 250@u_uF)
    circuit.R('load', 'out', circuit.gnd, 1@u_kΩ)

    simulator = Simulator.factory()
    simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
    analysis = simulation.transient(step_time=ac_line.period/200, end_time=ac_line.period*50)

    return analysis
