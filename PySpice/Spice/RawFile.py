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

from ..Probe.WaveForm import (OperatingPoint, SensitivityAnalysis,
                              DcAnalysis, AcAnalysis, TransientAnalysis,
                              WaveForm)

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Variable(object):

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
        self.data = None

    ##############################################

    def __repr__(self):

        return 'variable[{self.index}]: {self.name} [{self.unit}]'.format(self=self)

    ##############################################

    def is_node_voltage(self):

        return self.name.startswith('v(')

    ##############################################

    def is_branch_current(self):

        return self.name.startswith('i(')

    ##############################################

    def to_waveform(self, to_real=False, to_float=False):

        data = self.data
        if to_real:
            data = data.real
        if to_float:
            data = float(data[0])

        if self.is_node_voltage() or self.is_branch_current():
            name = self.name[2:-1]
        else:
            name = self.name

        return WaveForm(name, self.unit, data)

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
        self.variables = {}
        for i in xrange(self.number_of_variables):
            line = header_line_iterator.next()
            self._logger.debug(line)
            items = [x.strip() for x in line.split('\t') if x]
            # 0 frequency frequency grid=3
            index, name, unit = items[:3]
            self.variables[name] = Variable(index, name, unit)
        # self._read_header_field_line(header_line_iterator, 'Binary', has_value=False)

        if self.flags == 'real':
            number_of_columns = self.number_of_variables
        elif self.flags == 'complex':
            number_of_columns = 2*self.number_of_variables
        else:
            raise NotImplementedError

        input_data = np.fromstring(raw_data, count=number_of_columns*self.number_of_points, dtype='f8')
        input_data = input_data.reshape((self.number_of_points, number_of_columns))
        input_data = input_data.transpose()
        if self.flags == 'complex':
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.itervalues():
            variable.data = input_data[variable.index]

        if self.plot_name == 'Operating Point':
            self._operating_point_analysis()
        elif self.plot_name == 'Sensitivity Analysis':
            self._sensitivity_analysis()
        elif self.plot_name == 'DC transfer characteristic':
            self._dc_analysis()
        elif self.plot_name == 'AC Analysis':
            self._ac_analysis()
        elif self.plot_name == 'Transient Analysis':
            self._transient_analysis()
        else:
            raise NotImplementedError("Unsupported plot name {}".format(self.plot_name))

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

    ##############################################

    def _nodes(self, to_float=False):

        return [variable.to_waveform(to_float=to_float) 
                for variable in self.variables.itervalues()
                if variable.is_node_voltage()]

    ##############################################

    def _branches(self, to_float=False):

        return [variable.to_waveform(to_float=to_float)
                for variable in self.variables.itervalues()
                if variable.is_branch_current()]

    ##############################################

    def _elements(self):

        return [variable.to_waveform(to_float=True) 
                for variable in self.variables.itervalues()]

    ##############################################

    def _operating_point_analysis(self):

        self.analysis = OperatingPoint(nodes=self._nodes(to_float=True),
                                       branches=self._branches(to_float=True))

    ##############################################

    def _sensitivity_analysis(self):

        # Fixme: separate v(vinput), analysis.R2.m
        self.analysis = SensitivityAnalysis(elements=self._elements())

    ##############################################

    def _dc_analysis(self):

        self.analysis = DcAnalysis(v_sweep=self.variables['v(v-sweep)'].to_waveform(),
                                   nodes=self._nodes(), branches=self._branches())
        
    ##############################################

    def _ac_analysis(self):

        self.analysis = AcAnalysis(frequency=self.variables['frequency'].to_waveform(to_real=True),
                                   nodes=self._nodes(), branches=self._branches())
        
    ##############################################

    def _transient_analysis(self):

        self.analysis = TransientAnalysis(time=self.variables['time'].to_waveform(to_real=True),
                                          nodes=self._nodes(), branches=self._branches())

####################################################################################################
# 
# End
# 
####################################################################################################
