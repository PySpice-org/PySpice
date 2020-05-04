import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import BehavioralSource

circuit = Circuit('test')
circuit.LosslessTransmissionLine('line', 'output', circuit.gnd, 'input', circuit.gnd, Z0=50, TD=40e-9)

print(circuit)
