from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import *
from PySpice.Spice.Netlist import Circuit

class OpAmp(SubCircuitFactory):
    NAME = 'opamp'
    NODES = ('non_inverting_input', 'inverting_input', 'output')
    
    def __init__(self):
        super().__init__()
        self.VoltageControlledCurrentSource('input', self.gnd, 'n1', 'non_inverting_input', 'inverting_input', transconductance=100)
        self.Resistor('1', 'n1', self.gnd, resistance=1323@u_kOhm)
        self.Capacitor('1', 'n1', self.gnd, capacitance=30@u_pF)
        self.VoltageControlledVoltageSource('out', 'output', self.gnd, 'n1', self.gnd, voltage_gain=1)


# Create a new circuit
circuit = Circuit('Low Pass Filter')

# Add the opamp to the circuit
circuit.subcircuit(OpAmp())

# Define the input voltage

# Define the input voltage
circuit.SinusoidalVoltageSource('1', circuit.gnd, 'n2', amplitude = 5@u_V, frequency = 200@u_Hz)
circuit.SinusoidalVoltageSource('2', 'n2', 'n3', amplitude = 1@u_V, frequency = 5@u_Hz)

# Connect the opamp
circuit.X('opamp', 'opamp', 'non_inverting_input', 'inverting_input', 'nout')

# Define the resistors and capacitors for the low pass filter
circuit.R(1, 'n3', 'inverting_input', 10@u_kΩ)
circuit.R(2, 'inverting_input', 'nout', 1000@u_kΩ)
circuit.C(1, 'inverting_input', 'nout', 0.0159@u_uF)

# Ground non-inverting input
circuit.R(3, 'non_inverting_input', circuit.gnd, 1@u_pOhm)

# Connect the output
circuit.R('load', 'nout', circuit.gnd, 1@u_MΩ)

simulator = circuit.simulator(temperature=25, nominal_temperature=25, reltol=1e-12)
analysis = simulator.transient(step_time=0.1@u_ms, end_time=2@u_s)

import matplotlib.pyplot as plt

plt.figure(figsize=(20, 10))
plt.plot(u_ms(analysis.time), analysis['n3'], label='Input Voltage [V]')
plt.plot(u_ms(analysis.time), analysis['nout'], label='Output Voltage [V]')
plt.legend()
plt.plot()
