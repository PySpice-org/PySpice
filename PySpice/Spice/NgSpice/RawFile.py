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

from ..RawFile import VariableAbc, RawFileAbc

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

import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: self._

class Variable(VariableAbc):

    ##############################################

    def is_voltage_node(self):
        return self.name.startswith('v(')

    ##############################################

    def is_branch_current(self):
        # source branch current
        return self.name.startswith('i(')

    ##############################################

    @property
    def simplified_name(self):

        if self.is_voltage_node() or self.is_branch_current():
            return self.name[2:-1]
        else:
            return self.name

####################################################################################################

class RawFile(RawFileAbc):

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

    _variable_cls = Variable

    ##############################################

    def __init__(self, stdout, number_of_points):

        self.number_of_points = number_of_points

        raw_data = self._read_header(stdout)
        self._read_variable_data(raw_data)
        # self._to_analysis()

        self._simulation = None

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
        self._read_header_variables(header_line_iterator)

        return raw_data

    ##############################################

    def fix_case(self):

        """ Ngspice return lower case names. This method fixes the case of the variable names. """

        circuit = self.circuit
        element_translation = {element.lower():element for element in circuit.element_names}
        node_translation = {node.lower():node for node in circuit.node_names}
        for variable in self.variables.values():
            variable.fix_case(element_translation, node_translation)

    ##############################################

    def _to_dc_analysis(self):

        if 'v(v-sweep)' in self.variables:
            sweep_variable = self.variables['v(v-sweep)']
        elif 'v(i-sweep)' in self.variables:
            sweep_variable = self.variables['v(i-sweep)']
        else:
            #
            raise NotImplementedError

        return super()._to_dc_analysis(sweep_variable)
