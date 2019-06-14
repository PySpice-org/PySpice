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

    __analysis_name__ = None

    ##############################################

    @property
    def analysis_name(self):
        return self.__analysis_name__

    ##############################################

    def to_list(self):
        return ()

    ##############################################

    def __str__(self):

        return '.{0.analysis_name} {1}'.format(self, join_list(self.to_list()))

####################################################################################################

class OperatingPointAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for operating point analysis."""

    __analysis_name__ = 'op'

####################################################################################################

class DcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for DC sensitivity analysis."""

    __analysis_name__ = 'sens'

    ##############################################

    def __init__(self, output_variable):

        self._output_variable = output_variable

    ##############################################

    @property
    def output_variable(self):
        return self._output_variable

    ##############################################

    def to_list(self):

        return (
            self._output_variable,
        )

####################################################################################################

class AcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for AC sensitivity analysis."""

    __analysis_name__ = 'sens'

    ##############################################

    def __init__(self, output_variable,
                 variation, number_of_points, start_frequency, stop_frequency):

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
    def stop_frequencyr(self):
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

    __analysis_name__ = 'dc'

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

    __analysis_name__ = 'ac'

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
    def stop_frequencyr(self):
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

    __analysis_name__ = 'tran'

    ##############################################

    def __init__(self, step_time, end_time, start_time=0, max_time=None,
                 use_initial_condition=False):

        if use_initial_condition:
            uic = 'uic'
        else:
            uic = None

        self._step_time = as_s(step_time)
        self._end_time = as_s(end_time)
        self._start_time = as_s(start_time)
        self._max_time = as_s(max_time, none=True)
        self._use_initial_condition = uic

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
            self._use_initial_condition,
        )

####################################################################################################

class MeasureParameters(AnalysisParameters):

    """
    This class defines measurements on analysis.
    """

    __analysis_name__ = 'meas'

    ##############################################

    def __init__(self, analysis_type, name, *args):
        
        if (str(analysis_type).upper() not in ('AC', 'DC', 'OP', 'TRAN', 'TF', 'NOISE')):
            raise ValueError("Incorrect analysis type")
        
        self._parameters = [analysis_type, name, *args]

    ##############################################

    @property
    def parameters(self):
        return self._parameters

    ##############################################

    def to_list(self):

        return self._parameters

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

        self._options = {} # .options
        self._measures = [] # .measure
        self._initial_condition = {} # .ic
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

    def initial_condition(self, **kwargs):

        """ Set initial condition for voltage nodes.

        Usage::

            simulator.initial_condition(node_name1=value, ...)

        """

        for key, value in kwargs.items():
            self._initial_condition['V({})'.format(str(key))] = str_spice(value)

        # Fixme: .nodeset

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

        """This method is similar to`save` but assume *all*.
        """

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

        """Compute the sensitivity of the DC operating point of a node voltage or voltage-source branch
        current to all non-zero device parameters.

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

    def ac_sensitivity(self, output_variable,
                       variation, number_of_points, start_frequency, stop_frequency):

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

    def transient(self, step_time, end_time, start_time=0, max_time=None,
                  use_initial_condition=False):

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
        if self.initial_condition:
            netlist += '.ic ' + join_dict(self._initial_condition) + os.linesep
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

        method = getattr(CircuitSimulation, analysis_method)
        method(self, *args, **kwargs)

        self._logger.debug('desk' + os.linesep + str(self))

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
