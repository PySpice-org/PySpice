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

circuit = Circuit('Xspice Control Limit Test')

#add a sinwave source
circuit.SinusoidalVoltageSource('input', 'in', circuit.gnd, amplitude=10@u_V, frequency=100@u_kHz)
circuit.V('dd', 'vdd', circuit.gnd, 5@u_V)
circuit.V('ss', 'vss', circuit.gnd, -5@u_V)
# a6 in vdd vss out varlimit
circuit.A('cl', 'in', 'vdd', 'vss', 'out', model='varlimit')
# or you can use the following for diffrential inputs. 
# circuit.A('cl', '%vd(in, gnd)', '%vd(vdd, gnd)', '%vd(vss, gnd)', '%vd(out, gnd)', model='varlimit')
# look at the xspice manual for more information about controlling the limit
circuit.model('varlimit', 'climit', in_offset=0.0, gain=1.0, upper_delta=0.0, lower_delta=0.0, limit_range=2, fraction=False)
# print(circuit)

simulator = Simulator.factory()
simulation = simulator.simulation(circuit, temperature=25, nominal_temperature=25)
# add rshunt option to avoid the matrix singularity when using xspice models. a good value is 1e12 which is 1/gmin
simulation.options(rshunt=1e12)
print(simulation)
analysis = simulation.transient(step_time=1@u_us, end_time=20@u_us, start_time=0@u_ms, max_time = 1@u_ns)
figure, ax = plt.subplots(figsize=(20, 10))
time = analysis.time
ax.plot(time * 1e6, analysis['in'], label='in')
ax.plot(time * 1e6, analysis['out'], label='out')
ax.grid()

ax.set_xlabel('t [us]')
ax.set_ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'buck-converter.png')
