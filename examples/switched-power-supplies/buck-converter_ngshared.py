####################################################################################################

import matplotlib.pyplot as plt
import time
####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice import SpiceLibrary, Circuit, Simulator, plot
from PySpice.Unit import *

from PySpice.Spice.NgSpice.Shared import NgSpiceShared
ngspice = NgSpiceShared.new_instance()

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

####################################################################################################

end_time = 500e-6
circ_str = str(circuit)
options = f'.options TEMP = 25C \n'
options += '.options TNOM = 25C \n'
options += '.options NOINIT \n'
options += '.options RSHUNT = 1e12 \n'
# options += '.ic v(opamp_out) = 0\n'
options += f'.tran 1us {end_time} 0 1ns uic\n'
options += '.end'

circ_str += options 

ngspice.load_circuit(circ_str)
print('Loaded circuit:')
# print(ngspice.listing())

live = True
ngspice.run(background=live)
print('Plots:', ngspice.plot_names)
figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), sharex=True)
def update_plots(ax1, ax2, sim_time, analysis):
    ax1.clear()
    ax1.plot(sim_time * 1e6, analysis.out, label='Vout [V]')
    ax1.plot(sim_time * 1e6, analysis['source'], label='Vsource [V]')
    ax1.legend(loc='upper right')
    ax1.grid()
    ax1.set_ylabel('[V]')
    ax1.set_xlabel('t [us]')

    ax2.clear()
    ax2.plot(sim_time * 1e6, analysis.branches['vinductor_current'], label='L2 [A]')
    ax2.legend(loc='upper right')
    ax2.set_ylabel('[A]')
    ax2.set_xlabel('t [us]')
    ax2.grid()
    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)

if not live:
    print(ngspice.status())
    plot_data = ngspice.plot(simulation=None, plot_name=ngspice.last_plot)
    analysis = plot_data.to_analysis()
    update_plots(ax1, ax2, analysis.time, analysis)
    plt.show(block=True)
else:
    simulation_done = False
    while not simulation_done:
        time.sleep(0.1)
        ngspice.halt()
        plot_data = ngspice.plot(simulation=None, plot_name=ngspice.last_plot)
        print(ngspice.status())

        analysis = plot_data.to_analysis()
        sim_time = analysis.time
        if sim_time[-1]._value < end_time - 1e-6:
            ngspice.resume()
        else:
            simulation_done = True

        update_plots(ax1, ax2, sim_time, analysis)
        if simulation_done:
            plt.show(block=True)
            break
