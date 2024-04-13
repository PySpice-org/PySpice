from PySpice.Unit import *
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


circuit = Circuit("Full Bridge Rectifier")
circuit.model('DIODE1', 'D')
circuit.SinusoidalVoltageSource('in', 'n1', 'n3', amplitude = 230@u_V, frequency = 50@u_Hz)
circuit.D('1', 'n1', 'n2', model="DIODE1")
circuit.D('2', 'n3', 'n2', model="DIODE1")
circuit.D('3', 'n4', 'n3', model="DIODE1")
circuit.D('4', 'n4', 'n1', model="DIODE1")
circuit.R('load', 'n2', 'n4', 10@u_kOhm)
circuit.C('s', 'n2', 'n4', 10@u_F) #Smoothing capacitor
circuit.R('virtual', 'n4', circuit.gnd, 0@u_Ohm) #This is just a reference point for SPICE

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=1@u_ms, end_time=0.2@u_s)

Vout = analysis['n2'] - analysis['n4']
Vin = analysis['n1'] - analysis['n3']

import matplotlib.pyplot as plt
plt.figure()
plt.plot(analysis.time, Vin, label='Input Voltage [V]')
plt.plot(analysis.time, Vout, label='Output Voltage [V]')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.grid()
plt.show()
