###################################################################################################
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

"""This modules implements classes to perform simulations.
"""

####################################################################################################

import logging
import os

####################################################################################################

from ..Config import ConfigInstall
from ..Tools.StringTools import join_list, join_dict, str_spice
from ..Unit import Unit, as_V, as_A, as_s, as_Hz, as_Degree, u_Degree

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AnalysisParameters:

    """Base class for analysis parameters"""

    ANALYSIS_NAME = None

    ##############################################

    @property
    def analysis_name(self):
        return self.ANALYSIS_NAME

    ##############################################

    def to_list(self):
        return ()

    ##############################################

    def __str__(self):
        return '.{0.analysis_name} {1}'.format(self, join_list(self.to_list()))

####################################################################################################

class OperatingPointAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for operating point analysis."""

    ANALYSIS_NAME = 'op'

####################################################################################################

class DcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for DC sensitivity analysis."""

    ANALYSIS_NAME = 'sens'

    ##############################################

    def __init__(self, output_variable):
        self._output_variable = output_variable

    ##############################################

    @property
    def output_variable(self):
        return self._output_variable

    ##############################################

    def to_list(self):
        return (self._output_variable,)

####################################################################################################

class AcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for AC sensitivity analysis."""

    ANALYSIS_NAME = 'sens'

    ##############################################

    def __init__(self, output_variable, variation, number_of_points, start_frequency, stop_frequency):

        if variation not in ('dec', 'oct', 'lin'):
            raise ValueError("Incorrect variation type")

        self._output_variable = output_variable
        self._variation = variation
        self._number_of_points = number_of_points
        self._start_frequency = as_Hz(start_frequency)
        self._stop_frequency = as_Hz(stop_frequency)

    ##############################################

    @property
    def output_variable(self):
        return self._output_variable

    @property
    def variation(self):
        return self._variation

    @property
    def number_of_points(self):
        return self._number_of_points

    @property
    def start_frequency(self):
        return self._start_frequency

    @property
    def stop_frequency(self):
        return self._stop_frequency

    ##############################################

    def to_list(self):
        return (
            self._output_variable,
            self._variation,
            self._number_of_points,
            self._start_frequency,
            self._stop_frequency
        )

####################################################################################################

class DCAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for DC analysis."""

    ANALYSIS_NAME = 'dc'

    ##############################################

    def __init__(self, **kwargs):

        self._parameters = []
        for variable, value_slice in kwargs.items():
            variable_lower = variable.lower()
            if variable_lower[0] in ('v', 'i', 'r') or variable_lower == 'temp':
                self._parameters += [variable, value_slice.start, value_slice.stop, value_slice.step]
            else:
                raise NameError('Sweep variable must be a voltage/current source, '
                                'a resistor or the circuit temperature')

    ##############################################

    @property
    def parameters(self):
        return self._parameters

    ##############################################

    def to_list(self):
        return self._parameters

####################################################################################################

class ACAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for AC analysis."""

    ANALYSIS_NAME = 'ac'

    ##############################################

    def __init__(self, variation, number_of_points, start_frequency, stop_frequency):

        # Fixme: use mixin

        if variation not in ('dec', 'oct', 'lin'):
            raise ValueError("Incorrect variation type")

        self._variation = variation
        self._number_of_points = number_of_points
        self._start_frequency = as_Hz(start_frequency)
        self._stop_frequency = as_Hz(stop_frequency)

    ##############################################

    @property
    def variation(self):
        return self._variation

    @property
    def number_of_points(self):
        return self._number_of_points

    @property
    def start_frequency(self):
        return self._start_frequency

    @property
    def stop_frequency(self):
        return self._stop_frequency

    ##############################################

    def to_list(self):
        return (
            self._variation,
            self._number_of_points,
            self._start_frequency,
            self._stop_frequency
        )

####################################################################################################

class TransientAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for transient analysis."""

    ANALYSIS_NAME = 'tran'

    ##############################################

    def __init__(self, step_time, end_time, start_time=0, max_time=None, use_initial_condition=False):

        self._step_time = as_s(step_time)
        self._end_time = as_s(end_time)
        self._start_time = as_s(start_time)
        self._max_time = as_s(max_time, none=True)
        self._use_initial_condition = use_initial_condition

    ##############################################

    @property
    def step_time(self):
        return self._step_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def start_time(self):
        return self._start_time

    @property
    def max_time(self):
        return self._max_time

    @property
    def use_initial_condition(self):
        return self._use_initial_condition

    ##############################################

    def to_list(self):
        return (
            self._step_time,
            self._end_time,
            self._start_time,
            self._max_time,
            'uic' if self._use_initial_condition else None,
        )

####################################################################################################

class MeasureParameters(AnalysisParameters):

    """This class defines measurements on analysis.

    """

    ANALYSIS_NAME = 'meas'

    ##############################################

    def __init__(self, analysis_type, name, *args):

        _analysis_type = str(analysis_type).upper()
        if _analysis_type not in ('AC', 'DC', 'OP', 'TRAN', 'TF', 'NOISE'):
            raise ValueError('Incorrect analysis type {}'.format(analysis_type))

        self._parameters = [_analysis_type, name, *args]

    ##############################################

    @property
    def parameters(self):
        return self._parameters

    ##############################################

    def to_list(self):
        return self._parameters

####################################################################################################

class PoleZeroAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for pole-zero analysis."""

    ANALYSIS_NAME = 'pz'

    ##############################################

    def __init__(self, node1, node2, node3, node4, tf_type, pz_type):

        self._nodes = (node1, node2, node3, node4)
        self._tf_type = tf_type   # transfert_function
        self._pz_type = pz_type   # pole_zero

    ##############################################

    @property
    def node1(self):
        return self._nodes[0]

    @property
    def node2(self):
        return self._nodes[1]

    def node3(self):
        return self._nodes[2]

    @property
    def node4(self):
        return self._nodes[3]

    @property
    def tf_type(self):
        return self._tf_type

    @property
    def pz_type(self):
        return self._pz_type

    ##############################################

    def to_list(self):
        return list(self._nodes) + [self._tf_type, self._pz_type]

####################################################################################################

class NoiseAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for noise analysis."""

    ANALYSIS_NAME = 'noise'

    ##############################################

    def __init__(self, output, src, variation, points, start_frequency, stop_frequency, points_per_summary):

        self._output = output
        self._src = src
        self._variation = variation
        self._points = points
        self._start_frequency = start_frequency
        self._stop_frequency = stop_frequency
        self._points_per_summary = points_per_summary

    ##############################################

    @property
    def output(self):
        return self._output

    @property
    def src(self):
        return self._src

    @property
    def variation(self):
        return self._variation

    @property
    def points(self):
        return self._points

    # Fixme: mixin
    @property
    def start_frequency(self):
        return self._start_frequency

    @property
    def stop_frequency(self):
        return self._stop_frequency

    @property
    def points_per_summary(self):
        return self._points_per_summary

    ##############################################

    def to_list(self):

        parameters = [
            self._output,
            self._src,
            self._variation,
            self._points,
            self._start_frequency,
            self._stop_frequency,
        ]

        if self._points_per_summary:
            parameters.append(self._points_per_summary)

        return parameters

####################################################################################################

class DistortionAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for distortion analysis."""

    ANALYSIS_NAME = 'disto'

    ##############################################

    def __init__(self, variation, points, start_frequency, stop_frequency, f2overf1):

        self._variation = variation
        self._points = points
        self._start_frequency = start_frequency
        self._stop_frequency = stop_frequency
        self._f2overf1 = f2overf1

    ##############################################

    @property
    def variation(self):
        return self._variation

    @property
    def points(self):
        return self._points

    @property
    def start_frequency(self):
        return self._start_frequency

    @property
    def stop_frequency(self):
        return self._stop_frequency

    @property
    def f2overf1(self):
        return self._f2overf1

    ##############################################

    def to_list(self):

        parameters = [
            self._variation,
            self._points,
            self._start_frequency,
            self._stop_frequency,
        ]

        if self._f2overf1:
            parameters.append(self._f2overf1)

        return parameters

####################################################################################################

class TransferFunctionAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for transfer function (.tf) analysis."""

    ANALYSIS_NAME = 'tf'

    ##############################################

    def __init__(self, outvar, insrc):
        self._outvar = outvar
        self._insrc = insrc

    ##############################################

    @property
    def outvar(self):
        return self._outvar

    @property
    def insrc(self):
        return self._insrc

    ##############################################

    def to_list(self):
        return (self._outvar, self._insrc)

####################################################################################################

class CircuitSimulation:

    """Define and generate the spice instruction to perform a circuit simulation.

    .. warning:: In some cases NgSpice can perform several analyses one after the other. This case
      is partially supported.

    """

    _logger = _module_logger.getChild('CircuitSimulation')

    ##############################################

    def __init__(self, circuit, **kwargs):

        self._circuit = circuit

        self._options = {}   # .options
        self._measures = []   # .measure
        self._initial_condition = {}   # .ic
        self._node_set = {}   # .nodeset
        self._saved_nodes = set()
        self._analyses = {}

        self.temperature = kwargs.get('temperature', u_Degree(27))
        self.nominal_temperature = kwargs.get('nominal_temperature', u_Degree(27))

    ##############################################

    @property
    def circuit(self):
        return self._circuit

    ##############################################

    def options(self, *args, **kwargs):
        for item in args:
            self._options[str(item)] = None
        for key, value in kwargs.items():
            self._options[str(key)] = str_spice(value)

    ##############################################

    @property
    def temperature(self):
        return self._options['TEMP']

    @temperature.setter
    def temperature(self, value):
        self._options['TEMP'] = as_Degree(value)

    ##############################################

    @property
    def nominal_temperature(self):
        return self._options['TNOM']

    @nominal_temperature.setter
    def nominal_temperature(self, value):
        self._options['TNOM'] = as_Degree(value)

    ##############################################

    @staticmethod
    def _make_initial_condition_dict(kwargs):
        return {f"V({key})": str_spice(value) for key, value in kwargs.items()}

    ##############################################

    def initial_condition(self, **kwargs):
        """Set initial condition for voltage nodes.

        Usage::

            simulator.initial_condition(node_name=value, ...)

        General form::

            .ic v(node_name)=value ...

        The `.ic` line is for setting transient initial conditions.  It has two different
        interpretations, depending on whether the uic parameter is specified on the `.tran` control
        line, or not.  One should not confuse this line with the `.nodeset` line.  The `.nodeset`
        line is only to help DC convergence, and does not affect the final bias solution (except for
        multi-stable circuits).  The two indicated interpretations of this line are as follows:

        1. When the uic parameter is specified on the `.tran` line, the node voltages specified on
           the `.ic` control line are used to compute the capacitor, diode, BJT, JFET, and MOSFET
           initial conditions.  This is equivalent to specifying the `ic=...` parameter on each
           device line, but is much more convenient.  The `ic=...` parameter can still be specified
           and takes precedence over the `.ic` values.  Since no dc bias (initial transient)
           solution is computed before the transient analysis, one should take care to specify all
           dc source voltages on the `.ic` control line if they are to be used to compute device
           initial conditions.

        2. When the uic parameter is not specified on the `.tran` control line, the DC bias (initial
           transient) solution is computed before the transient analysis. In this case, the node
           voltages specified on the `.ic` control lines are forced to the desired initial values
           during the bias solution.  During transient analysis, the constraint on these node
           voltages is removed.  This is the preferred method since it allows Ngspice to compute a
           consistent dc solution.

        """
        d = self._make_initial_condition_dict(kwargs)
        self._initial_condition.update(d)

    ##############################################

    def node_set(self, **kwargs):
        """Specify initial node voltage guesses.

        Usage::

            simulator.node_set(node_name=value, ...)

        General form::

            .nodeset v(node_name)=value ...
            .nodeset all=val

        The `.nodeset` line helps the program find the DC or initial transient solution by making a
        preliminary pass with the specified nodes held to the given voltages.  The restrictions are
        then released and the iteration continues to the true solution.  The `.nodeset` line may be
        necessary for convergence on bistable or astable circuits. `.nodeset all=val` sets all
        starting node voltages (except for the ground node) to the same value.  In general, the
        `.nodeset` line should not be necessary.

        """
        d = self._make_initial_condition_dict(kwargs)
        self._node_set.update(d)

    ##############################################

    def save(self, *args):

        # Fixme: pass Node for voltage node, Element for source branch current, ...

        """Set the list of saved vectors.

        If no *.save* line is given, then the default set of vectors is saved (node voltages and
        voltage source branch currents). If *.save* lines are given, only those vectors specified
        are saved.

        Node voltages may be saved by giving the node_name or *v(node_name)*. Currents through an
        independent voltage source (including inductor) are given by *i(source_name)* or
        *source_name#branch*. Internal device data are accepted as *@dev[param]*.

        If you want to save internal data in addition to the default vector set, add the parameter
        *all* to the additional vectors to be saved.

        """

        self._saved_nodes |= set(*args)

    ##############################################

    def save_internal_parameters(self, *args):
        """This method is similar to`save` but assume *all*."""
        # Fixme: ok ???
        self.save(list(args) + ['all'])

    ##############################################

    @property
    def save_currents(self):
        """ Save all currents. """
        return self._options.get('SAVECURRENTS', False)

    @save_currents.setter
    def save_currents(self, value):
        if value:
            self._options['SAVECURRENTS'] = True
        else:
            del self._options['SAVECURRENTS']

    ##############################################

    def reset_analysis(self):
        self._analyses.clear()

    ##############################################

    def analysis_iter(self):
        return self._analyses.values()

    ##############################################

    def _add_analysis(self, analysis_parameters):
        self._analyses[analysis_parameters.analysis_name] = analysis_parameters

    ##############################################

    def _add_measure(self, measure_parameters):
        self._measures.append(measure_parameters)

    ##############################################

    def operating_point(self):
        """Compute the operating point of the circuit with capacitors open and inductors shorted."""
        self._add_analysis(OperatingPointAnalysisParameters())

    ##############################################

    def dc_sensitivity(self, output_variable):

        """Compute the sensitivity of the DC operating point of a node voltage or voltage-source
        branch current to all non-zero device parameters.

        Examples of usage::

            analysis = simulator.dc_sensitivity('v(out)')

        Spice syntax:

        .. code:: spice

            .sens outvar

        Examples:

        .. code:: spice

            .sens V(1, OUT)
            .sens I(VTEST)

        """

        self._add_analysis(DcSensitivityAnalysisParameters(output_variable))

    ##############################################

    def ac_sensitivity(self, output_variable, variation, number_of_points, start_frequency, stop_frequency):

        """Compute the sensitivity of the AC values of a node voltage or voltage-source branch
        current to all non-zero device parameters.

        Examples of usage::

            analysis = simulator.ac_sensitivity(...)

        Spice syntax:

        .. code::

            .sens outvar ac dec nd fstart fstop
            .sens outvar ac oct no fstart fstop
            .sens outvar ac lin np fstart fstop

        Spice examples:

        .. code::

            .sens V(OUT) AC DEC 10 100 100 k

        """

        self._add_analysis(
            AcSensitivityAnalysisParameters(
                output_variable,
                variation, number_of_points, start_frequency, stop_frequency
            ))

    ##############################################

    def dc(self, **kwargs):

        """Compute the DC transfer fonction of the circuit with capacitors open and inductors shorted.

        Examples of usage::

            analysis = simulator.dc(Vinput=slice(-2, 5, .01))
            analysis = simulator.dc(Ibase=slice(0, 100e-6, 10e-6))
            analysis = simulator.dc(Vcollector=slice(0, 5, .1), Ibase=slice(micro(10), micro(100), micro(10))) # broken ???

        Spice syntax:

        .. code:: spice

            .dc src_name vstart vstop vincr [ src2 start2 stop2 incr2 ]

        *src_name* is the name of an independent voltage or a current source, a resistor or the
        circuit temperature.

        *vstart*, *vstop*, and *vincr* are the starting, final, and incrementing values respectively.

        A second source (*src2*) may optionally be specified with associated sweep parameters. In
        this case, the first source is swept over its range for each value of the second source.

        Spice examples:

        .. code:: spice

            .dc VIN 0 .2 5 5.0 0.25
            .dc VDS 0 10 .5 VGS 0 5 1
            .dc VCE 0 10 .2 5 IB 0 10U 1U
            .dc RLoad 1k 2k 100
            .dc TEMP -15 75 5

        """

        self._add_analysis(DCAnalysisParameters(**kwargs))

    ##############################################

    def ac(self, variation, number_of_points, start_frequency, stop_frequency):

        # fixme: concise keyword ?

        """Perform a small-signal AC analysis of the circuit where all non-linear devices are linearized
        around their actual DC operating point.

        Examples of usage::

            analysis = simulator.ac(start_frequency=10@u_kHz, stop_frequency=1@u_GHz, number_of_points=10,  variation='dec')

        Note that in order for this analysis to be meaningful, at least one independent source must
        have been specified with an AC value. Typically it does not make much sense to specify more
        than one AC source. If you do, the result will be a superposition of all sources, thus
        difficult to interpret.

        Spice examples:

        .. code::

            .ac dec nd fstart fstop
            .ac oct no fstart fstop
            .ac lin np fstart fstop

        The parameter *variation* must be either `dec`, `oct` or `lin`.

        """

        self._add_analysis(
            ACAnalysisParameters(
                variation, number_of_points, start_frequency, stop_frequency
            ))

    ##############################################

    def measure(self, analysis_type, name, *args):

        """Add a measure in the circuit.

        Examples of usage::

            simulator.measure('TRAN', 'tdiff', 'TRIG AT=10m', 'TARG v(n1) VAL=75.0 CROSS=1')
            simulator.measure('tran', 'tdiff', 'TRIG AT=0m', f"TARG par('v(n1)-v(derate)') VAL=0 CROSS=1")

        Note: can be used with the .options AUTOSTOP to stop the simulation at Trigger.

        Spice syntax:

        .. code:: spice

            .meas tran tdiff TRIG AT=0m TARG v(n1) VAL=75.0 CROSS=1

        """

        self._add_measure(MeasureParameters(analysis_type, name, *args))

    ##############################################

    def transient(self, step_time, end_time, start_time=0, max_time=None, use_initial_condition=False):

        """Perform a transient analysis of the circuit.

        Examples of usage::

            analysis = simulator.transient(step_time=1@u_us, end_time=500@u_us)
            analysis = simulator.transient(step_time=source.period/200, end_time=source.period*2)

        Spice syntax:

        .. code:: spice

            .tran tstep tstop <tstart <tmax>> <uic>

        """

        self._add_analysis(
            TransientAnalysisParameters(
                step_time, end_time, start_time, max_time,
                use_initial_condition
            ))

    ##############################################

    def polezero(self, node1, node2, node3, node4, tf_type, pz_type):

        """Perform a Pole-Zero analysis of the circuit.

        node1, node2 - Input node pair.
        node3, node4 - Output node pair
        tf_type - should be `cur` for current or `vol` for voltage
        pz_type - should be `pol` for pole, `zer` for zero, or `pz` for combined pole zero analysis.

        See section 15.3.6 of ngspice manual.

        Spice syntax:

        .. code:: spice

            .tran tstep tstop <tstart <tmax>> <uic>
            .pz node1 node2 node3 node4 cur pol
            .pz node1 node2 node3 node4 cur zer
            .pz node1 node2 node3 node4 cur pz
            .pz node1 node2 node3 node4 vol pol
            .pz node1 node2 NODE3 node4 vol zer
            .pz node1 node2 node3 node4 vol pz

        Examples:

        .. code:: spice

            .pz 1 0 3 0 cur pol
            .pz 2 3 5 0 vol zer
            .pz 4 1 4 1 cur pz

        """

        # do some rudimentary parameter checking.
        if tf_type not in ('cur', 'vol'):
            raise NameError("polezero type must be 'cur' or 'vol'")
        if pz_type not in ('pol', 'zer', 'pz'):
            raise NameError("pz_type must be 'pol' or 'zer' or 'pz'")

        self._add_analysis(
            PoleZeroAnalysisParameters(node1, node2, node3, node4, tf_type, pz_type)
        )

    ##############################################

    def noise(self, output_node, ref_node, src, variation, points, start_frequency, stop_frequency, points_per_summary=None):

        """Perform a Pole-Zero analysis of the circuit.

        output_node, ref_node - output node pair.
        src - signal source, typically an ac voltage input.
        variation - must be 'dec' or 'lin' or 'oct' for decade, linear, or octave.
        points, start_frequency, stop_frequency - number of points, start and stop frequencies.
        points_per_summary - if specified, the noise contributions of each noise generator is produced every points_per_summary frequency points.

        See section 15.3.4 of ngspice manual.

        Spice syntax:

        General form:

        .. code:: spice

            .noise v(output <,ref >) src ( dec | lin | oct ) pts fstart fstop <pts_per_summary >

        Examples:

        .. code:: spice

            .noise v(5) VIN dec 10 1kHz 100 MEG
            .noise v(5 ,3) V1 oct 8 1.0 1.0 e6 1

        """

        # do some rudimentary parameter checking.
        # Fixme: mixin
        if variation not in ('dec', 'lin', 'oct'):
            raise NameError("variation must be 'dec' or 'lin' or 'oct'")

        output = 'V({},{})'.format(output_node, ref_node)

        self._add_analysis(
            NoiseAnalysisParameters(output, src, variation, points, start_frequency, stop_frequency, points_per_summary)
        )

    ##############################################

    def transfer_function(self, outvar, insrc):

        """The python arguments to this function should be two strings, outvar and insrc.

        ngspice documentation as follows:

        General form:

        .. code:: spice

            .tf outvar insrc

        Examples:

        .. code:: spice

           .tf v(5, 3) VIN
           .tf i(VLOAD) VIN

        The .tf line defines the small-signal output and input for the dc small-signal
        analysis. outvar is the small signal output variable and insrc is the small-signal input
        source. If this line is included, ngspice computes the dc small-signal value of the transfer
        function (output/input), input resistance, and output resistance. For the first example,
        ngspice would compute the ratio of V(5, 3) to VIN, the small-signal input resistance at VIN,
        and the small signal output resistance measured across nodes 5 and 3

        """

        self._add_analysis(
            TransferFunctionAnalysisParameters(outvar, insrc)
        )

    ##############################################

    def distortion(self, variation, points, start_frequency, stop_frequency, f2overf1=None):

        """Perform a distortion analysis of the circuit.

        variation, points, start_frequency, stop_frequency - typical ac range parameters.
        if f2overf1 is specified, perform a spectral analysis, else perform a harmonic analysis.

        See section 15.3.3 of ngspice manual.

        - harmonic analysis,
          The distof1 parameter of the AC input to the circuit must be specified.
          Second harmonic magnitude and phase are calculated at each circuit node.

        - Spectral analysis,
           The distof2 parameter of the AC input to the circuit must be specified as well as distof1.
           See the ngspice manual.

        Spice syntax:

        General form:

        .. code:: spice

              .disto dec nd fstart fstop <f2overf1 >
              .disto oct no fstart fstop <f2overf1 >
              .disto lin np fstart fstop <f2overf1 >

        Examples:

        .. code:: spice

              .disto dec 10 1kHz 100 MEG
              .disto dec 10 1kHz 100 MEG 0.9

        """

        # do some rudimentary parameter checking.
        if variation not in ('dec', 'lin', 'oct'):
            raise NameError("variation must be 'dec' or 'lin' or 'oct'")

        self._add_analysis(
            DistortionAnalysisParameters(variation, points, start_frequency, stop_frequency, f2overf1)
        )

    ##############################################

    def str_options(self, unit=True):

        # Fixme: use cls settings ???
        if unit:
            _str = str_spice
        else:
            _str = lambda x: str_spice(x, unit)

        netlist = ''
        if self.options:
            for key, value in self._options.items():
                if value is not None:
                    netlist += '.options {} = {}'.format(key, _str(value)) + os.linesep
                else:
                    netlist += '.options {}'.format(key) + os.linesep
        return netlist

    ##############################################

    def __str__(self):

        netlist = self._circuit.str(simulator=self.SIMULATOR)
        netlist += self.str_options()
        if self._initial_condition:
            netlist += '.ic ' + join_dict(self._initial_condition) + os.linesep
        if self._node_set:
            netlist += '.nodeset ' + join_dict(self._node_set) + os.linesep

        if self._saved_nodes:
            # Place 'all' first
            saved_nodes = self._saved_nodes
            if 'all' in saved_nodes:
                all_str = 'all '
                saved_nodes.remove('all')
            else:
                all_str = ''
            netlist += '.save ' + all_str + join_list(saved_nodes) + os.linesep
        for measure_parameters in self._measures:
            netlist += str(measure_parameters) + os.linesep
        for analysis_parameters in self._analyses.values():
            netlist += str(analysis_parameters) + os.linesep
        netlist += '.end' + os.linesep
        return netlist

####################################################################################################

class CircuitSimulator(CircuitSimulation):

    """ This class implements a circuit simulator. Each analysis mode is performed by a method that
    return the measured probes.

    For *ac* and *transient* analyses, the user must specify a list of nodes using the *probes* key
    argument.
    """

    _logger = _module_logger.getChild('CircuitSimulator')

    if ConfigInstall.OS.on_windows:
        DEFAULT_SIMULATOR = 'ngspice-shared'
    else:
        # DEFAULT_SIMULATOR = 'ngspice-subprocess'
        DEFAULT_SIMULATOR = 'ngspice-shared'
        # DEFAULT_SIMULATOR = 'xyce-serial'
        # DEFAULT_SIMULATOR = 'xyce-parallel'

    ##############################################

    @classmethod
    def factory(cls, circuit, *args, **kwargs):

        """Return a :obj:`PySpice.Spice.Simulation.SubprocessCircuitSimulator` or
        :obj:`PySpice.Spice.Simulation.NgSpiceSharedCircuitSimulator` instance depending of the
        value of the *simulator* parameter: ``subprocess`` or ``shared``, respectively. If this
        parameter is not specified then a subprocess simulator is returned.

        """

        if 'simulator' in kwargs:
            simulator = kwargs['simulator']
            del kwargs['simulator']
        else:
            simulator = cls.DEFAULT_SIMULATOR

        sub_cls = None
        if simulator in ('ngspice-subprocess', 'ngspice-shared'):
            if simulator == 'ngspice-subprocess':
                from .NgSpice.Simulation import NgSpiceSubprocessCircuitSimulator
                sub_cls = NgSpiceSubprocessCircuitSimulator
            elif simulator == 'ngspice-shared':
                from .NgSpice.Simulation import NgSpiceSharedCircuitSimulator
                sub_cls = NgSpiceSharedCircuitSimulator
        elif simulator in ('xyce-serial', 'xyce-parallel'):
            from .Xyce.Simulation import XyceCircuitSimulator
            sub_cls = XyceCircuitSimulator
            if simulator == 'xyce-parallel':
                kwargs['parallel'] = True

        if sub_cls is not None:
            return sub_cls(circuit, *args, **kwargs)
        else:
            raise ValueError('Unknown simulator type')

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        self.reset_analysis()
        if 'probes' in kwargs:
            self.save(* kwargs.pop('probes'))

        _kwargs = dict(kwargs)
        _kwargs.pop('log_desk', None)

        method = getattr(CircuitSimulation, analysis_method)
        method(self, *args, **_kwargs)

        message = 'desk' + os.linesep + str(self)
        if kwargs.get('log_desk', False):
            self._logger.info(message)
        else:
            self._logger.debug(message)

    ##############################################

    def operating_point(self, *args, **kwargs):
        return self._run('operating_point', *args, **kwargs)

    ##############################################

    def dc(self, *args, **kwargs):
        return self._run('dc', *args, **kwargs)

    ##############################################

    def dc_sensitivity(self, *args, **kwargs):
        return self._run('dc_sensitivity', *args, **kwargs)

    ##############################################

    def ac(self, *args, **kwargs):
        return self._run('ac', *args, **kwargs)

    ##############################################

    def transient(self, *args, **kwargs):
        return self._run('transient', *args, **kwargs)

    ##############################################

    def polezero(self, *args, **kwargs):
        return self._run('polezero', *args, **kwargs)

    ##############################################

    def noise(self, *args, **kwargs):
        return self._run('noise', *args, **kwargs)

    ##############################################

    def distortion(self, *args, **kwargs):
        return self._run('distortion', *args, **kwargs)

    ##############################################

    def transfer_function(self, *args, **kwargs):
        return self._run('transfer_function', *args, **kwargs)

    tf = transfer_function   # shorcut
