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

import logging

####################################################################################################

from ..Tools.StringTools import join_list, join_dict
from .NgSpice.Shared import NgSpiceShared
from .Server import SpiceServer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class CircuitSimulation(object):

    """Define and generate the spice instruction to perform a circuit simulation.

    .. warning:: In some cases NgSpice can perform several analyses one after the other. This case
    is partially supported.

    """

    _logger = _module_logger.getChild('CircuitSimulation')

    ##############################################

    def __init__(self, circuit,
                 temperature=27,
                 nominal_temperature=27,
                 pipe=True,
                ):

        self._circuit = circuit

        self._options = {} # .options
        self._initial_condition = {} # .ic
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

    def initial_condition(self, **kwargs):

        """ Set initial condition for voltage nodes.

        Usage: initial_condition(node_name1=value, ...)
        """

        for key, value in kwargs.iteritems():
            self._initial_condition['V({})'.format(str(key))] = str(value)

        # Fixme: .nodeset

    ##############################################

    def save(self, *args):

        # Fixme: pass Node for voltage node, Element for source branch current, ...

        """Set the list of saved vectors.

        If no *.save* line is given, then the default set of vectors is saved (node voltages and
        voltage source branch currents). If *.save* lines are given, only those vectors specified
        are saved.

        Node voltages may be saved by giving the node_name or *v(node_name)*. Currents through an
        independent voltage source (including inductor) are given by *i(source_name)* or
        *source_name#branch*. Internal device data are accepted as *@dev[param]*.

        If you want to save internal data in addition to the default vector set, add the parameter
        *all* to the additional vectors to be saved.

        """

        self._saved_nodes = list(args)

    ##############################################

    @property
    def save_currents(self):
        """ Save all currents. """
        return self._options.get('SAVECURRENTS', False)

    @save_currents.setter
    def save_currents(self, value):
        if value:
            self._options['SAVECURRENTS'] = True
        else:
            del self._options['SAVECURRENTS']

    ##############################################

    def reset_analysis(self):

        self._analysis_parameters.clear()

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
        if self.initial_condition:
            netlist += '.ic ' + join_dict(self._initial_condition) + '\n'
        if self._saved_nodes:
            netlist += '.save ' + join_list(self._saved_nodes) + '\n'
        for analysis, analysis_parameters in self._analysis_parameters.iteritems():
            netlist += '.' + analysis + ' ' + join_list(analysis_parameters) + '\n'
        netlist += '.end\n'
        return netlist

####################################################################################################

class CircuitSimulator(CircuitSimulation):

    """ This class implements a circuit simulator. Each analysis mode is performed by a method that
    return the measured probes.

    For *ac* and *transient* analyses, the user must specify a list of nodes using the *probes* key
    argument.
    """

    _logger = _module_logger.getChild('CircuitSimulator')
        
    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        self.reset_analysis()
        if 'probes' in kwargs:
            self.save(* kwargs.pop('probes'))

        method = getattr(CircuitSimulation, analysis_method)
        method(self, *args, **kwargs)

        self._logger.debug('desk\n' + str(self))

    ##############################################

    def operating_point(self, *args, **kwargs):

        return self._run('operating_point', *args, **kwargs)

    ##############################################

    def dc(self, *args, **kwargs):

        return self._run('dc', *args, **kwargs)

    ##############################################

    def dc_sensitivity(self, *args, **kwargs):

        return self._run('dc_sensitivity', *args, **kwargs)

    ##############################################

    def ac(self, *args, **kwargs):

        return self._run('ac', *args, **kwargs)

    ##############################################

    def transient(self, *args, **kwargs):

        return self._run('transient', *args, **kwargs)

####################################################################################################

class SubprocessCircuitSimulator(CircuitSimulator):

    _logger = _module_logger.getChild('SubprocessCircuitSimulator')

    ##############################################

    def __init__(self, circuit,
                 temperature=27,
                 nominal_temperature=27,
                 spice_command='ngspice',
                ):

        # Fixme: kwargs

        super(SubprocessCircuitSimulator, self).__init__(circuit, temperature, nominal_temperature, pipe=True)

        self._spice_server = SpiceServer()

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        super(SubprocessCircuitSimulator, self)._run(analysis_method, *args, **kwargs)

        raw_file = self._spice_server(str(self))
        self.reset_analysis()

        # for field in raw_file.variables:
        #     print field

        return raw_file.to_analysis(self._circuit)

####################################################################################################

class NgSpiceSharedCircuitSimulator(CircuitSimulator):

    _logger = _module_logger.getChild('NgSpiceSharedCircuitSimulator')

    __ngspice_shared__ = None

    ##############################################

    def __init__(self, circuit,
                 temperature=27,
                 nominal_temperature=27,
                ):

        # Fixme: kwargs

        super(NgSpiceSharedCircuitSimulator, self).__init__(circuit, temperature, nominal_temperature, pipe=False)

        if self.__ngspice_shared__ is None:
            self.__ngspice_shared__ = NgSpiceShared(send_data=False)
        self._ngspice_shared = self.__ngspice_shared__

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        super(NgSpiceSharedCircuitSimulator, self)._run(analysis_method, *args, **kwargs)
        
        self._ngspice_shared.load_circuit(str(self))
        self._ngspice_shared.run()
        self._logger.debug(str(self._ngspice_shared.plot_names))
        self.reset_analysis()

        if analysis_method == 'dc':
            plot_name = 'dc1'
        elif analysis_method == 'ac':
            plot_name = 'ac1'
        elif analysis_method == 'tran':
            plot_name = 'tran1'
        else:
            raise NotImplementedError

        return self._ngspice_shared.plot(plot_name).to_analysis()

####################################################################################################
# 
# End
# 
####################################################################################################
