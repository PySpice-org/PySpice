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
import numpy as np

from ..RawFile import VariableAbc, RawFileAbc

####################################################################################################

"""This module provide tools to read the output of Xyce.

Header

"""

####################################################################################################

import logging

####################################################################################################

_module_logger = logging.getLogger(__name__)


####################################################################################################

class Variable(VariableAbc):

    ##############################################

    def is_voltage_node(self):

        name = self.name.lower()
        return name.startswith('v(') or not self.is_branch_current()

    ##############################################

    def is_branch_current(self):
        return self.name.endswith('#branch')

    ##############################################

    @staticmethod
    def to_voltage_name(node):
        return 'v({})'.format(node)

    ##############################################

    @property
    def simplified_name(self):

        name = self.name
        if len(name) > 1 and name[1] == '(':
            return name[2:-1]
        elif name.endswith('#branch'):
            return name[:-7]
        elif '#' in name:
            # Xyce change name of type "output_plus" to "OUTPUT#PLUS"
            return name.replace('#', '_')
        else:
            return self.name


####################################################################################################

class RawFile(RawFileAbc):
    """ This class parse the stdout of ngspice and the raw data output.

    Public Attributes:

      :attr:`data`

      :attr:`date`

      :attr:`flags`
        'real' or 'complex'

      :attr:`number_of_points`

      :attr:`number_of_variables`

      :attr:`plot_name`
        AC Analysis, Operating Point, Sensitivity Analysis, DC transfer characteristic

      :attr:`title`

      :attr:`variables`

    """

    _logger = _module_logger.getChild('RawFile')

    _variable_cls = Variable

    ##############################################

    def __init__(self, output=None, filename=None):
        if filename:
            binary_line = b'Binary:\n'
            header = b""
            with open(filename, 'rb') as ifile:
                for line in ifile:
                    header += line
                    if line == binary_line:
                        break
                idx = ifile.tell()
            self._read_header(header)
            self._read_file_variable_data(filename, idx)
        else:
            raw_data = self._read_header(output)
            self._read_variable_data(raw_data)
        # self._to_analysis()

        self._simulation = None

    ##############################################

    def _read_header(self, output):

        """ Parse the header """

        # see https://github.com/FabriceSalvaire/PySpice/issues/132
        #   Xyce open the file in binary mode and print using: os << "Binary:" << std::endl;
        #   endl is thus \n
        binary_line = b'Binary:\n'
        binary_location = output.find(binary_line)
        if binary_location < 0:
            raise NameError('Cannot locate binary data')
        raw_data_start = binary_location + len(binary_line)
        self._logger.debug(os.linesep + output[:raw_data_start].decode('utf-8'))
        header_lines = output[:binary_location].splitlines()
        raw_data = output[raw_data_start:]
        header_line_iterator = iter(header_lines)

        self.title = self._read_header_field_line(header_line_iterator, 'Title')
        self.date = self._read_header_field_line(header_line_iterator, 'Date')
        self.plot_name = self._read_header_field_line(header_line_iterator, 'Plotname')
        self.flags = self._read_header_field_line(header_line_iterator, 'Flags')
        self.number_of_variables = int(self._read_header_field_line(header_line_iterator, 'No. Variables'))
        try:
            self.number_of_points = int(self._read_header_field_line(header_line_iterator, 'No. Points'))
        except ValueError:
            self.number_of_points = -1  # Simulation not finished
        self._read_header_field_line(header_line_iterator, 'Variables')
        self._read_header_variables(header_line_iterator)

        return raw_data

    def _read_file_variable_data(self, filename, idx):
        """ Read the raw data and set the variable values. """

        if self.flags == 'real':
            number_of_columns = self.number_of_variables
        elif self.flags == 'complex':
            number_of_columns = 2 * self.number_of_variables
        else:
            raise NotImplementedError

        input_data = np.fromfile(filename,
                                 count=self.number_of_points*self.number_of_variables,
                                 dtype='f8',
                                 offset=idx)

        number_of_rows = input_data.shape[0] // number_of_columns
        input_data = input_data[:number_of_rows * number_of_columns]
        input_data = input_data.reshape((-1, number_of_columns)).transpose()
        if self.flags == 'complex':
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.values():
            variable.data = input_data[variable.index]
        return input_data

    ##############################################

    def fix_case(self):

        """ Ngspice return lower case names. This method fixes the case of the variable names. """

        circuit = self.circuit
        element_translation = {element.upper(): element for element in circuit.element_names}
        node_translation = {node.upper(): node for node in circuit.node_names}
        for variable in self.variables.values():
            variable.fix_case(element_translation, node_translation)

    ##############################################

    def _to_dc_analysis(self):

        if 'sweep' in self.variables:
            sweep_variable = self.variables['sweep']
        else:
            raise NotImplementedError

        return super()._to_dc_analysis(sweep_variable)
