###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This modules provides classes to generate the simulation part of the Spice desk, i.e. the line
starting by a dot at the end of the desk.

.. warning:: Simulation features depend of the simulator.

"""

####################################################################################################

import datetime
import logging
import os
from collections.abc import Callable, ValuesView
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, Unpack, cast

from ..Tools.TextBuffer import TextBuffer
from ..Unit import as_Degree, u_Degree
from ..Unit.Unit import UnitValue
from .AnalysisParameters import (
    ACAnalysisParameters,
    AcSensitivityAnalysisParameters,
    AnalysisParameters,
    DCAnalysisParameters,
    DcSensitivityAnalysisParameters,
    DistortionAnalysisParameters,
    MeasureParameters,
    NoiseAnalysisParameters,
    OperatingPointAnalysisParameters,
    PoleZeroAnalysisParameters,
    TransferFunctionAnalysisParameters,
    TransientAnalysisParameters,
)
from .StringTools import join_dict, join_list
from .unit import str_spice

if TYPE_CHECKING:
    from PySpice.Probe.WaveForm import Analysis

    from .Netlist import Circuit
    from .Simulator import Simulator

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SimulationParams(TypedDict):
    temperature: NotRequired[u_Degree]  # = DEFAULT_Temperature
    nominal_temperature: NotRequired[u_Degree]  # = DEFAULT_Temperature

class RunSimulationParams(TypedDict):
    log_desk: NotRequired[bool]
    probes: NotRequired[list[str]]
    run: NotRequired[bool]

class Simulation:

    """Define and generate the Spice instruction to perform a simulation.

    Constructor Parameters
    ----------------------

    Simulation temperatures are set by default to 27°C, you can change theses values using the
    parameter `temperature` and `nominal_temperature`, respectively.

    Analysis Method Parameters
    --------------------------

    For *ac* and *transient* analyses, the user must specify a list of nodes using the *probes* key
    argument.

    You can log the desk using the parameter `log_desk` set to `True`.

    By default the analysis method runs the simulation and return the result, you can disable this
    feature using the parameter `run` set to `False`.

    .. warning:: In some cases NgSpice can perform several analyses one after the other. This case
                 is partially supported.

    """

    _logger = _module_logger.getChild('Simulation')

    DEFAULT_TEMPERATURE = u_Degree(27)

    ##############################################

    def __init__(self, simulator: Simulator, circuit: Circuit, **kwargs: Unpack[SimulationParams]) -> None:
        self._simulator = simulator
        self._circuit = circuit

        self._options: dict[str, str | bool | None] = {}   # .options
        self.temperature = kwargs.get('temperature', self.DEFAULT_TEMPERATURE)
        self.nominal_temperature = kwargs.get('nominal_temperature', self.DEFAULT_TEMPERATURE)

        self._measures: list[str] = []   # .measure
        self._initial_condition: dict[str, str] = {}   # .ic
        self._node_set: dict[str, str] = {}   # .nodeset
        self._saved_nodes: set[str] = set()
        self._analyses: dict[str, AnalysisParameters] = {}
        self._simulation_date: datetime.datetime = None  # ty: ignore[invalid-assignment]
        self._simulation_duration: datetime.timedelta = None  # ty: ignore[invalid-assignment]

    ##############################################

    def __getstate__(self) -> dict[str, Any]:
        # Pickle: get state
        state = self.__dict__.copy()
        # state['_simulator'] = self._simulator.__class__.__name__
        state['_simulator'] = self._simulator.name
        # state['_circuit'] = ...
        return state

    ##############################################

    def __setstate__(self, state: dict[str, Any]) -> None:
        # Pickle: restore state
        self.__dict__.update(state)
        # Fixme: ok ??? duplicate simulator ???
        from .Simulator import Simulator
        self._simulator = Simulator.factory(simulator=state['_simulator'])

    ##############################################

    @property
    def circuit(self) -> Circuit:
        return self._circuit

    @property
    def simulator(self) -> Simulator:
        return self._simulator

    ##############################################

    @property
    def simulator_name(self) -> str:
        return self._simulator.name

    @property
    def simulator_version(self) -> str:
        return self._simulator.version

    @property
    def simulation_date(self) -> datetime.datetime:
        return self._simulation_date

    @property
    def simulation_duration(self) -> datetime.timedelta:
        return self._simulation_duration

    ##############################################

    def options(self, *args, **kwargs) -> None:
        for item in args:
            self._options[str(item)] = None
        for key, value in kwargs.items():
            self._options[str(key)] = str_spice(value)

    ##############################################

    @property
    def temperature(self) -> u_Degree:
        return self._options['TEMP']

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._options['TEMP'] = as_Degree(value)

    ##############################################

    @property
    def nominal_temperature(self) -> u_Degree:
        return self._options['TNOM']

    @nominal_temperature.setter
    def nominal_temperature(self, value: float) -> None:
        self._options['TNOM'] = as_Degree(value)

    ##############################################

    @staticmethod
    def _make_initial_condition_dict(kwargs: dict[str, UnitValue | str]) -> dict[str, str]:
        return {f"V({key})": str_spice(value) for key, value in kwargs.items()}

    ##############################################

    def initial_condition(self, **kwargs: UnitValue | str) -> None:
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

    def node_set(self, **kwargs: UnitValue | str) -> None:
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

    def save(self, *args: str) -> None:
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

    def save_internal_parameters(self, *args: str) -> None:
        """This method is similar to`save` but assume *all*."""
        # Fixme: ok ???
        # self.save(list(args) + ['all'])
        self.save(*args, 'all')

    ##############################################

    @property
    def save_currents(self) -> bool:
        """ Save all currents. """
        return cast(bool, self._options.get('SAVECURRENTS', False))

    @save_currents.setter
    def save_currents(self, value: bool) -> None:
        if value:
            self._options['SAVECURRENTS'] = True
        else:
            del self._options['SAVECURRENTS']

    ##############################################

    def reset_analysis(self) -> None:
        self._analyses.clear()

    ##############################################

    def analysis_iter(self) -> ValuesView[AnalysisParameters]:
        # Fixme: -> analyses / item()
        #   used for ???
        return self._analyses.values()

    ##############################################

    def _add_analysis(self, analysis_parameters: AnalysisParameters) -> None:
        self._analyses[analysis_parameters.analysis_name] = analysis_parameters

    ##############################################

    def _add_measure(self, measure_parameters) -> None:
        self._measures.append(measure_parameters)

    ##############################################

    def _impl_operating_point(self) -> None:
        """Compute the operating point of the circuit with capacitors open and inductors shorted."""
        self._add_analysis(OperatingPointAnalysisParameters())

    ##############################################

    def _impl_dc_sensitivity(self, output_variable: str) -> None:
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

    # Fixme: implement AnalysisParameters protocol
    def _impl_ac_sensitivity(
            self,
            output_variable: str,
            variation,
            number_of_points,
            start_frequency,
            stop_frequency,
    ) -> None:
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

    def _impl_dc(self, **kwargs) -> None:
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

    def _impl_ac(
            self,
            variation,
            number_of_points,
            start_frequency,
            stop_frequency,
    ) -> None:
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

    def _impl_measure(self, analysis_type, name, *args) -> None:
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

    def _impl_transient(
        self,
        step_time,
        end_time,
        start_time=0,
        max_time=None,
        use_initial_condition=False,
    ) -> None:
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

    def _impl_polezero(self, node1, node2, node3, node4, tf_type, pz_type) -> None:
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

    def _impl_noise(
        self,
        output_node,
        ref_node,
        src,
        variation,
        points,
        start_frequency,
        stop_frequency,
        points_per_summary: int | None = None,
    ):
        """Perform a Pole-Zero analysis of the circuit.

        output_node, ref_node - output node pair.
        src - signal source, typically an ac voltage input.
        variation - must be 'dec' or 'lin' or 'oct' for decade, linear, or octave.
        points, start_frequency, stop_frequency - number of points, start and stop frequencies.
        points_per_summary - if specified, the noise contributions of each noise generator
            is produced every points_per_summary frequency points.

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
        output = f'V({output_node}, {ref_node})'
        self._add_analysis(
            NoiseAnalysisParameters(
                output, src,
                variation, points,
                start_frequency, stop_frequency,
                points_per_summary,
            )
        )

    ##############################################

    def _impl_transfer_function(self, outvar, insrc) -> None:
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

    def _impl_distortion(
            self,
            variation,
            points,
            start_frequency,
            stop_frequency,
            f2overf1=None,
    ) -> None:
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

    def str_options(self, unit: bool = True) -> TextBuffer:
        # Fixme: use cls settings ???
        if unit:
            _str = str_spice
        else:
            def _str(x):
                return str_spice(x, unit)
        netlist = TextBuffer()
        for key, value in self._options.items():
            _ = f'.options {key}'
            if value is not None:
                _ += f' = {_str(value)}'
            netlist += _
        return netlist

    ##############################################

    def str_netlist(self) -> str:
        return self._circuit.str(simulator=self.simulator.SIMULATOR)

    ##############################################

    def str_simulation(self) -> str:
        lines = self.str_options()
        if self._initial_condition:
            lines += '.ic ' + join_dict(self._initial_condition)
        if self._node_set:
            lines += '.nodeset ' + join_dict(self._node_set)

        if self._saved_nodes:
            # Place 'all' first
            saved_nodes = self._saved_nodes
            if 'all' in saved_nodes:
                all_str = 'all '
                saved_nodes.remove('all')
            else:
                all_str = ''
            lines += '.save ' + all_str + join_list(saved_nodes)
        for measure_parameters in self._measures:
            lines += str(measure_parameters)
        for analysis_parameters in self._analyses.values():
            lines += str(analysis_parameters)
        lines += '.end'
        return str(lines)

    ##############################################

    def __str__(self) -> str:
        return self.str_netlist() + self.str_simulation()

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):
        # Trick to execute code before/after the analysis implementation
        log_desk = kwargs.pop('log_desk', None)
        run = kwargs.pop('run', True)

        if 'probes' in kwargs:
            self.save(* kwargs.pop('probes'))

        # Execute analysis implementation
        analysis_method(self, *args, **kwargs)

        # Set simulator's specific settings
        self._simulator.customise(self)

        # Log the desk ?
        message = 'desk' + os.linesep + str(self)
        if log_desk:
            self._logger.info(message)
        else:
            self._logger.debug(message)

        # Run simulation ?
        if run:
            now = datetime.datetime.now()
            self._simulation_date = now
            analysis = self._simulator.run(self)
            self._simulation_duration = now - self._simulation_date
            return analysis

    ##############################################

    # Fixme: cf. impl
    ac: Callable
    ac_sensitivity: Callable
    dc: Callable
    dc_sensitivity: Callable
    distortion: Callable
    measure: Callable
    noise: Callable
    operating_point: Callable
    polezero: Callable
    transfer_function: Callable
    transient: Callable

    tf: Callable

####################################################################################################

# Register analysis wrappers and shortcuts in Simulation

def _make_wrapper(analysis_method: Callable) -> Callable:
    def wrapper(self, *args, **kwargs):
        return self._run(analysis_method, *args, **kwargs)
    return wrapper

_ANALYSES_PREFIX = '_impl_'
_ANALYSES_METHOD: list[Callable] = [
    method
    for method in Simulation.__dict__.values()
    if callable(method) and method.__name__.startswith(_ANALYSES_PREFIX)
]

_SHORTCUTS: dict[str, str] = {
    'transfer_function': 'tf',
}

for _analysis_method in _ANALYSES_METHOD:
    _wrapper = _make_wrapper(_analysis_method)
    _wrapper.__doc__ = _analysis_method.__doc__
    _analysis = _analysis_method.__name__[len(_ANALYSES_PREFIX):]  # ty: ignore[unresolved-attribute]
    setattr(Simulation, _analysis, _wrapper)
    _shortcut = _SHORTCUTS.get(_analysis)
    if _shortcut:
        setattr(Simulation, _shortcut, _wrapper)
