import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import BehavioralSource

circuit = Circuit('test')
# circuit.LosslessTransmissionLine('line1', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50)
circuit.LosslessTransmissionLine('line1', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, TD=40e-9)
circuit.LosslessTransmissionLine('line2', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, time_delay=40@u_ns)
# circuit.LosslessTransmissionLine('line3', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, frequency=50@u_ns)
circuit.LosslessTransmissionLine('line3', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, frequency=50@u_Hz, normalized_length=10)
circuit.LosslessTransmissionLine('line4', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, F=50@u_Hz, NL=10)

print(circuit)
