# -*- coding: utf-8 -*-

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

""" This module implements high level elements built on top of Spice elements. """

# Fixme: these waveforms can be current sources as well

####################################################################################################

from ..Math import rms_to_amplitude, amplitude_to_rms
from ..Tools.StringTools import join_list, join_dict, str_spice
from ..Unit import as_s, as_V, as_A, as_Hz
from .BasicElement import VoltageSource

####################################################################################################

class Sinusoidal(VoltageSource):

    r""" This class implements a sinusoidal waveform.

    +------+----------------+---------------+-------+
    | Name + Parameter      + Default Value + Units |
    +------+----------------+---------------+-------+
    | Vo   + offset         +               + V, A  |
    +------+----------------+---------------+-------+
    | Va   + amplitude      +               + V, A  |
    +------+----------------+---------------+-------+
    | f    + frequency      + 1 / TStop     + Hz    |
    +------+----------------+---------------+-------+
    | Td   + delay          + 0.0           + sec   |
    +------+----------------+---------------+-------+
    | Df   + damping factor + 0.01          + 1/sec |
    +------+----------------+---------------+-------+

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

        super().__init__(name, node_plus, node_minus)

        self.dc_offset = as_V(dc_offset)
        self.offset = as_V(offset)
        self.amplitude = as_V(amplitude)
        self.frequency = as_Hz(frequency) # Fixme: protect by setter?
        self.delay = as_s(delay)
        self.damping_factor = as_Hz(damping_factor)

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

        sin_part = join_list((self.offset, self.amplitude, self.frequency, self.delay, self.damping_factor))
        return join_list((
            'DC {}'.format(str_spice(self.dc_offset)),
            'AC SIN({})'.format(sin_part),
        ))

####################################################################################################

class AcLine(Sinusoidal):

    ##############################################

    def __init__(self, name, node_plus, node_minus, rms_voltage=230, frequency=50):

        super().__init__(name, node_plus, node_minus,
                         amplitude=rms_to_amplitude(rms_voltage),
                         frequency=frequency)

####################################################################################################

class Pulse(VoltageSource):

    """This class implements a pulse waveform.

    Nomenclature:

    +--------+---------------+---------------+-------+
    | Name   + Parameter     + Default Value + Units |
    +--------+---------------+---------------+-------+
    | V1     + initial value +               + V, A  |
    +--------+---------------+---------------+-------+
    | V2     + pulsed value  +               + V, A  |
    +--------+---------------+---------------+-------+
    | Td     + delay time    + 0.0           + sec   |
    +--------+---------------+---------------+-------+
    | Tr     + rise time     + Tstep         + sec   |
    +--------+---------------+---------------+-------+
    | Tf     + fall time     + Tstep         + sec   |
    +--------+---------------+---------------+-------+
    | Pw     + pulse width   + Tstop         + sec   |
    +--------+---------------+---------------+-------+
    | Period + period        + Tstop         + sec   |
    +--------+---------------+---------------+-------+

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

        # Fixme: default
        #  rise_time, fall_time = Tstep
        #  pulse_width, period = Tstop

        super().__init__(name, node_plus, node_minus)

        self.initial_value = as_V(initial_value)
        self.pulsed_value = as_V(pulsed_value)
        self.delay_time = as_s(delay_time)
        self.rise_time = as_s(rise_time)
        self.fall_time = as_s(fall_time)
        self.pulse_width = as_s(pulse_width)
        self.period = as_s(period) # Fixme: protect by setter?

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
        return ('PULSE(' +
                join_list((self.initial_value, self.pulsed_value, self.delay_time,
                           self.rise_time, self.fall_time, self.pulse_width, self.period)) +
                ')')

####################################################################################################

class Exponential(VoltageSource):

    r"""This class implements a Exponential waveform.

    Nomenclature:

    +------+--------------------+---------------+-------+
    | Name + Parameter          + Default Value + Units |
    +------+--------------------+---------------+-------+
    | V1   + Initial value      +               + V, A  |
    +------+--------------------+---------------+-------+
    | V2   + pulsed value       +               + V, A  |
    +------+--------------------+---------------+-------+
    | Td1  + rise delay time    + 0.0           + sec   |
    +------+--------------------+---------------+-------+
    | tau1 + rise time constant + Tstep         + sec   |
    +------+--------------------+---------------+-------+
    | Td2  + fall delay time    + Td1+Tstep     + sec   |
    +------+--------------------+---------------+-------+
    | tau2 + fall time constant + Tstep         + sec   |
    +------+--------------------+---------------+-------+

    Spice Syntax::

        EXP ( V1 V2 TD1 TAU1 TD2 TAU2 )

    The shape of the waveform is described by the following formula:

    Let V21 = V2 - V1 and V12 = V1 - V2.

    .. math::

        V(t) = \begin{cases}
          V_1 & \text{if}\ 0 \leq t < T_{d1}, \\
          V_1 + V_{21} ( 1 − e^{-\frac{t-T_{d1}}{\tau_1}} )
          & \text{if}\ T_{d1} \leq t < T_{d2}, \\
          V_1 + V_{21} ( 1 − e^{-\frac{t-T_{d1}}{\tau_1}} ) + V_{12} ( 1 − e^{-\frac{t-T_{d2}}{\tau_2}} )
          & \text{if}\ T_{d2} \leq t < T_{stop}
        \end{cases}

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 initial_value, pulsed_value,
                 rise_delay_time=.0, rise_time_constant=None,
                 fall_delay_time=None, fall_time_constant=None,
             ):

        # Fixme: default

        super().__init__(name, node_plus, node_minus)

        self.initial_value = as_V(initial_value)
        self.pulsed_value = as_V(pulsed_value)
        self.rise_delay_time = as_s(rise_delay_time)
        self.rise_time_constant = as_s(rise_time_constant)
        self.fall_delay_time = as_s(fall_delay_time)
        self.fall_time_constant = as_s(fall_time_constant)

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?
        return ('EXP(' +
                join_list((self.initial_value, self.pulsed_value,
                           self.rise_delay_time, self.rise_time_constant,
                           self.fall_delay_time, self.fall_time_constant,
                       )) +
                ')')

####################################################################################################

class PieceWiseLinear(VoltageSource):

    r"""This class implements a Piece-Wise Linear waveform.

    Spice Syntax::

        PWL( T1 V1 <T2 V2 T3 V3 T4 V4 ... > ) <r=value> <td=value>

    Each pair of values (Ti , Vi) specifies that the value of the source is Vi (in Volts or Amps) at
    time = Ti . The value of the source at intermediate values of time is determined by using linear
    interpolation on the input values. The parameter r determines a repeat time point. If r is not
    given, the whole sequence of values (Ti , Vi ) is issued once, then the output stays at its
    final value. If r = 0, the whole sequence from time = 0 to time = Tn is repeated forever. If r =
    10ns, the sequence between 10ns and 50ns is repeated forever. the r value has to be one of the
    time points T1 to Tn of the PWL sequence. If td is given, the whole PWL sequence is delayed by a
    delay time time = td. The current source still needs to be patched, td and r are not yet
    available.

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 values,
                 repeate_time=0, delay_time=.0,
             ):

        # Fixme: default

        super().__init__(name, node_plus, node_minus)

        self.values = [as_V(x) for x in values]
        self.repeate_time = as_s(repeate_time)
        self.delay_time = as_s(delay_time)

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?
        return ('PWL(' +
                join_list(self.values) +
                join_dict({'r':self.repeate_time, 'td':self.delay_time}) + # OrderedDict(
                ')')

####################################################################################################

class SingleFrequencyFM(VoltageSource):

    r"""This class implements a Single-Frequency FM waveform.

    Spice Syntax::

        SFFM (VO VA FC MDI FS )

   +------+-------------------+---------------+-------+
   | Name + Parameter         + Default Value + Units |
   +------+-------------------+---------------+-------+
   | Vo   + offset            +               + V, A  |
   +------+-------------------+---------------+-------+
   | Va   + amplitude         +               + V, A  |
   +------+-------------------+---------------+-------+
   | Fc   + carrier frequency + 1 / Tstop     + Hz    |
   +------+-------------------+---------------+-------+
   | Mdi  + modulation index  +               +       |
   +------+-------------------+---------------+-------+
   | Fs   + signal frequency  + 1 / Tstop     + Hz    |
   +------+-------------------+---------------+-------+

    The shape of the waveform is described by the following equation:

    .. math::

        V(t) = V_o + V_a \sin (2\pi F_c\, t + M_{di} \sin (2\pi F_s\,t))

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 offset, amplitude, carrier_frequency, modulation_index, signal_frequency):

        super().__init__(name, node_plus, node_minus)

        self.offset = as_V(offset)
        self.amplitude = as_V(amplitude)
        self.carrier_frequency = as_Hz(carrier_frequency)
        self.modulation_index = modulation_index
        self.signal_frequency = as_Hz(signal_frequency)

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?
        return ('SFFM(' +
                join_list((self.offset, self.amplitude, self.carrier_frequency,
                           self.modulation_index, self.signal_frequency)) +
                ')')

####################################################################################################

class AmplitudeModulated(VoltageSource):

    r"""This class implements a Amplitude Modulated source.

    +------+----------------------+---------------+-------+
    | Name + Parameter            + Default Value + Units |
    +------+----------------------+---------------+-------+
    | Vo   + offset               +               + V, A  |
    +------+----------------------+---------------+-------+
    | Va   + amplitude            +               + V, A  |
    +------+----------------------+---------------+-------+
    | Mf   + modulating frequency +               + Hz    |
    +------+----------------------+---------------+-------+
    | Fc   + carrier frequency    + 1 / Tstop     + Hz    |
    +------+----------------------+---------------+-------+
    | Td   + signal delay         +               + s     |
    +------+----------------------+---------------+-------+

    Spice Syntax::

        AM(VA VO MF FC TD)

    The shape of the waveform is described by the following equation:

    .. math::

        V(t) = V_a (V_o + \sin (2\pi M_f\,t)) \sin (2\pi F_c\,t)

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 offset, amplitude, modulating_frequency, carrier_frequency, signal_delay):

        # Fixme: default

        super().__init__(name, node_plus, node_minus)

        self.offset = as_V(offset)
        self.amplitude = as_V(amplitude)
        self.carrier_frequency = as_Hz(carrier_frequency)
        self.modulating_frequency = as_Hz(modulating_frequency)
        self.signal_delay = as_s(signal_delay)

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?
        return ('AM(' +
                join_list((self.offset, self.amplitude, self.carrier_frequency,
                           self.modulating_frequency, self.signal_delay)) +
                ')')

####################################################################################################

class RandomVoltage(VoltageSource):

    r"""This class implements a Random Voltage source.

    The TRRANDOM option yields statistically distributed voltage values, derived from the ngspice
    random number generator. These values may be used in the transient simulation directly within a
    circuit, e.g. for generating a specific noise voltage, but especially they may be used in the
    control of behavioral sources (B, E, G sources, voltage controllable A sources, capacitors,
    inductors, or resistors) to simulate the circuit dependence on statistically varying device
    parameters. A Monte-Carlo simulation may thus be handled in a single simulation run.

    Spice Syntax::

        TRRANDOM( TYPE TS <TD <PARAM1 <PARAM2> > >)

    TYPE determines the random variates generated: 1 is uniformly distributed, 2 Gaussian, 3
    exponential, 4 Poisson. TS is the duration of an individual voltage value. TD is a time delay
    with 0 V output before the random voltage values start up. PARAM1 and PARAM2 depend on the type
    selected.

    +-------------+---------------+---------+-------------+---------+
    | Type        + Parameter 1   + Default + Parameter 2 + Default |
    +-------------+---------------+---------+-------------+---------+
    | uniform     + range         + 1       + offset      + 0       |
    +-------------+---------------+---------+-------------+---------+
    | gaussian    + standard dev. + 1       + mean        + 0       |
    +-------------+---------------+---------+-------------+---------+
    | exponential + mean          + 1       + offset      + 0       |
    +-------------+---------------+---------+-------------+---------+
    | poisson     + lambda        + 1       + offset      + 0       |
    +-------------+---------------+---------+-------------+---------+

    """

    ##############################################

    def __init__(self, name, node_plus, node_minus,
                 random_type, duration=0, time_delay=0, parameter1=1, parameter2=0):

        # Fixme: random_type and parameters

        super().__init__(name, node_plus, node_minus)

        self.random_type = random_type
        self.duration = as_s(duration)
        self.time_delay = as_s(time_delay)
        self.parameter1 = parameter1
        self.parameter2 = parameter2

    ##############################################

    def format_spice_parameters(self):

        if self.random_type == 'uniform':
            random_type = 1
        elif self.random_type == 'exponential':
            random_type = 2
        elif self.random_type == 'gaussian':
            random_type = 3
        elif self.random_type == 'poisson':
            random_type = 4
        else:
            raise ValueError("Wrong random type {}".format(self.random_type))

        # Fixme: to func?
        return ('TRRANDOM(' +
                join_list((random_type, self.duration, self.time_delay,
                           self.parameter1, self.parameter2)) +
                ')')
