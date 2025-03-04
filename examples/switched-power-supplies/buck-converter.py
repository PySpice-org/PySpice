####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator, plot
from PySpice.Unit import *

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#?# circuit_macros('buck-converter.m4')

circuit = Circuit('Buck Converter')
circuit.include(spice_library['genopa1'])
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
inductor = circuit.L(1, 'source', 1, L)
# add a series resistor to model the ESR of the inductor. It helps convergence
inductor.pins[0].add_esr(circuit, value = 10@u_mOhm)
inductor.pins[0].add_current_probe(circuit, name = 'inductor_current')

circuit.R('L', 1, 'out', RL)
circuit.C(1, 'out', circuit.gnd, Cout) # , initial_condition=0@u_V
circuit.R('load', 'out', circuit.gnd, Rload)

simulator = Simulator.factory()
simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)

# I noticed that sometimes tmax is not calculated correctly. it's better to specify it manually using max_time
# for convergence issues, it's better to use a smaller timestep
# Also, sometimes you may use UIC to assist covnergence. 
analysis = simulation.transient(step_time=period/300, end_time=period*150, start_time=0@u_ms, max_time=1@u_ns, use_initial_condition=True)

figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

ax1.plot(analysis.out)
ax1.plot(analysis['source'])
# ax.plot(analysis['source'] - analysis['out'])
# ax.plot(analysis['gate'])
ax1.axhline(y=float(Vout), color='red')
ax1.legend(('Vout [V]', 'Vsource [V]'), loc=(.8,.8))
ax1.grid()
ax1.set_xlabel('t [s]')
ax1.set_ylabel('[V]')


ax2.plot(analysis.branches['vinductor_current'], label='L2 [A]')
ax2.legend(('Inductor current [A]',), loc=(.8,.8))
ax2.grid()
ax2.set_xlabel('t [s]')
ax2.set_ylabel('[A]')
plt.tight_layout()
plt.show()

#f# save_figure('figure', 'buck-converter.png')
