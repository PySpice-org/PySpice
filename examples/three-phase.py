####################################################################################################
#
# Three-phase electric power: Y and Delta configurations
#
####################################################################################################

####################################################################################################

import math

import numpy as np
from matplotlib import pylab

####################################################################################################

frequency = 50
w = 2*math.pi*frequency
period = 1. / frequency

rms_mono = 230
rms_tri = math.sqrt(3) * rms_mono
amplitude_mono = rms_mono * math.sqrt(2)
amplitude_tri = rms_tri * math.sqrt(2)

t = np.linspace(0, 3*period, 1000)

# Y configuration
Ph1 = amplitude_mono * np.sin(t*w) # Ph1 - N
Ph2 = amplitude_mono * np.sin(t*w + 2*math.pi/3) # Ph2 - N
Ph3 = amplitude_mono * np.sin(t*w + 4*math.pi/3) # Ph3 - N

# Delta configuration
Ph12 = amplitude_tri * np.sin(t*w + math.pi/6) # Ph1 - Ph2
Ph23 = amplitude_tri * np.sin(t*w + 3*math.pi/2) # Ph2 - Ph3
Ph31 = amplitude_tri * np.sin(t*w + 5*math.pi/6) # Ph3 - Ph1

pylab.plot(t, Ph1, t, Ph2, t, Ph3,
           # t, Ph12, t, Ph23, t, Ph31,
           t, Ph1-Ph2, t, Ph2-Ph3, t, Ph3-Ph1,
          )
pylab.grid()
pylab.title('Three-phase electric power: Y and Delta configurations (230V Mono/400V Tri 50Hz Europe)')
pylab.legend(('Ph1-N', 'Ph2-N', 'Ph3-N',
              'Ph1-Ph2', 'Ph2-Ph3', 'Ph3-Ph1'),
             loc=(.7,.5))
pylab.xlabel('t [s]')
pylab.ylabel('[V]')
pylab.axhline(y=rms_mono, color='blue')
pylab.axhline(y=-rms_mono, color='blue')
pylab.axhline(y=rms_tri, color='blue')
pylab.axhline(y=-rms_tri, color='blue')
pylab.show()

####################################################################################################
# 
# End
# 
####################################################################################################
