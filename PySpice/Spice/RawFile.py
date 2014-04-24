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

    """ This class implements a variable or probe in a Spice simulation output.

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

    @property
    def simplified_name(self):

        if self.is_node_voltage() or self.is_branch_current():
            return self.name[2:-1]
        else:
            return self.name

    ##############################################

    def to_waveform(self, abscissa=None, to_real=False, to_float=False):

        data = self.data
        if to_real:
            data = data.real
        if to_float:
            data = float(data[0])

        return WaveForm(self.simplified_name, self.unit, data, abscissa=abscissa)

####################################################################################################

class RawFile(object):

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

    """

    _logger = _module_logger.getChild('RawFile')

    ##############################################

    def __init__(self, stdout, number_of_points):

        self.number_of_points = number_of_points

        raw_data = self._read_header(stdout)
        self._read_variable_data(raw_data)
        # self._to_analysis()

    ##############################################

    def _read_header(self, stdout):

        """ Parse the header """

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

        return raw_data

    ##############################################
        
    def _read_line(self, header_line_iterator):

        """ Return the next line """

        # Fixme: self._header_line_iterator, etc.

        line = None
        while not line:
            line = header_line_iterator.next()
        return line

    ##############################################
        
    def _read_header_line(self, header_line_iterator, head_line):

        """ Read an header line and check it starts with *head_line*. """

        line = self._read_line(header_line_iterator)
        self._logger.debug(line)
        if not line.startswith(head_line):
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
        if self.flags == 'complex':
            raw_data = input_data
            input_data = np.array(raw_data[0::2], dtype='complex64')
            input_data.imag = raw_data[1::2]
        for variable in self.variables.itervalues():
            variable.data = input_data[variable.index]

    ##############################################

    def nodes(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float) 
                for variable in self.variables.itervalues()
                if variable.is_node_voltage()]

    ##############################################

    def branches(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.variables.itervalues()
                if variable.is_branch_current()]

    ##############################################

    def elements(self, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=True) 
                for variable in self.variables.itervalues()]

    ##############################################

    def to_analysis(self):

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

        return OperatingPoint(nodes=self.nodes(to_float=True), branches=self.branches(to_float=True))

    ##############################################

    def _to_sensitivity_analysis(self):

        # Fixme: separate v(vinput), analysis.R2.m
        return SensitivityAnalysis(elements=self.elements())

    ##############################################

    def _to_dc_analysis(self):

        v_sweep = self.variables['v(v-sweep)'].to_waveform()
        return DcAnalysis(v_sweep, nodes=self.nodes(), branches=self.branches())
        
    ##############################################

    def _to_ac_analysis(self):

        frequency = self.variables['frequency'].to_waveform(to_real=True)
        return AcAnalysis(frequency, nodes=self.nodes(), branches=self.branches())
        
    ##############################################

    def _to_transient_analysis(self):

        time = self.variables['time'].to_waveform(to_real=True)
        return TransientAnalysis(time, nodes=self.nodes(abscissa=time), branches=self.branches(abscissa=time))

####################################################################################################
# 
# End
# 
####################################################################################################
