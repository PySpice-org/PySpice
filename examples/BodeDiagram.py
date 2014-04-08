####################################################################################################

import math

from matplotlib import pyplot

####################################################################################################
 
# frequency in Hz, gain in dB, phase in radians between -pi and pi.

def bode_diagram(frequency, gain, phase,
                 title=None,
                 **kwargs):

    figure = pyplot.figure()
 
    if title is not None:
        pyplot.title(title)

    axes = pyplot.subplot(211)
    axes.semilogx(frequency, gain, basex=10, **kwargs)
    axes.grid(True)
    axes.grid(True, which='minor')
    axes.set_ylabel("Gain [dB]")
 
    axes = pyplot.subplot(212)
    axes.semilogx(frequency, phase, basex=10, **kwargs)
    axes.set_ylim(-math.pi, math.pi)
    axes.grid(True)
    axes.grid(True, which='minor')
    axes.set_xlabel("Frequency [Hz]")
    axes.set_ylabel("Phase [rads]")
    # axes.set_yticks # Fixme:
    pyplot.yticks((-math.pi, -math.pi/2,0, math.pi/2, math.pi),
                  (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))

####################################################################################################
# 
# End
# 
####################################################################################################
