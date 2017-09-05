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

####################################################################################################

import os

####################################################################################################

"""This module provide tools to read the output of Ngspice.

Header

.. code::

    Circuit: 230V Rectifier

    Doing analysis at TEMP = 25.000000 and TNOM = 25.000000

    Title: 230V Rectifier
    Date: Thu Jun  4 23:40:58  2015
    Plotname: Transient Analysis
    Flags: real
    No. Variables: 6
    No. Points: 0
    Variables:
    No. of Data Columns : 6
            0       time    time
            1       v(in)   voltage
            ...
            5       i(vinput)       current
    Binary:

Operating Point
Node voltages and source branch currents:

 * v(node_name)
 * i(vname)

Sensitivity Analysis

 * v({element})
 * v({element}_{parameter})
 * v(v{source})

DC

 * v(v-sweep)
 * v({node})
 * i(v{source})

AC
Frequency, node voltages and source branch currents:

 * frequency
 * v({node})
 * i(v{name})

Transient Analysis
Time, node voltages and source branch currents:

 * time
 * v({node})
 * i(v{source})

"""

# * v({element}:bv_max)
# * i(e.xdz1.ev1)

####################################################################################################

from ..Unit import u_Degree, U_V, U_A, U_s, U_Hz

####################################################################################################

import logging
import numpy as np

####################################################################################################

from ..Probe.WaveForm import (OperatingPoint, SensitivityAnalysis,
                              DcAnalysis, AcAnalysis, TransientAnalysis,
                              WaveForm)

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: self._

class Variable:

    """This class implements a variable or probe in a SPICE simulation output.

    Public Attributes:

      :attr:`index`
        index in the array

      :attr:`name`

      :attr:`unit`

    """

    ##############################################

    def __init__(self, index, name, unit):

        self.index = int(index)
        self.name = str(name)
        self.unit = unit # could be guessed from name also for voltage node and branch current
        self.data = None

    ##############################################

    def __repr__(self):
        return 'variable[{0.index}]: {0.name} [{0.unit}]'.format(self)

    ##############################################

    def is_voltage_node(self):
        return self.name.startswith('v(')

    ##############################################

    def is_branch_current(self):
        # source branch current
        return self.name.startswith('i(')

    ##############################################

    @staticmethod
    def to_voltage_name(node):
        return 'v({})'.format(node)

    ##############################################

    @staticmethod
    def to_branch_name(element):
        return 'i({})'.format(element)

    ##############################################

    @property
    def simplified_name(self):

        if self.is_voltage_node() or self.is_branch_current():
            return self.name[2:-1]
        else:
            return self.name

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

    def to_waveform(self, abscissa=None, to_real=False, to_float=False):

        """ Return a :obj:`PySpice.Probe.WaveForm` instance. """

        data = self.data
        if to_real:
            data = data.real
        if to_float:
            data = float(data[0])

        return WaveForm(self.simplified_name, self.unit, data, abscissa=abscissa)

####################################################################################################

class RawFile:

    """ This class parse the stdout of ngspice and the raw data output.

    Public Attributes:

      :attr:`circuit`
        same as title

      :attr:`data`

      :attr:`date`

      :attr:`flags`
        'real' or 'complex'

      :attr:`number_of_points`

      :attr:`number_of_variables`

      :attr:`plot_name`
        AC Analysis, Operating Point, Sensitivity Analysis, DC transfer characteristic

      :attr:`temperature`

      :attr:`title`

      :attr:`variables`

      :attr:`warnings`

    """

    _logger = _module_logger.getChild('RawFile')

    ##############################################

    def __init__(self, stdout, number_of_points):

        self.number_of_points = number_of_points

        raw_data = self._read_header(stdout)
        self._read_variable_data(raw_data)
        # self._to_analysis()

        self._simulation = None

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

    __name_to_unit__ = {
        'time': U_s,
        'voltage': U_V,
        'current': U_A,
        'frequency': U_Hz,
    }

    ##############################################

    def _read_header(self, stdout):

        """ Parse the header """

        binary_line = b'Binary:' + os.linesep.encode('ascii')
        binary_location = stdout.find(binary_line)
        if binary_location < 0:
            raise NameError('Cannot locate binary data')
        raw_data_start = binary_location + len(binary_line)
        # self._logger.debug(os.linesep + stdout[:raw_data_start].decode('utf-8'))
        header_lines = stdout[:binary_location].splitlines()
        raw_data = stdout[raw_data_start:]
        header_line_iterator = iter(header_lines)

        self.circuit_name = self._read_header_field_line(header_line_iterator, 'Circuit')
        self.temperature, self.nominal_temperature = self._read_temperature_line(header_line_iterator)
        self.warnings = [self._read_header_field_line(header_line_iterator, 'Warning')
                         for i in range(stdout.count(b'Warning'))]
        for warning in self.warnings:
            self._logger.warn(warning)
        self.title = self._read_header_field_line(header_line_iterator, 'Title')
        self.date = self._read_header_field_line(header_line_iterator, 'Date')
        self.plot_name = self._read_header_field_line(header_line_iterator, 'Plotname')
        self.flags = self._read_header_field_line(header_line_iterator, 'Flags')
        self.number_of_variables = int(self._read_header_field_line(header_line_iterator, 'No. Variables'))
        self._read_header_field_line(header_line_iterator, 'No. Points')
        self._read_header_field_line(header_line_iterator, 'Variables', has_value=False)
        self._read_header_field_line(header_line_iterator, 'No. of Data Columns ')
        self.variables = {}
        for i in range(self.number_of_variables):
            line = (next(header_line_iterator)).decode('utf-8')
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            #  unit = time, voltage, current
            unit = self.__name_to_unit__[unit] # convert to Unit
            self.variables[name] = Variable(index, name, unit)
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

        return raw_data

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
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]

    ##############################################

    def fix_case(self):

        """ Ngspice return lower case names. This method fixes the case of the variable names. """

        circuit = self.circuit
        element_translation = {element.lower():element for element in circuit.element_names()}
        node_translation = {node.lower():node for node in circuit.node_names()}
        for variable in self.variables.values():
            variable.fix_case(element_translation, node_translation)

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

    def _to_dc_analysis(self):

        if 'v(v-sweep)' in self.variables:
            sweep_variable = self.variables['v(v-sweep)']
        elif 'v(i-sweep)' in self.variables:
            sweep_variable = self.variables['v(i-sweep)']
        else:
            #
            raise NotImplementedError
        sweep = sweep_variable.to_waveform()
        return DcAnalysis(
            simulation=self.simulation,
            sweep=sweep,
            nodes=self.nodes(),
            branches=self.branches(),
        )

    ##############################################

    def _to_ac_analysis(self):

        frequency = self.variables['frequency'].to_waveform(to_real=True)
        return AcAnalysis(
            simulation=self.simulation,
            frequency=frequency,
            nodes=self.nodes(),
            branches=self.branches(),
        )

    ##############################################

    def _to_transient_analysis(self):

        time = self.variables['time'].to_waveform(to_real=True)
        return TransientAnalysis(
            simulation=self.simulation,
            time=time,
            nodes=self.nodes(abscissa=time),
            branches=self.branches(abscissa=time),
        )
