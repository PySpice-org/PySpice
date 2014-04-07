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
from .Tools.StringTools import join_lines, join_list, join_dict

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

class Pulse(VoltageSource):

    """
    
    PULSE ( V1 V2 TD TR TF PW PER )
    
    A single pulse so specified is described by the following table:
    
    || Time        || Value ||
    || 0           || V1    ||
    || TD          || V1    ||
    || TD+TR       || V2    ||
    || TD+TR+PW    || V2    ||
    || TD+TR+PW+TF || V1    ||
    || TSTOP       || V1    ||
    
    default value for rise and fall time in the transient step, period is stop time.

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 initial_value, pulsed_value,
                 pulse_width, period,
                 delay_time=0, rise_time=0, fall_time=0):
                 # delay_time=.0,
                 # rise_time=None, fall_time=None, pulse_width=None, period=None):

        super(Pulse, self).__init__(name, node_plus, node_minus)

        self.initial_value = initial_value
        self.pulsed_value = pulsed_value
        self.delay_time = delay_time
        self.rise_time = rise_time
        self.fall_time = fall_time
        self.pulse_width = pulse_width
        self.period = period

        # # Fixme: to func?
        # # Check parameters
        # found_none = False
        # for parameter in ('rise_time', 'fall_time', 'pulse_width', 'period'):
        #     parameter_value = getattr(self, parameter)
        #     if found_none:
        #         if parameter_value is not None:
        #             raise ValueError("Parameter {} is set but some previous parameters was not set".format(parameter))
        #     else:
        #         found_none = parameter_value is None

    ##############################################

    @property
    def frequency(self):
        return 1./self.period

    ##############################################

    @property
    def parameters(self):

        # Fixme: to func?
        return ('PULSE(' + \
                join_list((self.initial_value, self.pulsed_value, self.delay_time, 
                           self.rise_time, self.fall_time, self.pulse_width, self.period)) + \
                ')',)

####################################################################################################
# 
# End
# 
####################################################################################################
