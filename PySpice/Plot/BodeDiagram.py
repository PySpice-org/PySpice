####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""This module provides helpers to plot Bode diagrams using Matplolib.

Frequency is in Hz, gain in dB, phase in radians between -π and π.
"""

####################################################################################################

import math

from matplotlib import pyplot

####################################################################################################

def bode_diagram_gain(axe, frequency, gain, **kwargs):

    axe.semilogx(frequency, gain, basex=10, **kwargs)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Gain [dB]")

####################################################################################################

def bode_diagram_phase(axe, frequency, phase, **kwargs):

    axe.semilogx(frequency, phase, basex=10, **kwargs)
    axe.set_ylim(-math.pi, math.pi)
    axe.grid(True)
    axe.grid(True, which='minor')
    axe.set_xlabel("Frequency [Hz]")
    axe.set_ylabel("Phase [rads]")
    # axe.set_yticks # Fixme:
    pyplot.yticks((-math.pi, -math.pi/2,0, math.pi/2, math.pi),
                  (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))

####################################################################################################

def bode_diagram(axes, frequency, gain, phase, **kwargs):
    bode_diagram_gain(axes[0], frequency, gain, **kwargs)
    bode_diagram_phase(axes[1], frequency, phase, **kwargs)
