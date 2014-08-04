####################################################################################################

import math

from matplotlib import pyplot

####################################################################################################
 
# frequency in Hz, gain in dB, phase in radians between -pi and pi.

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

####################################################################################################
# 
# End
# 
####################################################################################################
