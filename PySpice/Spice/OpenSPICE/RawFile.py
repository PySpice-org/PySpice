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

    def __init__(self, output):

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
        self.number_of_points = int(self._read_header_field_line(header_line_iterator, 'No. Points'))
        self._read_header_field_line(header_line_iterator, 'Variables')
        self._read_header_variables(header_line_iterator)

        return raw_data

    ##############################################

    def fix_case(self):

        """ Ngspice return lower case names. This method fixes the case of the variable names. """

        circuit = self.circuit
        element_translation = {element.upper():element for element in circuit.element_names}
        node_translation = {node.upper():node for node in circuit.node_names}
        for variable in self.variables.values():
            variable.fix_case(element_translation, node_translation)

    ##############################################

    def _to_dc_analysis(self):

        if 'sweep' in self.variables:
            sweep_variable = self.variables['sweep']
        else:
            raise NotImplementedError

        return super()._to_dc_analysis(sweep_variable)
