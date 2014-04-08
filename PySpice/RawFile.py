####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

import logging
import numpy as np

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class WaveFormVariable(object):

    """

    Public Attributes:

      :attr:`index`

      :attr:`name`

      :attr:`unit`

    """

    ##############################################

    def __init__(self, index, name, unit):

        self.index = int(index)
        self.name = str(name)
        self.unit = str(unit)

    ##############################################

    def __repr__(self):

        return 'variable[{self.index}]: {self.name} [{self.unit}]'.format(self=self)

####################################################################################################

class RawFile(object):

    """

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

    """

    _logger = _module_logger.getChild('RawFile')

    ##############################################

    def __init__(self, stdout, number_of_points):

        self.number_of_points = number_of_points

        binary_line = 'Binary:\n'
        binary_location = stdout.find(binary_line)
        if binary_line < 0:
            raise NameError('Cannot locate binary data')
        header_lines = stdout[:binary_location].splitlines()
        raw_data = stdout[binary_location + len(binary_line):]
        header_line_iterator = iter(header_lines)

        self.circuit = self._read_header_field_line(header_line_iterator, 'Circuit')
        self.temperature = self._read_header_line(header_line_iterator, 'Doing analysis at TEMP')
        self.title = self._read_header_field_line(header_line_iterator, 'Title')
        self.date = self._read_header_field_line(header_line_iterator, 'Date')
        self.plot_name = self._read_header_field_line(header_line_iterator, 'Plotname')
        self.flags = self._read_header_field_line(header_line_iterator, 'Flags')
        self.number_of_variables = int(self._read_header_field_line(header_line_iterator, 'No. Variables'))
        self._read_header_field_line(header_line_iterator, 'No. Points')
        self._read_header_field_line(header_line_iterator, 'Variables', has_value=False)
        self._read_header_field_line(header_line_iterator, 'No. of Data Columns ')
        self.variables = []
        for i in xrange(self.number_of_variables):
            line = header_line_iterator.next()
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            self.variables.append(WaveFormVariable(index, name, unit))
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

        # dtype = {}
        # for variable in enumerate(self.variables):
        # (name, offset, title)
        #     dtype[variable.name] = ('f8', 0, '{} [{}]'.format(variable.name, variable.unit))
        if self.flags == 'real':
            dtype = 'f8' # 64-bit float
            number_of_columns = self.number_of_variables
        elif self.flags == 'complex':
            dtype = np.complex64
            number_of_columns = self.number_of_variables * 2
        else:
            raise NotImplementedError
        data_dtype = [(variable.name, dtype) for variable in self.variables]
        self.data = np.zeros(self.number_of_points, dtype=data_dtype)

        # Fixme: simpler way
        self._logger.debug("Raw data is {} bytes and {} number of points".format(len(raw_data), self.number_of_points))
        input_data = np.fromstring(raw_data, count=number_of_columns*self.number_of_points, dtype='f8')
        input_data = input_data.reshape((self.number_of_points, number_of_columns))
        # self._logger.debug(str(input_data.shape) + '\n' + str(input_data))
        input_data = input_data.transpose()
        # self.data[:] = input_data # don't work
        # ValueError: could not broadcast input array from shape (2023,5) into shape (2023)
        for variable in self.variables:
            if self.flags == 'real':
                column_index = variable.index
                variable_data = input_data[column_index,:]
            elif self.flags == 'complex':
                column_index = variable.index * 2
                variable_data = input_data[column_index,:] + input_data[column_index+1,:]*1j
            self.data[variable.name] = variable_data
        # for i in xrange(self.number_of_points):
        #    self.data[i] = tuple(input_data[i,:])

    ##############################################
        
    def _read_line(self, header_line_iterator):

        line = None
        while not line:
            line = header_line_iterator.next()

        return line

    ##############################################
        
    def _read_header_line(self, header_line_iterator, head_line):

        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if not line.startswith(head_line):
            raise NameError("Unexpected line: %s" % (line))

    ##############################################
        
    def _read_header_field_line(self, header_line_iterator, expected_label, has_value=True):

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

####################################################################################################
# 
# End
# 
####################################################################################################
