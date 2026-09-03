####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This module provide tools to read raw output.
"""

####################################################################################################

import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING

import numpy as np

from PySpice.Probe.WaveForm import (
    AcAnalysis,
    DcAnalysis,
    OperatingPoint,
    SensitivityAnalysis,
    TransientAnalysis,
    WaveForm,
)
from PySpice.Unit import UnitValueShorcut, u_A, u_Degree, u_Hz, u_s, u_V

if TYPE_CHECKING:
    from .Netlist import Circuit
    from .Simulation import Simulation

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class VariableAbc:

    """This class implements a variable or probe in a SPICE simulation output.

    Public Attributes:

      :attr:`index`
        index in the array

      :attr:`name`

      :attr:`unit`

    """

    ##############################################

    def __init__(self, index: int, name: str, unit: UnitValueShorcut | None) -> None:
        # Fixme: self._ ?
        self._index = int(index)
        self.name = str(name)
        self._unit = unit  # could be guessed from name also for voltage node and branch current
        self.data: np.ndarray = None  # ty: ignore[invalid-assignment]

    ##############################################

    @property
    def index(self) -> int:
        return self._index

    # @property
    # def name(self):
    #     return self._name

    # @name.setter
    # def name(self, value):
    #     self._name = value

    ##############################################

    def __repr__(self) -> str:
        return f'variable[{self._index}]: {self.name} [{self._unit}]'

    ##############################################

    def is_voltage_node(self) -> bool:
        raise NotImplementedError

    ##############################################

    def is_branch_current(self) -> bool:
        raise NotImplementedError

    ##############################################

    @property
    def is_interval_parameter(self) -> bool:
        return self.name.startswith('@')  # Fixme: Xyce ???

    ##############################################

    @staticmethod
    def to_voltage_name(node: str) -> str:
        return f'v({node})'

    ##############################################

    @staticmethod
    def to_branch_name(element: str) -> str:
        return f'i({element})'

    ##############################################

    def fix_case(self, element_translation: dict[str, str], node_translation: dict[str, str],) -> None:
        """ Update the name to the right case. """
        if self.is_branch_current():
            if self.simplified_name in element_translation:
                self.name = self.to_branch_name(element_translation[self.simplified_name])
        elif self.is_voltage_node() and self.simplified_name in node_translation:
            self.name = self.to_voltage_name(node_translation[self.simplified_name])

    ##############################################

    @property
    def simplified_name(self) -> str:
        raise NotImplementedError

    ##############################################

    def to_waveform(
            self,
            abscissa: WaveForm | None = None,
            to_real: bool = False,
            to_float: bool = False,
    ) -> WaveForm:
        """ Return a :obj:`PySpice.Probe.WaveForm` instance. """
        data = self.data
        if to_real:
            data = data.real
        # Fixme: else UnitValue instead of UnitValues
        # if to_float:
        #     data = float(data[0])

        if self._unit is not None:
            return WaveForm.from_unit_values(self.simplified_name, self._unit(data), abscissa=abscissa)
        else:
            return WaveForm.from_array(self.simplified_name, data, abscissa=abscissa)

####################################################################################################

class RawFileAbc:

    """ This class parse the stdout of ngspice and the raw data output.
    """

    _logger = _module_logger.getChild('RawFileAbc')

    _variable_cls: VariableAbc

    ##############################################

    def __init__(self) -> None:
        self._simulation: Simulation | None
        self.flags: str
        self.number_of_points: int
        self.number_of_variables: int
        self.plot_name: str

    ##############################################

    def fix_case(self) -> None:
        raise NotImplementedError

    ##############################################

    @property
    def simulation(self) -> Simulation:
        if self._simulation is not None:
            return self._simulation
        else:
            raise NameError('Simulation is undefined')

    @simulation.setter
    def simulation(self, value: Simulation):
        self._simulation = value

    ##############################################

    @property
    def circuit(self) -> Circuit:
        return self.simulation.circuit

    ##############################################

    _name_to_unit = {
        'time': u_s,
        'voltage': u_V,
        'current': u_A,
        'frequency': u_Hz,
    }

    ##############################################

    def _read_line(self, header_line_iterator: Iterator[bytes]) -> str:
        """ Return the next line """
        # Fixme: self._header_line_iterator, etc.
        # skip empty line
        line = None
        while not line:
            line = next(header_line_iterator)
        return line.decode('utf-8')

    ##############################################

    def _read_header_line(self, header_line_iterator: Iterator[bytes], head_line: str) -> str:
        """ Read an header line and check it starts with *head_line*. """
        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if line.startswith(head_line):
            return line
        else:
            raise NameError(f"Unexpected line: {line}")

    ##############################################

    def _read_header_field_line(self, header_line_iterator: Iterator[bytes], expected_label: str) -> str:
        """ Read an header line and check it starts with *expected_label* and colon.

        Return the values next to the label.
        """
        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        # a title can have ': ' after 'title: '
        location = line.find(': ')  # first occurence
        label, value = line[:location], line[location + 2:]
        if label != expected_label:
            raise NameError(f"Expected label '{label}' instead of '{expected_label}'")
        return value.strip()

    ##############################################

    def _read_header_section_line(self, header_line_iterator: Iterator[bytes], expected_label: str) -> str:
        """ Read an header line and check it starts with *expected_label*.

        Return the line.
        """
        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if not line.startswith(expected_label):
            raise NameError(f"Expected section '{line}' instead of '{expected_label}'")
        return line

    ##############################################

    def _read_temperature_line(self, header_line_iterator: Iterator[bytes]) -> tuple[u_Degree, u_Degree]:
        # Doing analysis at TEMP = 25.000000 and TNOM = 25.000000
        line = self._read_header_line(header_line_iterator, 'Doing analysis at TEMP')
        pattern1 = 'TEMP = '
        pattern2 = ' and TNOM = '
        pos1 = line.find(pattern1)
        pos2 = line.find(pattern2)
        if pos1 != -1 and pos2 != -1:
            part1 = line[pos1 + len(pattern1):pos2]
            part2 = line[pos2 + len(pattern2):].strip()
            temperature = u_Degree(float(part1))
            nominal_temperature = u_Degree(float(part2))
        else:
            temperature = None
            nominal_temperature = None
        return temperature, nominal_temperature

    ##############################################

    def _read_header_variables(self, header_line_iterator: Iterator[bytes]) -> None:
        self.variables = {}
        for _ in range(self.number_of_variables):
            line = (next(header_line_iterator)).decode('utf-8')
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            #  unit = time, voltage, current
            unit = self._name_to_unit[unit]  # convert to Unit
            self.variables[name] = self._variable_cls(index, name, unit)  # ty: ignore[call-non-callable]
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

    ##############################################

    def _read_variable_data(self, raw_data: bytes) -> None:
        """ Read the raw data and set the variable values. """
        match self.flags:
            case 'real':
                number_of_columns = self.number_of_variables
            case 'complex':
                number_of_columns = 2 * self.number_of_variables
            case _:
                raise NotImplementedError

        input_data = np.frombuffer(raw_data, count=number_of_columns * self.number_of_points, dtype='f8')
        input_data = input_data.reshape((self.number_of_points, number_of_columns))
        input_data = input_data.transpose()
        # np.savetxt('raw.txt', input_data)
        if self.flags == 'complex':
            _ = input_data
            input_data = np.array(_[0::2], dtype='complex128')
            input_data.imag = _[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]

    ##############################################

    def nodes(self, to_float: bool = False, abscissa=None) -> list[WaveForm]:
        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_voltage_node()]

    ##############################################

    def branches(self, to_float: bool = False, abscissa=None) -> list[WaveForm]:
        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_branch_current()]

    ##############################################

    def internal_parameters(self, to_float: bool = False, abscissa=None) -> list[WaveForm]:
        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_interval_parameter]

    ##############################################

    def elements(self, abscissa=None) -> list[WaveForm]:
        return [variable.to_waveform(abscissa, to_float=True)
                for variable in self.variables.values()]

    ##############################################

    def to_analysis(self):
        self.fix_case()
        match self.plot_name:
            case 'Operating Point':
                return self._to_operating_point_analysis()
            case 'Sensitivity Analysis':
                return self._to_sensitivity_analysis()
            case 'DC transfer characteristic':
                return self._to_dc_analysis()  # Fixme: 
            case 'AC Analysis':
                return self._to_ac_analysis()
            case 'Transient Analysis':
                return self._to_transient_analysis()
            case _:
                raise NotImplementedError(f"Unsupported plot name '{self.plot_name}'")

    ##############################################

    def _to_operating_point_analysis(self) -> OperatingPoint:
        return OperatingPoint(
            simulation=self.simulation,
            nodes=self.nodes(to_float=True),
            branches=self.branches(to_float=True),
        )

    ##############################################

    def _to_sensitivity_analysis(self) -> SensitivityAnalysis:
        # Fixme: test .SENS I (VTEST)
        # Fixme: separate v(vinput), analysis.R2.m
        return SensitivityAnalysis(
            simulation=self.simulation,
            elements=self.elements(),
        )  # Fixme:

    ##############################################

    def _to_dc_analysis(self, sweep_variable) -> DcAnalysis:
        sweep = sweep_variable.to_waveform()
        return DcAnalysis(
            simulation=self.simulation,
            sweep=sweep,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_ac_analysis(self) -> AcAnalysis:
        frequency = self.variables['frequency'].to_waveform(to_real=True)
        return AcAnalysis(
            simulation=self.simulation,
            frequency=frequency,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_transient_analysis(self) -> TransientAnalysis:
        time = self.variables['time'].to_waveform(to_real=True)
        return TransientAnalysis(
            simulation=self.simulation,
            time=time,
            nodes=self.nodes(abscissa=time),
            branches=self.branches(abscissa=time),
            internal_parameters=self.internal_parameters(),
        )
