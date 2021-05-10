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

"""This module implements high level elements built on top of Spice elements."""

# Fixme: check NgSpice for discrepancies

####################################################################################################

from ..Math import rms_to_amplitude, amplitude_to_rms
from ..Tools.StringTools import join_list, join_dict, str_spice, str_spice_list
from ..Unit import as_s, as_V, as_A, as_Hz
from .BasicElement import VoltageSource, CurrentSource

####################################################################################################

class SourceMixinAbc:
    AS_UNIT = None

####################################################################################################

class VoltageSourceMixinAbc:
    AS_UNIT = as_V

####################################################################################################

class CurrentSourceMixinAbc:
    AS_UNIT = as_A

####################################################################################################

class SinusoidalMixin(SourceMixinAbc):

    r"""This class implements a sinusoidal waveform.

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

      :attr:`ac_magnitude`

      :attr:`amplitude`

      :attr:`damping_factor`

      :attr:`dc_offset`

      :attr:`delay`

      :attr:`frequency`

      :attr:`offset`

    """

    ##############################################

    def __init__(self,
                 dc_offset=0,
                 ac_magnitude=1,
                 offset=0, amplitude=1, frequency=50,
                 delay=0, damping_factor=0):

        self.dc_offset = self.AS_UNIT(dc_offset)
        self.ac_magnitude = self.AS_UNIT(ac_magnitude)
        self.offset = self.AS_UNIT(offset)
        self.amplitude = self.AS_UNIT(amplitude)
        self.frequency = as_Hz(frequency)   # Fixme: protect by setter?
        self.delay = as_s(delay)
        self.damping_factor = as_Hz(damping_factor)

    ##############################################

    @property
    def rms_voltage(self):
        # Fixme: ok ???
        return amplitude_to_rms(self.amplitude * self.ac_magnitude)

    ##############################################

    @property
    def period(self):
        return self.frequency.period

    ##############################################

    def format_spice_parameters(self):
        sin_part = join_list((self.offset, self.amplitude, self.frequency, self.delay, self.damping_factor))
        return join_list((
            'DC {} AC {}'.format(*str_spice_list(self.dc_offset, self.ac_magnitude)),
            'SIN({})'.format(sin_part),
        ))

####################################################################################################

class PulseMixin(SourceMixinAbc):

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
    | Phase  + phase         + 0.0           + sec   |
    +--------+---------------+---------------+-------+

    Phase is only possible when XSPICE is enabled

    Spice Syntax::

        PULSE ( V1 V2 Td Tr Tf Pw Period Phase )

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

      :attr:`phase`

      :attr:`pulse_width`

      :attr:`pulsed_value`

      :attr:`rise_time`

    """

    ##############################################

    def __init__(self,
                 initial_value, pulsed_value,
                 pulse_width, period,
                 delay_time=0, rise_time=0, fall_time=0,
                 phase=None,
                 dc_offset=0):

        # Fixme: default
        #  rise_time, fall_time = Tstep
        #  pulse_width, period = Tstop

        self.dc_offset = self.AS_UNIT(dc_offset)   # Fixme: -> SourceMixinAbc
        self.initial_value = self.AS_UNIT(initial_value)
        self.pulsed_value = self.AS_UNIT(pulsed_value)
        self.delay_time = as_s(delay_time)
        self.rise_time = as_s(rise_time)
        self.fall_time = as_s(fall_time)
        self.pulse_width = as_s(pulse_width)
        self.period = as_s(period)   # Fixme: protect by setter?

        # XSPICE
        if phase is not None:
            self.phase = as_s(phase)
        else:
            self.phase = None

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

        # if DC is not provided, ngspice complains
        #   Warning: vpulse: no DC value, transient time 0 value used

        # Fixme: to func?
        return join_list((
            'DC {}'.format(str_spice(self.dc_offset)),
            'PULSE(' +
            join_list((self.initial_value, self.pulsed_value, self.delay_time,
                       self.rise_time, self.fall_time, self.pulse_width, self.period,
                       self.phase)) +
            ')'))

####################################################################################################

class ExponentialMixin(SourceMixinAbc):

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

    def __init__(self,
                 initial_value, pulsed_value,
                 rise_delay_time=.0, rise_time_constant=None,
                 fall_delay_time=None, fall_time_constant=None):

        # Fixme: default

        self.initial_value = self.AS_UNIT(initial_value)
        self.pulsed_value = self.AS_UNIT(pulsed_value)
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

class PieceWiseLinearMixin(SourceMixinAbc):

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

    `values` should be given as a list of (`Time`, `Value`)-tuples, e.g.::

        PieceWiseLinearVoltageSource(
            circuit,
            'pwl1', '1', '0',
            values=[(0, 0), (10@u_ms, 0), (11@u_ms, 5@u_V), (20@u_ms, 5@u_V)],
        )

    """

    ##############################################

    def __init__(self, values, repeat_time=None, delay_time=None, dc=None):
        self.values = sum(([as_s(t), self.AS_UNIT(x)] for (t, x) in values), [])
        self.repeat_time = as_s(repeat_time, none=True)
        self.delay_time = as_s(delay_time, none=True)
        self.dc = self.AS_UNIT(dc, none=True)

    ##############################################

    def format_spice_parameters(self):

        # Fixme: to func?

        d = {}
        if self.repeat_time is not None:
            d["r"] = self.repeat_time
        if self.delay_time is not None:
            d["td"] = self.delay_time

        _ = ""
        if self.dc is not None:
            _ += "DC {} ".format(str_spice(self.dc))
        _ += "PWL(" + join_list(self.values)
        if d:
            _ += " " + join_dict(d)   # OrderedDict(
        _ += ")"

        return _

####################################################################################################

class SingleFrequencyFMMixin(SourceMixinAbc):

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

    def __init__(self, offset, amplitude, carrier_frequency, modulation_index, signal_frequency):
        self.offset = self.AS_UNIT(offset)
        self.amplitude = self.AS_UNIT(amplitude)
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

class AmplitudeModulatedMixin(SourceMixinAbc):

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

    def __init__(self, offset, amplitude, modulating_frequency, carrier_frequency, signal_delay):

        # Fixme: default

        self.offset = self.AS_UNIT(offset)
        self.amplitude = self.AS_UNIT(amplitude)
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

class RandomMixin(SourceMixinAbc):

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

    def __init__(self, random_type, duration=0, time_delay=0, parameter1=1, parameter2=0):
        # Fixme: random_type and parameters
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

####################################################################################################

class SinusoidalVoltageSource(VoltageSource, VoltageSourceMixinAbc, SinusoidalMixin):

    r"""This class implements a sinusoidal waveform voltage source.

    See :class:`SinusoidalMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        SinusoidalMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = SinusoidalMixin.format_spice_parameters

####################################################################################################

class SinusoidalCurrentSource(CurrentSource, CurrentSourceMixinAbc, SinusoidalMixin):

    r"""This class implements a sinusoidal waveform current source.

    See :class:`SinusoidalMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        SinusoidalMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = SinusoidalMixin.format_spice_parameters

####################################################################################################

class AcLine(SinusoidalVoltageSource):

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, rms_voltage=230, frequency=50):
        super().__init__(netlist, name, node_plus, node_minus,
                         amplitude=rms_to_amplitude(rms_voltage),
                         frequency=frequency)

####################################################################################################

class PulseVoltageSource(VoltageSource, VoltageSourceMixinAbc, PulseMixin):

    r"""This class implements a pulse waveform voltage source.

    See :class:`PulseMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        PulseMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = PulseMixin.format_spice_parameters

####################################################################################################

class PulseCurrentSource(CurrentSource, CurrentSourceMixinAbc, PulseMixin):

    r"""This class implements a pulse waveform current source.

    See :class:`PulseMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        PulseMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = PulseMixin.format_spice_parameters

####################################################################################################

class ExponentialVoltageSource(VoltageSource, VoltageSourceMixinAbc, ExponentialMixin):

    r"""This class implements a exponential waveform voltage source.

    See :class:`ExponentialMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        ExponentialMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = ExponentialMixin.format_spice_parameters

####################################################################################################

class ExponentialCurrentSource(CurrentSource, CurrentSourceMixinAbc, ExponentialMixin):

    r"""This class implements a exponential waveform current source.

    See :class:`ExponentialMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        ExponentialMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = ExponentialMixin.format_spice_parameters

####################################################################################################

class PieceWiseLinearVoltageSource(VoltageSource, VoltageSourceMixinAbc, PieceWiseLinearMixin):

    r"""This class implements a piece wise linear waveform voltage source.

    See :class:`PieceWiseLinearMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        PieceWiseLinearMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = PieceWiseLinearMixin.format_spice_parameters

####################################################################################################

class PieceWiseLinearCurrentSource(CurrentSource, CurrentSourceMixinAbc, PieceWiseLinearMixin):

    r"""This class implements a piece wise linear waveform current source.

    See :class:`PieceWiseLinearMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        PieceWiseLinearMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = PieceWiseLinearMixin.format_spice_parameters

####################################################################################################

class SingleFrequencyFMVoltageSource(VoltageSource, VoltageSourceMixinAbc, SingleFrequencyFMMixin):

    r"""This class implements a single frequency FM waveform voltage source.

    See :class:`SingleFrequencyFMMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):

        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        SingleFrequencyFMMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = SingleFrequencyFMMixin.format_spice_parameters

####################################################################################################

class SingleFrequencyFMCurrentSource(CurrentSource, CurrentSourceMixinAbc, SingleFrequencyFMMixin):

    r"""This class implements a single frequency FM waveform current source.

    See :class:`SingleFrequencyFMMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        SingleFrequencyFMMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = SingleFrequencyFMMixin.format_spice_parameters

####################################################################################################

class AmplitudeModulatedVoltageSource(VoltageSource, VoltageSourceMixinAbc, AmplitudeModulatedMixin):

    r"""This class implements a amplitude modulated waveform voltage source.

    See :class:`AmplitudeModulatedMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        AmplitudeModulatedMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = AmplitudeModulatedMixin.format_spice_parameters

####################################################################################################

class AmplitudeModulatedCurrentSource(CurrentSource, CurrentSourceMixinAbc, AmplitudeModulatedMixin):

    r"""This class implements a amplitude modulated waveform current source.

    See :class:`AmplitudeModulatedMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        AmplitudeModulatedMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = AmplitudeModulatedMixin.format_spice_parameters

####################################################################################################

class RandomVoltageSource(VoltageSource, VoltageSourceMixinAbc, RandomMixin):

    r"""This class implements a random waveform voltage source.

    See :class:`RandomMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        VoltageSource.__init__(self, netlist, name, node_plus, node_minus)
        RandomMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = RandomMixin.format_spice_parameters

####################################################################################################

class RandomCurrentSource(CurrentSource, CurrentSourceMixinAbc, RandomMixin):

    r"""This class implements a random waveform current source.

    See :class:`RandomMixin` for documentation.

    """

    ##############################################

    def __init__(self, netlist, name, node_plus, node_minus, *args, **kwargs):
        CurrentSource.__init__(self, netlist, name, node_plus, node_minus)
        RandomMixin.__init__(self, *args, **kwargs)

    ##############################################

    format_spice_parameters = RandomMixin.format_spice_parameters
