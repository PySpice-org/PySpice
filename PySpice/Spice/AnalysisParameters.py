###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This modules provides classes to handle analysis parameters.

"""

####################################################################################################

__all__ = [
    'ACAnalysisParameters',
    'AcSensitivityAnalysisParameters',
    'DCAnalysisParameters',
    'DcSensitivityAnalysisParameters',
    'DistortionAnalysisParameters',
    'MeasureParameters',
    'NoiseAnalysisParameters',
    'OperatingPointAnalysisParameters',
    'PoleZeroAnalysisParameters',
    'TransferFunctionAnalysisParameters',
    'TransientAnalysisParameters',
]

####################################################################################################

import logging

from ..Unit import as_Hz, as_s, u_Hz, u_s
from .StringTools import join_list

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AnalysisParameters:

    """Base class for analysis parameters"""

    _ANALYSIS_NAME: str = None  # ty: ignore[invalid-assignment]

    ##############################################

    @property
    def analysis_name(self) -> str:
        return self._ANALYSIS_NAME

    ##############################################

    def to_list(self) -> tuple:
        return ()

    ##############################################

    def __str__(self) -> str:
        return f'.{self.analysis_name} {join_list(self.to_list())}'

####################################################################################################

class OperatingPointAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for operating point analysis."""

    _ANALYSIS_NAME = 'op'

####################################################################################################

class DcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for DC sensitivity analysis."""

    _ANALYSIS_NAME = 'sens'

    ##############################################

    def __init__(self, output_variable: str) -> None:
        self._output_variable = output_variable

    ##############################################

    @property
    def output_variable(self) -> str:
        return self._output_variable

    ##############################################

    def to_list(self) -> tuple:
        return (self._output_variable,)

####################################################################################################

class AcSensitivityAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for AC sensitivity analysis."""

    _ANALYSIS_NAME = 'sens'

    ##############################################

    def __init__(
            self,
            output_variable: str,
            variation: str,
            number_of_points: int,
            start_frequency: u_Hz | float,
            stop_frequency: u_Hz | float,
    ) -> None:
        if variation not in ('dec', 'oct', 'lin'):
            raise ValueError("Incorrect variation type")

        self._output_variable = output_variable
        self._variation = variation
        self._number_of_points = number_of_points
        self._start_frequency: u_Hz = as_Hz(start_frequency)
        self._stop_frequency: u_Hz = as_Hz(stop_frequency)

    ##############################################

    @property
    def output_variable(self) -> str:
        return self._output_variable

    @property
    def variation(self) -> str:
        return self._variation

    @property
    def number_of_points(self) -> int:
        return self._number_of_points

    @property
    def start_frequency(self) -> u_Hz:
        return self._start_frequency

    @property
    def stop_frequency(self) -> u_Hz:
        return self._stop_frequency

    ##############################################

    def to_list(self) -> tuple[str, str, int, u_Hz, u_Hz]:
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

    _ANALYSIS_NAME = 'dc'

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
    def parameters(self) -> list:
        return self._parameters

    ##############################################

    def to_list(self) -> tuple:
        return tuple(self._parameters)

####################################################################################################

class ACAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for AC analysis."""

    _ANALYSIS_NAME = 'ac'

    ##############################################

    def __init__(
            self,
            variation: str,
            number_of_points: int,
            start_frequency: u_Hz | float,
            stop_frequency: u_Hz | float,
    ) -> None:
        # Fixme: use mixin
        if variation not in ('dec', 'oct', 'lin'):
            raise ValueError("Incorrect variation type")

        self._variation = variation
        self._number_of_points = number_of_points
        self._start_frequency: u_Hz = as_Hz(start_frequency)
        self._stop_frequency: u_Hz = as_Hz(stop_frequency)

    ##############################################

    @property
    def variation(self) -> str:
        return self._variation

    @property
    def number_of_points(self) -> int:
        return self._number_of_points

    @property
    def start_frequency(self) -> u_Hz:
        return self._start_frequency

    @property
    def stop_frequency(self) -> u_Hz:
        return self._stop_frequency

    ##############################################

    def to_list(self) -> tuple[str, int, u_Hz, u_Hz]:
        return (
            self._variation,
            self._number_of_points,
            self._start_frequency,
            self._stop_frequency
        )

####################################################################################################

class TransientAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for transient analysis."""

    _ANALYSIS_NAME = 'tran'

    ##############################################

    def __init__(
            self,
            step_time: float,
            end_time: float,
            start_time: float = 0,
            max_time: float | None = None,
            use_initial_condition: bool = False,
    ) -> None:
        # Fixme: as_s -> PeriodValue
        self._step_time: u_s = as_s(step_time)
        self._end_time: u_s = as_s(end_time)
        self._start_time: u_s = as_s(start_time)
        self._max_time: u_s | None = as_s(max_time, none=True)  # ty: ignore[invalid-argument-type]
        self._use_initial_condition = use_initial_condition

    ##############################################

    @property
    def step_time(self) -> u_s:
        return self._step_time

    @property
    def end_time(self) -> u_s:
        return self._end_time

    @property
    def start_time(self) -> u_s:
        return self._start_time

    @property
    def max_time(self) -> u_s | None:
        return self._max_time

    @property
    def use_initial_condition(self) -> bool:
        return self._use_initial_condition

    ##############################################

    def to_list(self) -> tuple[u_s, u_s, u_s, u_s | None, str | None]:
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

    _ANALYSIS_NAME = 'meas'

    ##############################################

    def __init__(self, analysis_type: str, name: str, *args):
        _analysis_type = str(analysis_type).upper()
        if _analysis_type not in ('AC', 'DC', 'OP', 'TRAN', 'TF', 'NOISE'):
            raise ValueError(f'Incorrect analysis type {analysis_type}')
        self._parameters = [_analysis_type, name, *args]

    ##############################################

    @property
    def parameters(self) -> list:
        return self._parameters

    ##############################################

    def to_list(self) -> tuple:
        return tuple(self._parameters)

####################################################################################################

class PoleZeroAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for pole-zero analysis."""

    _ANALYSIS_NAME = 'pz'

    ##############################################

    def __init__(self, node1, node2, node3, node4, tf_type, pz_type) -> None:
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

    def to_list(self) -> tuple:
        return tuple(list(self._nodes) + [self._tf_type, self._pz_type])

####################################################################################################

class NoiseAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for noise analysis."""

    _ANALYSIS_NAME = 'noise'

    ##############################################

    def __init__(
            self,
            output,
            src,
            variation: str,
            points,
            start_frequency: u_Hz | float,
            stop_frequency: u_Hz | float,
            points_per_summary: int | None,
    ) -> None:
        self._output = output
        self._src = src
        self._variation = variation
        self._points = points
        self._start_frequency: u_Hz = as_Hz(start_frequency)
        self._stop_frequency: u_Hz = as_Hz(stop_frequency)
        self._points_per_summary = points_per_summary

    ##############################################

    @property
    def output(self):
        return self._output

    @property
    def src(self):
        return self._src

    @property
    def variation(self) -> str:
        return self._variation

    @property
    def points(self):
        return self._points

    # Fixme: mixin
    @property
    def start_frequency(self) -> u_Hz:
        return self._start_frequency

    @property
    def stop_frequency(self) -> u_Hz:
        return self._stop_frequency

    @property
    def points_per_summary(self) -> int | None:
        return self._points_per_summary

    ##############################################

    def to_list(self) -> tuple:
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
        return tuple(parameters)

####################################################################################################

class DistortionAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for distortion analysis."""

    _ANALYSIS_NAME = 'disto'

    ##############################################

    def __init__(
            self,
            variation,
            points,
            start_frequency: u_Hz | float,
            stop_frequency: u_Hz | float,
            f2overf1,
    ) -> None:
        self._variation = variation
        self._points = points
        self._start_frequency: u_Hz = as_Hz(start_frequency)
        self._stop_frequency: u_Hz = as_Hz(stop_frequency)
        self._f2overf1 = f2overf1

    ##############################################

    @property
    def variation(self) -> str:
        return self._variation

    @property
    def points(self):
        return self._points

    @property
    def start_frequency(self) -> u_Hz:
        return self._start_frequency

    @property
    def stop_frequency(self) -> u_Hz:
        return self._stop_frequency

    @property
    def f2overf1(self):
        return self._f2overf1

    ##############################################

    def to_list(self) -> tuple:
        parameters = [
            self._variation,
            self._points,
            self._start_frequency,
            self._stop_frequency,
        ]
        if self._f2overf1:
            parameters.append(self._f2overf1)
        return tuple(parameters)

####################################################################################################

class TransferFunctionAnalysisParameters(AnalysisParameters):

    """This class defines analysis parameters for transfer function (.tf) analysis."""

    _ANALYSIS_NAME = 'tf'

    ##############################################

    def __init__(self, outvar, insrc) -> None:
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

    def to_list(self) -> tuple:
        return (self._outvar, self._insrc)
