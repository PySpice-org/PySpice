#!# ============
#!#  RLC Filter
#!# ============

#!# This example illustrates RLC Filters.

####################################################################################################

import numpy as np
import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Plot.BodeDiagram import bode_diagram
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *

####################################################################################################

#!# We define four low-pass RLC filters with the following factor of quality: .5, 2, 2 and 4.

#cm# low-pass-rlc-filter.m4

circuit1 = Circuit('Four double-pole Low-Pass RLC Filter')

circuit1.Sinusoidal('input', 'in', circuit1.gnd, amplitude=1)
# pulse 0 5 10 ms
# Q = .5
circuit1.R(1, 'in', 2, 200)
circuit1.L(1, 2, 3, milli(10))
circuit1.C(1, 3, circuit1.gnd, micro(1)) # vout = 3
# Q = 1
circuit1.R(2, 'in', 4, 100)
circuit1.L(2, 4, 5, milli(10))
circuit1.C(2, 5, circuit1.gnd, micro(1))
# Q = 2
circuit1.R(3, 'in', 6, 50)
circuit1.L(3, 6, 7, milli(10))
circuit1.C(3, 7, circuit1.gnd, micro(1))
# Q = 4
R4 = circuit1.R(4, 'in', 8, 25)
L4 = circuit1.L(4, 8, 9, milli(10))
C4 = circuit1.C(4, 9, circuit1.gnd, micro(1))

simulator1 = circuit1.simulator(temperature=25, nominal_temperature=25)
analysis1 = simulator1.ac(start_frequency=100, stop_frequency=kilo(10), number_of_points=100,  variation='dec')

#!# The resonant frequency is given by
#!#
#!# .. math::
#!#
#!#     f_0 = 2 \pi \omega_0 = \frac{1}{2 \pi \sqrt{L C}}
#!#
#!# and the factor of quality by
#!#
#!# .. math::
#!#
#!#     Q = \frac{1}{R} \sqrt{\frac{L}{C}} = \frac{1}{RC \omega_0}
#!#

resonant_frequency = 1 / (2 * math.pi * math.sqrt(L4.inductance * C4.capacitance))
quality_factor = 1 / R4.resistance * math.sqrt(L4.inductance / C4.capacitance)
print("Resonant frequency = {:.1f} Hz".format(resonant_frequency))
print("Factor of quality = {:.1f}".format(quality_factor))
#o#

#!# We plot the Bode diagram of the Q = 4 filter.

figure1 = plt.figure(1, (20, 10))
plt.title("Bode Diagram of a Low-Pass RLC Filter")
axes1 = (plt.subplot(211), plt.subplot(212))
bode_diagram(axes=axes1,
             frequency=analysis1.frequency,
             gain=20*np.log10(np.absolute(analysis1['4'])),
             phase=np.angle(analysis1['4'], deg=False),
             marker='.',
             color='blue',
             linestyle='-',
            )
for axe in axes1:
    axe.axvline(x=resonant_frequency, color='red')

plt.tight_layout()
plt.show()

#fig# save_figure(figure1, 'low-pass-rlc-filter-bode-diagram.png')

####################################################################################################

#!# We define a pass-band RLC filter with a quality's factor of 4.

#cm# pass-band-rlc-filter.m4

circuit2 = Circuit('Pass-Band RLC Filter')

circuit2.Sinusoidal('input', 'in', circuit2.gnd, amplitude=1)
L1 = circuit2.L(1, 'in', 2, milli(10))
C1 = circuit2.C(1, 2, 'out', micro(1))
R1 = circuit2.R(1, 'out', circuit2.gnd, 25)

resonant_frequency = 1 / (2 * math.pi * math.sqrt(L1.inductance * C1.capacitance))
quality_factor = 1 / R4.resistance * math.sqrt(L1.inductance / C1.capacitance)
print("Resonant frequency = {:.1f} Hz".format(resonant_frequency))
print("Factor of quality = {:.1f}".format(quality_factor))
#o#

simulator2 = circuit2.simulator(temperature=25, nominal_temperature=25)
analysis2 = simulator2.ac(start_frequency=100, stop_frequency=kilo(10), number_of_points=100,  variation='dec')

figure2 = plt.figure(2, (20, 10))
plt.title("Bode Diagram of a Pass-Band RLC Filter")
axes2 = (plt.subplot(211), plt.subplot(212))
bode_diagram(axes=axes2,
             frequency=analysis2.frequency,
             gain=20*np.log10(np.absolute(analysis2.out)),
             phase=np.angle(analysis2.out, deg=False),
             marker='.',
             color='blue',
             linestyle='-',
            )
for axe in axes2:
    axe.axvline(x=resonant_frequency, color='red')

plt.tight_layout()
plt.show()

#fig# save_figure(figure2, 'pass-band-rlc-filter-bode-diagram.png')
