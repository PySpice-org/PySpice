####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
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

####################################################################################################

import os

####################################################################################################

"""This module provide tools to read raw output.
"""

####################################################################################################

from PySpice.Unit import u_Degree, u_V, u_A, u_s, u_Hz

####################################################################################################

import logging
import numpy as np

####################################################################################################

from PySpice.Probe.WaveForm import (OperatingPoint, SensitivityAnalysis,
                                    DcAnalysis, AcAnalysis, TransientAnalysis,
                                    WaveForm)

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

    def __init__(self, index, name, unit):

        # Fixme: self._ ?

        self._index = int(index)
        self.name = str(name)
        self._unit = unit # could be guessed from name also for voltage node and branch current
        self.data = None

    ##############################################

    @property
    def index(self):
        return self._index

    # @property
    # def name(self):
    #     return self._name

    # @name.setter
    # def name(self, value):
    #     self._name = value

    ##############################################

    def __repr__(self):
        return 'variable[{0._index}]: {0.name} [{0._unit}]'.format(self)

    ##############################################

    def is_voltage_node(self):
        raise NotImplementedError

    ##############################################

    def is_branch_current(self):
        raise NotImplementedError

    ##############################################

    @property
    def is_interval_parameter(self):
        return self.name.startswith('@') # Fixme: Xyce ???

    ##############################################

    @staticmethod
    def to_voltage_name(node):
        return 'v({})'.format(node)

    ##############################################

    @staticmethod
    def to_branch_name(element):
        return 'i({})'.format(element)

    ##############################################

    def fix_case(self, element_translation, node_translation):

        """ Update the name to the right case. """

        if self.is_branch_current():
            if self.simplified_name in element_translation:
                self.name = self.to_branch_name(element_translation[self.simplified_name])
        elif self.is_voltage_node():
            if self.simplified_name in node_translation:
                self.name = self.to_voltage_name(node_translation[self.simplified_name])

    ##############################################

    @property
    def simplified_name(self):
        raise NotImplementedError

    ##############################################

    def to_waveform(self, abscissa=None, to_real=False, to_float=False):

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

    ##############################################

    @property
    def simulation(self):

        if self._simulation is not None:
            return self._simulation
        else:
            raise NameError('Simulation is undefined')

    @simulation.setter
    def simulation(self, value):
        self._simulation = value

    ##############################################

    @property
    def circuit(self):
        return self._simulation.circuit

    ##############################################

    _name_to_unit = {
        'time': u_s,
        'voltage': u_V,
        'current': u_A,
        'frequency': u_Hz,
    }

    ##############################################

    def _read_line(self, header_line_iterator):

        """ Return the next line """

        # Fixme: self._header_line_iterator, etc.

        line = None
        while not line:
            line = next(header_line_iterator)
        return line.decode('utf-8')

    ##############################################

    def _read_header_line(self, header_line_iterator, head_line):

        """ Read an header line and check it starts with *head_line*. """

        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if line.startswith(head_line):
            return line
        else:
            raise NameError("Unexpected line: %s" % (line))

    ##############################################

    def _read_header_field_line(self, header_line_iterator, expected_label, has_value=True):

        """ Read an header line and check it starts with *expected_label*.

        Return the values next to the label if the flag *has_value* is set.
        """

        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if has_value:
            # a title can have ': ' after 'title: '
            location = line.find(': ') # first occurence
            label, value = line[:location], line[location+2:]
        else:
            label = line[:-1]
        if label != expected_label:
            raise NameError("Expected label %s instead of %s" % (expected_label, label))
        if has_value:
            return value.strip()

    ##############################################

    def _read_temperature_line(self, header_line_iterator):

        # Doing analysis at TEMP = 25.000000 and TNOM = 25.000000

        line = self._read_header_line(header_line_iterator, 'Doing analysis at TEMP')
        pattern1 = 'TEMP = '
        pattern2 = ' and TNOM = '
        pos1 = line.find(pattern1)
        pos2 = line.find(pattern2)
        if pos1 != -1 and pos2 != -1:
            part1 = line[pos1+len(pattern1):pos2]
            part2 = line[pos2+len(pattern2):].strip()
            temperature = u_Degree(float(part1))
            nominal_temperature = u_Degree(float(part2))
        else:
            temperature = None
            nominal_temperature = None
        return temperature, nominal_temperature

    ##############################################

    def _read_header_variables(self, header_line_iterator):

        self.variables = {}
        for i in range(self.number_of_variables):
            line = (next(header_line_iterator)).decode('utf-8')
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            #  unit = time, voltage, current
            unit = self._name_to_unit[unit] # convert to Unit
            self.variables[name] = self._variable_cls(index, name, unit)
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

    ##############################################

    def _read_variable_data(self, raw_data):

        """ Read the raw data and set the variable values. """

        if self.flags == 'real':
            number_of_columns = self.number_of_variables
        elif self.flags == 'complex':
            number_of_columns = 2*self.number_of_variables
        else:
            raise NotImplementedError

        input_data = np.fromstring(raw_data, count=number_of_columns*self.number_of_points, dtype='f8')
        input_data = input_data.reshape((self.number_of_points, number_of_columns))
        input_data = input_data.transpose()
        # np.savetxt('raw.txt', input_data)
        if self.flags == 'complex':
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex128')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]

    ##############################################

    def nodes(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_voltage_node()]

    ##############################################

    def branches(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_branch_current()]

    ##############################################

    def internal_parameters(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.values()
                if variable.is_interval_parameter]

    ##############################################

    def elements(self, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=True)
                for variable in self.variables.values()]

    ##############################################

    def to_analysis(self):

        self.fix_case()

        if self.plot_name == 'Operating Point':
            return self._to_operating_point_analysis()
        elif self.plot_name == 'Sensitivity Analysis':
            return self._to_sensitivity_analysis()
        elif self.plot_name == 'DC transfer characteristic':
            return self._to_dc_analysis()
        elif self.plot_name == 'AC Analysis':
            return self._to_ac_analysis()
        elif self.plot_name == 'Transient Analysis':
            return self._to_transient_analysis()
        else:

            raise NotImplementedError("Unsupported plot name {}".format(self.plot_name))

    ##############################################

    def _to_operating_point_analysis(self):

        return OperatingPoint(
            simulation=self.simulation,
            nodes=self.nodes(to_float=True),
            branches=self.branches(to_float=True),
        )

    ##############################################

    def _to_sensitivity_analysis(self):

        # Fixme: test .SENS I (VTEST)
        # Fixme: separate v(vinput), analysis.R2.m
        return SensitivityAnalysis(
            simulation=self.simulation,
            elements=self.elements(),
        )

    ##############################################

    def _to_dc_analysis(self, sweep_variable):

        sweep = sweep_variable.to_waveform()
        return DcAnalysis(
            simulation=self.simulation,
            sweep=sweep,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_ac_analysis(self):

        frequency = self.variables['frequency'].to_waveform(to_real=True)
        return AcAnalysis(
            simulation=self.simulation,
            frequency=frequency,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_transient_analysis(self):

        time = self.variables['time'].to_waveform(to_real=True)
        return TransientAnalysis(
            simulation=self.simulation,
            time=time,
            nodes=self.nodes(abscissa=time),
            branches=self.branches(abscissa=time),
            internal_parameters=self.internal_parameters(),
        )
