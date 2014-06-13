####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

""" This module implements high level elements built on Spice elements. """

# Fixme: these waveforms can be current sources as well

####################################################################################################

from ..Math import rms_to_amplitude, amplitude_to_rms
from ..Tools.StringTools import join_list
from ..Unit.Units import Frequency, Period
from .BasicElement import VoltageSource

####################################################################################################

class Sinusoidal(VoltageSource):

    r""" This class implements a sinusoidal waveform.

    The shape of the waveform is described by the following formula:

    .. math::

        V(t) = \begin{cases}
          V_o & \text{if}\ 0 \leq t < T_d, \\
          V_o + V_a e^{-D_f(t-T_d)} \sin\left(2\pi f (t-T_d)\right) & \text{if}\ T_d \leq t < T_{stop}.
        \end{cases}

    Spice syntax::

        SIN ( Voffset Vamplitude Freq Tdelay DampingFactor )

    Public Attributes:

      :attr:`amplitude`

      :attr:`damping_factor`

      :attr:`dc_offset`

      :attr:`delay`

      :attr:`frequency`

      :attr:`offset`

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 dc_offset=0,
                 offset=0, amplitude=1, frequency=50,
                 delay=0, damping_factor=0):

        super(Sinusoidal, self).__init__(name, node_plus, node_minus)

        self.dc_offset = dc_offset
        self.offset = offset
        self.amplitude = amplitude
        self.frequency = Frequency(frequency) # Fixme: protect by setter?
        self.delay = delay
        self.damping_factor = damping_factor

    ##############################################

    @property
    def rms_voltage(self):
        return amplitude_to_rms(self.amplitude)

    ##############################################

    @property
    def period(self):
        return self.frequency.period

    ##############################################

    def format_spice_parameters(self):

        return join_list(('DC {}V'.format(self.dc_offset),
                          'AC SIN({}V {}V {}Hz {}s {})'.format(self.offset, self.amplitude,
                                                               self.frequency, self.delay,
                                                               self.damping_factor)))
        
####################################################################################################

class AcLine(Sinusoidal):

    ##############################################

    def __init__(self, name, node_plus, node_minus, rms_voltage=230, frequency=50):

        super(AcLine, self).__init__(name, node_plus, node_minus,
                                     amplitude=rms_to_amplitude(rms_voltage),
                                     frequency=frequency)

####################################################################################################

class Pulse(VoltageSource):

    """This class implements a pulse waveform.

    Nomenclature:

    +----+---------------+
    | V1 | initial_value |
    +----+---------------+
    | V2 | pulsed_value  |
    +----+---------------+
    | Pw | pulse_width   |
    +----+---------------+
    | Td | delay_time    |
    +----+---------------+
    | Tr | rise_time     |
    +----+---------------+
    | Tf | fall_time     |
    +----+---------------+

    Spice Syntax::
    
        PULSE ( V1 V2 Td Tr Tf Pw Period )
    
    A single pulse so specified is described by the following table:
    
    +-------------+-------+
    | Time        | Value |
    +-------------+-------+
    | 0           | V1    |
    +-------------+-------+
    | Td          | V1    |
    +-------------+-------+
    | Td+Tr       | V2    |
    +-------------+-------+
    | Td+Tr+Pw    | V2    |
    +-------------+-------+
    | Td+Tr+Pw+Tf | V1    |
    +-------------+-------+
    | Tstop       | V1    |
    +-------------+-------+
    
    Note: default value in Spice for rise and fall time is the simulation transient step, pulse
    width and period is the simulation stop time.

    Public Attributes:

      :attr:`delay_time`

      :attr:`fall_time`

      :attr:`initial_value`

      :attr:`period`

      :attr:`pulse_width`

      :attr:`pulsed_value`

      :attr:`rise_time`

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 initial_value, pulsed_value,
                 pulse_width, period,
                 delay_time=0, rise_time=0, fall_time=0):
                 # delay_time=.0,
                 # rise_time=None, fall_time=None, pulse_width=None, period=None):

        # Fixme: default
        #  rise_time, fall_time = Tstep
        #  pulse_width, period = Tstop

        super(Pulse, self).__init__(name, node_plus, node_minus)

        self.initial_value = initial_value
        self.pulsed_value = pulsed_value
        self.delay_time = delay_time
        self.rise_time = rise_time
        self.fall_time = fall_time
        self.pulse_width = pulse_width
        self.period = Period(period) # Fixme: protect by setter?

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
        return self.period.frequency

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?
        return ('PULSE(' + \
                join_list((self.initial_value, self.pulsed_value, self.delay_time, 
                           self.rise_time, self.fall_time, self.pulse_width, self.period)) + \
                ')')

####################################################################################################
# 
# End
# 
####################################################################################################
