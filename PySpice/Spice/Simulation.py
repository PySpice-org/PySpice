####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

from ..Tools.StringTools import join_list

####################################################################################################

class CircuitSimulation(object):

    ##############################################

    def __init__(self, circuit,
                 temperature=27,
                 nominal_temperature=27,
                 pipe=True,
                ):

        self._circuit = circuit

        self._options = {} # .options
        self._saved_nodes = ()
        self._analysis_parameters = {}

        self.temperature = temperature
        self.nominal_temperature = nominal_temperature

        if pipe:
            self.options('NOINIT')
            self.options(filetype='binary')

    ##############################################

    @property
    def circuit(self):
        return self._circuit

    ##############################################

    def options(self, *args, **kwargs):

        for item in args:
            self._options[str(item)] = None
        for key, value in kwargs.iteritems():
            self._options[str(key)] = str(value)

    ##############################################

    @property
    def temperature(self):
        return self._options['TEMP']

    @temperature.setter
    def temperature(self, value):
        self._options['TEMP'] = value

    ##############################################

    @property
    def nominal_temperature(self):
        return self._options['TNOM']

    @nominal_temperature.setter
    def nominal_temperature(self, value):
        self._options['TNOM'] = value

    ##############################################

    def save(self, *args):

        self._saved_nodes = list(args)

    ##############################################

    def operating_point(self):

        self._analysis_parameters['op'] = ''

    ##############################################

    def dc_sensitivity(self, output_variable):

        """
        .sens outvar

        .sens outvar ac dec nd fstart fstop
        .sens outvar ac oct no fstart fstop
        .sens outvar ac lin np fstart fstop
        """

        self._analysis_parameters['sens'] = (output_variable,)

    ##############################################

    def dc(self, **kwargs):

        """ .dc srcnam vstart vstop vincr [ src2 start2 stop2 incr2 ] """

        parameters = []
        for source_name, voltage_slice in kwargs.iteritems():
            parameters += [source_name, voltage_slice.start, voltage_slice.stop, voltage_slice.step]
        self._analysis_parameters['dc'] = parameters

    ##############################################

    def ac(self, start_frequency, stop_frequency, number_of_points, variation):

        # fixme: concise keyword ?

        """
        .ac dec nd fstart fstop
        .ac oct no fstart fstop
        .ac lin np fstart fstop
        """

        if variation not in ('dec', 'oct', 'lin'):
            raise ValueError("Incorrect variation type")

        self._analysis_parameters['ac'] = (variation, number_of_points, start_frequency, stop_frequency)

    ##############################################

    def transient(self, step_time, end_time, start_time=None, max_time=None,
                  use_initial_condition=False):

        """
        .tran tstep tstop <tstart <tmax>> <uic>
        """

        if use_initial_condition:
            uic = 'uic'
        else:
            uic = None
        self._analysis_parameters['tran'] = (step_time, end_time, start_time, max_time, uic)

    ##############################################

    def __str__(self):

        netlist = str(self._circuit)
        if self.options:
            for key, value in self._options.iteritems():
                if value is not None:
                    netlist += '.options {} = {}\n'.format(key, value)
                else:
                    netlist += '.options {}\n'.format(key)
        if self._saved_nodes:
            netlist += '.save ' + join_list(self._saved_nodes) + '\n'
        for analysis, analysis_parameters in self._analysis_parameters.iteritems():
            netlist += '.' + analysis + ' ' + join_list(analysis_parameters) + '\n'
        return netlist

####################################################################################################
# 
# End
# 
####################################################################################################
