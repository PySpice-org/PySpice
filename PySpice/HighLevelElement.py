####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import math

####################################################################################################

from .SpiceElement import VoltageSource

####################################################################################################

class AcLine(VoltageSource):

    ##############################################

    def __init__(self, name, node_plus, node_minus, rms_voltage=230, frequency=50):

        super(AcLine, self).__init__(name, node_plus, node_minus)

        self.rms_voltage = rms_voltage
        self.frequency = frequency

    ##############################################

    @property
    def peak_to_peak_voltage(self):
        return self.rms_voltage * math.sqrt(2)

    ##############################################

    @property
    def period(self):
        return 1./self.frequency

    ##############################################

    @property
    def parameters(self):

        return ('DC 0V', 'SIN(0V {}V {}Hz)'.format(self.peak_to_peak_voltage, self.frequency))

####################################################################################################
# 
# End
# 
####################################################################################################
