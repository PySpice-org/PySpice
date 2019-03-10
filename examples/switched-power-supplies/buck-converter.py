####################################################################################################

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
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#?# circuit_macros('buck-converter.m4')

circuit = Circuit('Buck Converter')

circuit.include(spice_library['1N5822']) # Schottky diode
circuit.include(spice_library['irf150'])

# From Microchip WebSeminars - Buck Converter Design Example

Vin = 12@u_V
Vout = 5@u_V
ratio = Vout / Vin

Iload = 2@u_A
Rload = Vout / (.8 * Iload)

frequency = 400@u_kHz
period = frequency.period
duty_cycle = ratio * period

ripple_current = .3 * Iload # typically 30 %
ripple_voltage = 50@u_mV

print('ratio =', ratio)
print('RLoad =', Rload)
print('period =', period.canonise())
print('duty_cycle =', duty_cycle.canonise())
print('ripple_current =', ripple_current)

#r# .. math:
#r#      U = L \frac{dI}{dt}

L = (Vin - Vout) * duty_cycle / ripple_current
RL = 37@u_mΩ

#r# .. math:
#r#      dV = dI (ESR + \frac{dt}{C} + \frac{ESL}{dt})

ESR = 30@u_mΩ
ESL = 0
Cout = (ripple_current * duty_cycle) / (ripple_voltage - ripple_current * ESR)

ripple_current_in = Iload / 2
ripple_voltage_in = 200@u_mV
ESR_in = 120@u_mΩ
Cin = duty_cycle / (ripple_voltage_in / ripple_current_in - ESR_in)

L = L.canonise()
Cout = Cout.canonise()
Cin = Cin.canonise()

print('L =', L)
print('Cout =', Cout)
print('Cint =', Cin)

circuit.V('in', 'in', circuit.gnd, Vin)
circuit.C('in', 'in', circuit.gnd, Cin)

# Fixme: out drop from 12V to 4V
# circuit.VCS('switch', 'gate', circuit.gnd, 'in', 'source', model='Switch', initial_state='off')
# circuit.PulseVoltageSource('pulse', 'gate', circuit.gnd, 0@u_V, Vin, duty_cycle, period)
# circuit.model('Switch', 'SW', ron=1@u_mΩ, roff=10@u_MΩ)

# Fixme: Vgate => Vout ???
circuit.X('Q', 'irf150', 'in', 'gate', 'source')
# circuit.PulseVoltageSource('pulse', 'gate', 'source', 0@u_V, Vin, duty_cycle, period)
circuit.R('gate', 'gate', 'clock', 1@u_Ω)
circuit.PulseVoltageSource('pulse', 'clock', circuit.gnd, 0@u_V, 2.*Vin, duty_cycle, period)

circuit.X('D', '1N5822', circuit.gnd, 'source')
circuit.L(1, 'source', 1, L)
circuit.R('L', 1, 'out', RL)
circuit.C(1, 'out', circuit.gnd, Cout) # , initial_condition=0@u_V
circuit.R('load', 'out', circuit.gnd, Rload)

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=period/300, end_time=period*150)

figure = plt.figure(1, (20, 10))
axe = plt.subplot(111)

plot(analysis.out, axis=axe)
plot(analysis['source'], axis=axe)
# plot(analysis['source'] - analysis['out'], axis=axe)
# plot(analysis['gate'], axis=axe)
plt.axhline(y=float(Vout), color='red')
plt.legend(('Vout [V]', 'Vsource [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'buck-converter.png')
