####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

import logging
import numpy as np
import re

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

        self.index = index
        self.name = name
        self.unit = unit

    ##############################################

    def __repr__(self):

        return 'variable[{self.index}]: {self.name} [{self.unit}]'.format(self=self)

####################################################################################################

class RawFile(object):

    """

    Public Attributes:

      :attr:`circuit`

      :attr:`data`

      :attr:`date`

      :attr:`flags`

      :attr:`number_of_points`

      :attr:`number_of_variables`

      :attr:`plot_name`

      :attr:`temperature`

      :attr:`title`

      :attr:`variables`

    """

    _logger = _module_logger.getChild('RawFile')

    ##############################################

    def __init__(self, stdout, stderr):

        match = re.match(r'@@@ (\d+) (\d+)', stderr)
        if match is not None:
            self.number_of_points = int(match.group(2))
        else:
            raise NameError("Cannot decode the number of points")

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
            index, name, unit = [x.strip() for x in line.split('\t') if x]
            self.variables.append(WaveFormVariable(index, name, unit))
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

        # dtype = {}
        # for variable in enumerate(self.variables):
        # (name, offset, title)
        #     dtype[variable.name] = ('f8', 0, '{} [{}]'.format(variable.name, variable.unit))
        dtype = [(variable.name, 'f8') for variable in self.variables]
        self.data = np.zeros(self.number_of_points, dtype=dtype)
        # Fixme: simpler way
        input_data = np.fromstring(raw_data, count=self.number_of_variables*self.number_of_points, dtype='f8')
        input_data = input_data.reshape((self.number_of_points, self.number_of_variables))
        input_data = input_data.transpose()
        # self.data[:] = input_data # don't work
        # ValueError: could not broadcast input array from shape (2023,5) into shape (2023)
        for variable in self.variables:
            self.data[variable.name] = input_data[variable.index,:]
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
