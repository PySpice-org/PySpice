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

"""This module provides a Python interface to the Ngspice shared library described in the *ngspice
as shared library or dynamic link library* section of the Ngspice user manual.

In comparison to the subprocess interface, it provides an interaction with the simulator through
commands and callbacks and it enables the usage of external voltage and current source in the
circuit.

.. This approach corresponds to the *standard way* to make an interface to a simulator code.

.. warning:: Since we don't simulate a circuit in a fresh environment on demand, this approach is
 less safe than the subprocess approach. In case of bugs within Ngspice, we can expect some side
 effects like memory leaks or worse unexpected things.

This interface use the CFFI module to interface with the shared library. It is thus suited to run
within the Pypy interpreter which implements JIT optimisation for Python.

It can also be used to experiment parallel simulation as explained in the Ngspice user manual. But
it seems the Ngspice source code was designed with global variables which imply to use one copy of
the shared library by worker as explained in the manual.

.. warning:: This interface can strongly slow down the simulation if the input or output callbacks
  is used.  If the simulation time goes wrong for you then you need to implement the callbacks at a
  lower level than Python. You can have look to Pypy, Cython or a C extension module.

"""

####################################################################################################

import logging
import os
import platform
import re
# import time

import numpy as np

####################################################################################################

from cffi import FFI
ffi = FFI()

####################################################################################################

from PySpice.Unit import u_V, u_A, u_s, u_Hz, u_F

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

from PySpice.Config import ConfigInstall
from PySpice.Probe.WaveForm import (OperatingPoint, SensitivityAnalysis,
                                    DcAnalysis, AcAnalysis, TransientAnalysis,
                                    WaveForm)
from PySpice.Tools.EnumFactory import EnumFactory
from .SimulationType import SIMULATION_TYPE

####################################################################################################

def ffi_string_utf8(x):
    return ffi.string(x).decode('utf8') # Fixme: ascii ?

####################################################################################################

class Vector:

    """ This class implements a vector in a simulation output.

    Public Attributes:

      :attr:`data`

      :attr:`name`

    """

    _logger = _module_logger.getChild('Vector')

    ##############################################

    def __init__(self, ngspice_shared, name, type_, data):

        self._ngspice_shared = ngspice_shared
        self._name = str(name)
        self._type = type_
        self._data = data
        self._unit = ngspice_shared.type_to_unit(type_)
        if self._unit is None:
            self._logger.warning('Unit is None for {0._name} {0._type}'.format(self))

    ##############################################

    def __repr__(self):

        return 'variable: {0._name} {0._type}'.format(self)

    ##############################################

    @property
    def is_interval_parameter(self):
        return self._name.startswith('@')

    ##############################################

    @property
    def is_voltage_node(self):
        return self._type == self._ngspice_shared.simulation_type.voltage and not self.is_interval_parameter

    ##############################################

    @property
    def is_branch_current(self):
        return self._type == self._ngspice_shared.simulation_type.current and not self.is_interval_parameter

    ##############################################

    @property
    def simplified_name(self):

        if self.is_voltage_node and self._name.startswith('V('):
            return self._name[2:-1]
        elif self.is_branch_current:
            # return self._name.replace('#branch', '')
            return self._name[:-7]
        else:
            return self._name

    ##############################################

    def to_waveform(self, abscissa=None, to_real=False, to_float=False):

        """ Return a :obj:`PySpice.Probe.WaveForm` instance. """

        data = self._data
        if to_real:
            data = data.real
        # Fixme: else UnitValue instead of UnitValues
        # if to_float:
        #     data = float(data[0])

        if self._unit is not None:
            return WaveForm.from_unit_values(self.simplified_name, self._unit(data), abscissa=abscissa)
        else:
            return WaveForm.from_array(self.simplified_name, data, abscissa=abscissa)

####################################################################################################

class Plot(dict):

    """ This class implements a plot in a simulation output.

    Public Attributes:

      :attr:`plot_name`

    """

    ##############################################

    def __init__(self, simulation, plot_name):

        super().__init__()

        self._simulation = simulation
        self.plot_name = plot_name

    ##############################################

    def nodes(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.values()
                if variable.is_voltage_node]

    ##############################################

    def branches(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.values()
                if variable.is_branch_current]

    ##############################################

    def internal_parameters(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.values()
                if variable.is_interval_parameter]

    ##############################################

    def elements(self, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=True)
                for variable in self.values()]

    ##############################################

    def to_analysis(self):

        if self.plot_name.startswith('op'):
            return self._to_operating_point_analysis()
        elif self.plot_name.startswith('sens'):
            return self._to_sensitivity_analysis()
        elif self.plot_name.startswith('dc'):
            return self._to_dc_analysis()
        elif self.plot_name.startswith('ac'):
            return self._to_ac_analysis()
        elif self.plot_name.startswith('tran'):
            return self._to_transient_analysis()
        else:
            raise NotImplementedError("Unsupported plot name {}".format(self.plot_name))

    ##############################################

    def _to_operating_point_analysis(self):

        return OperatingPoint(
            simulation=self._simulation,
            nodes=self.nodes(to_float=True),
            branches=self.branches(to_float=True),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_sensitivity_analysis(self):

        # Fixme: separate v(vinput), analysis.R2.m
        return SensitivityAnalysis(
            simulation=self._simulation,
            elements=self.elements(), # Fixme: internal parameters ???
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_dc_analysis(self):

        # if 'v(v-sweep)' in self:
        #     sweep_variable = self['v(v-sweep)']
        # elif 'v(i-sweep)' in self:
        #     sweep_variable = self['v(i-sweep)']
        if 'v-sweep' in self:
            sweep_variable = self['v-sweep']
        elif 'i-sweep' in self:
            sweep_variable = self['i-sweep']
        else:
            raise NotImplementedError(str(self))
        sweep = sweep_variable.to_waveform()
        return DcAnalysis(
            simulation=self._simulation,
            sweep=sweep,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_ac_analysis(self):

        frequency = self['frequency'].to_waveform(to_real=True)
        return AcAnalysis(
            simulation=self._simulation,
            frequency=frequency,
            nodes=self.nodes(),
            branches=self.branches(),
            internal_parameters=self.internal_parameters(),
        )

    ##############################################

    def _to_transient_analysis(self):

        time = self['time'].to_waveform(to_real=True)
        return TransientAnalysis(
            simulation=self._simulation,
            time=time,
            nodes=self.nodes(abscissa=time),
            branches=self.branches(abscissa=time),
            internal_parameters=self.internal_parameters(abscissa=time),
        )

####################################################################################################

class NgSpiceShared:

    _logger = _module_logger.getChild('NgSpiceShared')

    NGSPICE_PATH = None
    LIBRARY_PATH = None

    __MAX_COMMAND_LENGTH__ = 1023

    ##############################################

    _instances = {}

    @classmethod
    def new_instance(cls, ngspice_id=0, send_data=False):

        # Fixme: send_data

        if ngspice_id in cls._instances:
            return cls._instances[ngspice_id]
        else:
            cls._logger.info("New instance for id {}".format(ngspice_id))
            instance = cls(ngspice_id=ngspice_id, send_data=send_data)
            cls._instances[ngspice_id] = instance
            return instance

    ##############################################

    def __init__(self, ngspice_id=0, send_data=False):

        """ Set the *send_data* flag if you want to enable the output callback.

        Set the *ngspice_id* to an integer value if you want to run NgSpice in parallel.
        """

        self._ngspice_id = ngspice_id

        self._stdout = []
        self._stderr = []

        self._load_library()
        self._init_ngspice(send_data)

        self._is_running = False

    ##############################################

    already_read_ffi = False

    def _load_library(self):

        if ConfigInstall.OS.on_windows:
            # https://sourceforge.net/p/ngspice/discussion/133842/thread/1cece652/#4e32/5ab8/9027
            # When environment variable SPICE_LIB_DIR is empty, ngspice looks in C:\Spice64\share\ngspice\scripts
            # Else it tries %SPICE_LIB_DIR%\scripts\spinit
            if 'SPICE_LIB_DIR' not in os.environ:
                os.environ['SPICE_LIB_DIR'] = os.path.join(self.NGSPICE_PATH, 'share', 'ngspice')

        if not NgSpiceShared.already_read_ffi:
            NgSpiceShared.already_read_ffi = True
            api_path = os.path.join(os.path.dirname(__file__), 'api.h')
            with open(api_path) as f:
                ffi.cdef(f.read())

        if not self._ngspice_id:
            library_prefix = ''
        else:
            library_prefix = '{}'.format(self._ngspice_id)
        library_path = self.LIBRARY_PATH.format(library_prefix)
        self._logger.debug('Load {}'.format(library_path))
        self._ngspice_shared = ffi.dlopen(library_path)

        # Note: cannot yet execute command

    ##############################################

    def _init_ngspice(self, send_data):

        self._send_char_c = ffi.callback('int (char *, int, void *)', self._send_char)
        self._send_stat_c = ffi.callback('int (char *, int, void *)', self._send_stat)
        self._exit_c = ffi.callback('int (int, bool, bool, int, void *)', self._exit)
        self._send_init_data_c = ffi.callback('int (pvecinfoall, int, void *)', self._send_init_data)
        self._background_thread_running_c = ffi.callback('int (bool, int, void *)', self._background_thread_running)

        if send_data:
            self._send_data_c = ffi.callback('int (pvecvaluesall, int, int, void *)', self._send_data)
        else:
            self._send_data_c = ffi.NULL

        self._get_vsrc_data_c = ffi.callback('int (double *, double, char *, int, void *)', self._get_vsrc_data)
        self._get_isrc_data_c = ffi.callback('int (double *, double, char *, int, void *)', self._get_isrc_data)

        self_c = ffi.new_handle(self)
        self._self_c = self_c # To prevent garbage collection

        rc = self._ngspice_shared.ngSpice_Init(self._send_char_c,
                                               self._send_stat_c,
                                               self._exit_c,
                                               self._send_data_c,
                                               self._send_init_data_c,
                                               self._background_thread_running_c,
                                               self_c)
        if rc:
            raise NameError("Ngspice_Init returned {}".format(rc))

        ngspice_id_c = ffi.new('int *', self._ngspice_id)
        self._ngspice_id = ngspice_id_c # To prevent garbage collection
        rc = self._ngspice_shared.ngSpice_Init_Sync(self._get_vsrc_data_c,
                                                    self._get_isrc_data_c,
                                                    ffi.NULL, # GetSyncData
                                                    ngspice_id_c,
                                                    self_c)
        if rc:
            raise NameError("Ngspice_Init_Sync returned {}".format(rc))

        self._get_version()

        try:
            self._simulation_type = EnumFactory('SimulationType', SIMULATION_TYPE[self._ngspice_version])
        except KeyError:
            self._simulation_type = EnumFactory('SimulationType', SIMULATION_TYPE['last'])
            self._logger.warning("Unsupported Ngspice version {}".format(self._ngspice_version))
        self._type_to_unit = {
            self._simulation_type.time: u_s,
            self._simulation_type.voltage: u_V,
            self._simulation_type.current: u_A,
            self._simulation_type.frequency: u_Hz,
            self._simulation_type.capacitance: u_F,
        }

        # Prevent paging output of commands (hangs)
        self.set('nomoremode')

    ##############################################

    @staticmethod
    def _send_char(message_c, ngspice_id, user_data):

        """Callback for sending output from stdout, stderr to caller"""

        self = ffi.from_handle(user_data)
        message = ffi_string_utf8(message_c)

        prefix, _, content = message.partition(' ')
        if prefix == 'stderr':
            self._stderr.append(content)
            self._logger.error(content)
        else:
            self._stdout.append(content)

        # Fixme: ???
        return self.send_char(message, ngspice_id)

    ##############################################

    @staticmethod
    def _send_stat(message, ngspice_id, user_data):
        """Callback for simulation status to caller"""
        self = ffi.from_handle(user_data)
        return self.send_stat(ffi_string_utf8(message), ngspice_id)

    ##############################################

    @staticmethod
    def _exit(exit_status, immediate_unloding, quit_exit, ngspice_id, user_data):
        """Callback for asking for a reaction after controlled exit"""
        self = ffi.from_handle(user_data)
        self._logger.debug('ngspice_id-{} exit status={} immediate_unloding={} quit_exit={}'.format(
            ngspice_id,
            exit_status,
            immediate_unloding,
            quit_exit))
        return exit_status

    ##############################################

    @staticmethod
    def _send_data(data, number_of_vectors, ngspice_id, user_data):
        """Callback to send back actual vector data"""
        self = ffi.from_handle(user_data)
        # self._logger.debug('ngspice_id-{} send_data [{}]'.format(ngspice_id, data.vecindex))
        actual_vector_values = {}
        for i in range(int(number_of_vectors)):
            actual_vector_value = data.vecsa[i]
            vector_name = ffi_string_utf8(actual_vector_value.name)
            value = complex(actual_vector_value.creal, actual_vector_value.cimag)
            actual_vector_values[vector_name] = value
            # self._logger.debug('    Vector: {} {}'.format(vector_name, value))
        return self.send_data(actual_vector_values, number_of_vectors, ngspice_id)

    ##############################################

    @staticmethod
    def _send_init_data(data,  ngspice_id, user_data):
        """Callback to send back initialization vector data"""
        self = ffi.from_handle(user_data)
        # if self._logger.isEnabledFor(logging.DEBUG):
        #     self._logger.debug('ngspice_id-{} send_init_data'.format(ngspice_id))
        #     number_of_vectors = data.veccount
        #     for i in range(number_of_vectors):
        #         self._logger.debug('  Vector: ' + ffi_string_utf8(data.vecs[i].vecname))
        return self.send_init_data(data, ngspice_id) # Fixme: should be a Python object

    ##############################################

    @staticmethod
    def _background_thread_running(is_running, ngspice_id, user_data):
        """Callback to indicate if background thread is runnin"""
        self = ffi.from_handle(user_data)
        self._logger.debug('ngspice_id-{} background_thread_running {}'.format(ngspice_id, is_running))
        self._is_running = is_running

    ##############################################

    @staticmethod
    def _get_vsrc_data(voltage, time, node, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        return self.get_vsrc_data(voltage, time, ffi_string_utf8(node), ngspice_id)

    ##############################################

    @staticmethod
    def _get_isrc_data(current, time, node, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        return self.get_isrc_data(current, time, ffi_string_utf8(node), ngspice_id)

    ##############################################

    def send_char(self, message, ngspice_id):
        """ Reimplement this callback in a subclass to process logging messages from the simulator. """
        # self._logger.debug('ngspice-{} send_char {}'.format(ngspice_id, message))
        return 0

    ##############################################

    def send_stat(self, message, ngspice_id):
        """ Reimplement this callback in a subclass to process statistic messages from the simulator. """
        # self._logger.debug('ngspice-{} send_stat {}'.format(ngspice_id, message))
        return 0

    ##############################################

    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        """ Reimplement this callback in a subclass to process the vector actual values. """
        return 0

    ##############################################

    def send_init_data(self, data,  ngspice_id):
        """ Reimplement this callback in a subclass to process the initial data. """
        return 0

    ##############################################

    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        """ Reimplement this callback in a subclass to provide external voltage source. """
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        return 0

    ##############################################

    def get_isrc_data(self, current, time, node, ngspice_id):
        """ Reimplement this callback in a subclass to provide external current source. """
        self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        return 0

    ##############################################

    @staticmethod
    def _convert_string_array(array):

        strings = []
        i = 0
        while (True):
            if array[i] == ffi.NULL:
                break
            else:
                strings.append(ffi_string_utf8(array[i]))
            i += 1
        return strings

    ##############################################

    @staticmethod
    def _to_python(value):

        try:
            return int(value)
        except ValueError:
            try:
                # Fixme: return float(value.replace(',', '.'))
                return float(value)
            except ValueError:
                return str(value)

    ##############################################

    @staticmethod
    def _lines_to_dicts(lines):

        values = dict(description=lines[0])
        values.update({parts[0]: NgSpiceShared._to_python(parts[1])
                       for parts in map(str.split, lines)})
        return values

    ##############################################

    @property
    def is_running(self):
        return self._is_running

    ##############################################

    def clear_output(self):

        self._stdout = []
        self._stderr = []

    ##############################################

    @property
    def stdout(self):
        return os.linesep.join(self._stdout)

    @property
    def stderr(self):
        return os.linesep.join(self._stderr)

    ##############################################

    def exec_command(self, command, join_lines=True):

        """ Execute a command and return the output. """

        if len(command) > self.__MAX_COMMAND_LENGTH__:
            raise ValueError('Command must not exceed {} characters'.format(self.__MAX_COMMAND_LENGTH__))

        self._logger.debug('Execute command: {}'.format(command))
        self.clear_output()
        rc = self._ngspice_shared.ngSpice_Command(command.encode('ascii'))
        if rc:
            raise NameError("ngSpice_Command '{}' returned {}".format(command, rc))
        if join_lines:
            return self.stdout
        else:
            return self._stdout

    ##############################################

    def _get_version(self):

        self._ngspice_version = None
        self._has_xspice = False
        self._has_cider = False
        self._extensions = []

        output = self.exec_command('version -f')
        for line in output.split('\n'):
            match = re.match('\*\* ngspice\-(\d+)', line)
            if match is not None:
                self._ngspice_version = int(match.group(1))
            # if '** XSPICE extensions included' in line:
            if '** XSPICE' in line:
                self._has_xspice = True
                self._extensions.append('XSPICE')
            # if '** CIDER 1.b1 (CODECS simulator) included' in line:
            if 'CIDER' in line:
                self._has_cider = True
                self._extensions.append('CIDER')

        self._logger.debug('Ngspice version {} with extensions: {}'.format(
            self._ngspice_version,
            ', '.join(self._extensions),
        ))

    ##############################################

    @property
    def ngspice_version(self):
        return self._ngspice_version

    @property
    def has_xspice(self):
        """Return True if libngspice was compiled with XSpice support."""
        return self._has_xspice

    @property
    def has_cider(self):
        """Return True if libngspice was compiled with CIDER support."""
        return self._has_cider

    ##############################################

    @property
    def simulation_type(self):
        return self._simulation_type

    def type_to_unit(self, vector_type):

        return  self._type_to_unit.get(vector_type, None)

    ##############################################

    def _alter(self, command, device, kwargs):

        device_name = device.lower()
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                value = '[ ' + ' '.join(value) + ' ]'
            self.exec_command('{} {} {} = {}'.format(command, device_name, key, value))

    ##############################################

    def alter_device(self, device, **kwargs):

        """Alter device parameters"""

        self._alter('alter', device, kwargs)

    ##############################################

    def alter_model(self, model, **kwargs):

        """Alter model parameters"""

        self._alter('altermod', model, kwargs)

    ##############################################

    def delete(self, debug_number):

        """Remove a trace or breakpoint"""

        self.exec_command('delete {}'.format(debug_number))

    ##############################################

    def destroy(self, plot_name='all'):

        """Release the memory holding the output data (the given plot or all plots) for the specified runs."""

        self.exec_command('destroy ' + plot_name)

    ##############################################

    def device_help(self, device):

        """Shows the user information about the devices available in the simulator. """

        return self.exec_command('devhelp ' + device.lower())

    ##############################################

    def save(self, vector):

        self.exec_command('save ' + vector)

    ##############################################

    def show(self, device):

        command = 'show ' + device.lower()
        lines = self.exec_command(command, join_lines=False)
        values = self._lines_to_dicts(lines)
        return values

    ##############################################

    def showmod(self, device):

        command = 'showmod ' + device.lower()
        lines = self.exec_command(command, join_lines=False)
        values = self._lines_to_dicts(lines)
        return values

    ##############################################

    def source(self, file_path):

        """Read a ngspice input file"""

        self.exec_command('source ' + file_path)

    ##############################################

    def option(self, **kwargs):

        """Set any of the simulator variables."""

        for key, value in kwargs.items():
            self.exec_command('option {} = {}'.format(key, value))

    ##############################################

    def quit(self):

        self.set('noaskquit')
        return self.exec_command('quit')

    ##############################################

    def remove_circuit(self):

        """Removes the current circuit from the list of circuits sourced into ngspice."""

        self.exec_command('remcirc')

    ##############################################

    def reset(self):

        """Throw out any intermediate data in the circuit (e.g, after a breakpoint or after one or more
        analyses have been done already), and re-parse the input file. The circuit can then be
        re-run from it’s initial state, overriding the affect of any set or alter commands.

        """

        self.exec_command('reset')

    ##############################################

    def ressource_usage(self, *ressources):

        """Print resource usage statistics. If any resources are given, just print the usage of that resource.

        Most resources require that a circuit be loaded. Currently valid resources are:

        * decklineno    Number of lines in deck
        * netloadtime   Nelist loading time
        * netparsetime  Netlist parsing time
        * elapsed       The amount of time elapsed since the last rusage elapsed call.
        * faults        Number of page faults and context switches (BSD only).
        * space         Data space used.
        * time          CPU time used so far.
        * temp          Operating temperature.
        * tnom          Temperature at which device parameters were measured.
        * equations     Circuit Equations
        * time Total    Analysis Time
        * totiter       Total iterations
        * accept        Accepted time-points
        * rejected      Rejected time-points
        * loadtime      Time spent loading the circuit matrix and RHS.
        * reordertime   Matrix reordering time
        * lutime        L-U decomposition time
        * solvetime     Matrix solve time
        * trantime      Transient analysis time
        * tranpoints    Transient time-points
        * traniter      Transient iterations
        * trancuriters  Transient iterations for the last time point*
        * tranlutime    Transient L-U decomposition time
        * transolvetime Transient matrix solve time
        * everything    All of the above.
        """

        if not ressources:
            ressources = ['everything']

        command = 'rusage ' + ' '.join(ressources)
        lines = self.exec_command(command, join_lines=False)
        values = {}
        for line in lines:
            if '=' in line:
                parts = line.split(' = ')
            else:
                parts = line.split(': ')
            values[parts[0]] =  NgSpiceShared._to_python(parts[1])
        return values

    ##############################################

    def set(self, *args, **kwargs):

        """Set the value of variables"""

        for key in args:
            self.exec_command('set {}'.format(key))
        for key, value in kwargs.items():
            self.exec_command('option {} = {}'.format(key, value))

    ##############################################

    def set_circuit(self, name):

        """Change the current circuit"""

        self.exec_command('setcirc {}'.format(name))

    ##############################################

    def status(self):

        """Display breakpoint information"""

        return self.exec_command('status')

    ##############################################

    def step(self, number_of_steps=None):

        """Run a fixed number of time-points"""

        if number_of_steps is not None:
            self.exec_command('step {}'.format(number_of_steps))
        else:
            self.exec_command('step')

    ##############################################

    def stop(self, *args, **kwargs):

        """Set a breakpoint.

        Examples::

            ngspice.stop('v(out) > 1', 'v(1) > 10', after=10)

        A when condition can use theses symbols: = <> > < >= <=.

        """

        command = 'stop'
        if 'after' in kwargs:
            command += ' after {}'.format(kwargs['after'])
        for condition in args:
            command += ' when {}'.format(condition)
        self.exec_command(command)

    ##############################################

    def trace(self, *args):

        """Trace nodes"""

        self.exec_command('trace ' + ' '.join(args))

    ##############################################

    def unset(self, *args):

        """Unset variables"""

        for key in args:
            self.exec_command('unset {}'.format(key))

    ##############################################

    def where(self):

        """Identify troublesome node or device"""

        return self.exec_command('where')

    ##############################################

    def load_circuit(self, circuit):

        """Load the given circuit string."""

        circuit_lines = [line for line in str(circuit).split(os.linesep) if line]
        circuit_lines_keepalive = [ffi.new("char[]", line.encode('utf8'))
                                   for line in circuit_lines]
        circuit_lines_keepalive += [ffi.NULL]
        circuit_array = ffi.new("char *[]", circuit_lines_keepalive)
        rc = self._ngspice_shared.ngSpice_Circ(circuit_array)
        if rc:
            raise NameError("ngSpice_Circ returned {}".format(rc))

        # for line in circuit_lines:
        #     rc = self._ngspice_shared.ngSpice_Command('circbyline ' + line)
        #     if rc:
        #         raise NameError("ngSpice_Command circbyline returned {}".format(rc))

    ##############################################

    def run(self, background=False):

        """ Run the simulation. """

        #  in the background thread and wait until the simulation is done

        command = b'bg_run' if background else b'run'
        rc = self._ngspice_shared.ngSpice_Command(command)
        if rc:
            raise NameError("ngSpice_Command run returned {}".format(rc))

        if background:
            self._is_running = True
        else:
            self._logger.debug("Simulation is done")

        # time.sleep(.1) # required before to test if the simulation is running
        # while (self._ngspice_shared.ngSpice_running()):
        #     time.sleep(.1)
        #     self._logger.debug("Simulation is done")

    ##############################################

    def halt(self):

        """ Halt the simulation in the background thread. """

        rc = self._ngspice_shared.ngSpice_Command(b'bg_halt')
        if rc:
            raise NameError("ngSpice_Command bg_halt returned {}".format(rc))

    ##############################################

    def resume(self, background=True):

        """ Halt the simulation in the background thread. """

        command = b'bg_resume' if background else b'resume'
        rc = self._ngspice_shared.ngSpice_Command(command)
        if rc:
            raise NameError("ngSpice_Command bg_resume returned {}".format(rc))

    ##############################################

    @property
    def plot_names(self):

        """ Return the list of plot names. """

        return self._convert_string_array(self._ngspice_shared.ngSpice_AllPlots())

    ##############################################

    @property
    def last_plot(self):

        """ Return the last plot name. """

        return self.plot_names[0]

    ##############################################

    @staticmethod
    def _flags_to_str(flags):

        # enum dvec_flags {
        #   VF_REAL = (1 << 0),		// The data is real.
        #   VF_COMPLEX = (1 << 1),	// The data is complex.
        #   VF_ACCUM = (1 << 2),	// writedata should save this vector.
        #   VF_PLOT = (1 << 3),		// writedata should incrementally plot it.
        #   VF_PRINT = (1 << 4),	// writedata should print this vector.
        #   VF_MINGIVEN = (1 << 5),	// The v_minsignal value is valid.
        #   VF_MAXGIVEN = (1 << 6),	// The v_maxsignal value is valid.
        #   VF_PERMANENT = (1 << 7)	// Don't garbage collect this vector.
        # };

        if flags & 1:
            return 'real'
        elif flags & 2:
            return 'complex'

    ##############################################

    @staticmethod
    def _vector_is_real(flags):

        return flags & 1

    ##############################################

    @staticmethod
    def _vector_is_complex(flags):

        return flags & 2

    ##############################################

    def plot(self, simulation, plot_name):

        """ Return the corresponding plot. """

        # plot_name is for example dc with an integer suffix which is increment for each run

        plot = Plot(simulation, plot_name)
        all_vectors_c = self._ngspice_shared.ngSpice_AllVecs(plot_name.encode('utf8'))
        i = 0
        while (True):
            if all_vectors_c[i] == ffi.NULL:
                break
            else:
                vector_name = ffi_string_utf8(all_vectors_c[i])
                name = '.'.join((plot_name, vector_name))
                vector_info = self._ngspice_shared.ngGet_Vec_Info(name.encode('utf8'))
                vector_type = self._simulation_type[vector_info.v_type]
                length = vector_info.v_length
                # self._logger.debug("vector[{}] {} type {} flags {} length {}".format(i,
                #                                                                      vector_name,
                #                                                                      vector_type,
                #                                                                      self._flags_to_str(vector_info.v_flags),
                #                                                                      length))
                if vector_info.v_compdata == ffi.NULL:
                    # for k in xrange(length):
                    #     print("  [{}] {}".format(k, vector_info.v_realdata[k]))
                    tmp_array = np.frombuffer(ffi.buffer(vector_info.v_realdata, length*8), dtype=np.float64)
                    array = np.array(tmp_array, dtype=tmp_array.dtype) # copy data
                else:
                    # for k in xrange(length):
                    #     value = vector_info.v_compdata[k]
                    #     print(ffi.addressof(value, field='cx_real'), ffi.addressof(value, field='cx_imag'))
                    #     print("  [{}] {} + i {}".format(k, value.cx_real, value.cx_imag))
                    tmp_array = np.frombuffer(ffi.buffer(vector_info.v_compdata, length*8*2), dtype=np.float64)
                    array = np.array(tmp_array[0::2], dtype=np.complex64)
                    array.imag = tmp_array[1::2]
                plot[vector_name] = Vector(self, vector_name, vector_type, array)
            i += 1

        return plot

####################################################################################################
#
# Platform setup
#

if ConfigInstall.OS.on_windows:
    drive = os.getenv('SystemDrive') or 'C:'
    root = drive + os.sep

    ngspice_dirname = 'Spice'
    if platform.architecture()[0] == '64bit':
        ngspice_dirname += '64'
    ngspice_dirname += '_dll'

    ngspice_path = os.path.join(root, 'Program Files', ngspice_dirname)
    NgSpiceShared.NGSPICE_PATH = ngspice_path

    _path = os.path.join(ngspice_path, 'dll-vs', 'ngspice{}.dll')
elif ConfigInstall.OS.on_osx:
    _path = 'libngspice{}.dylib'
elif ConfigInstall.OS.on_linux:
    _path = 'libngspice{}.so'
else:
    raise NotImplementedError
NgSpiceShared.LIBRARY_PATH= _path
