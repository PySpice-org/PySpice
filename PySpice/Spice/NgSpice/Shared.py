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
import time

import numpy as np

####################################################################################################

from cffi import FFI
ffi = FFI()

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

from PySpice.Probe.WaveForm import (OperatingPoint, SensitivityAnalysis,
                                    DcAnalysis, AcAnalysis, TransientAnalysis,
                                    WaveForm)
from PySpice.Tools.EnumFactory import EnumFactory

####################################################################################################

def ffi_string_utf8(x):
    return ffi.string(x).decode('utf8')

####################################################################################################

class Vector:

    """ This class implements a vector in a simulation output.

    Public Attributes:

      :attr:`data`

      :attr:`name`

      :attr:`type`
        cf. `NgSpiceShared.simulation_type`

    """

    ##############################################

    def __init__(self, name, type_, data):

        self.name = str(name)
        self.type = type_
        self.data = data

    ##############################################

    def __repr__(self):

        return 'variable: {0.name} {0.type}'.format(self)

    ##############################################

    def is_voltage_node(self):

        return self.type == NgSpiceShared.simulation_type.voltage

    ##############################################

    def is_branch_current(self):

        return self.type == NgSpiceShared.simulation_type.current

    ##############################################

    @property
    def simplified_name(self):

        if self.is_branch_current():
            # return self.name.replace('#branch', '')
            return self.name[:-7]
        else:
            return self.name

    ##############################################

    @property
    def unit(self):

        if self.type == NgSpiceShared.simulation_type.voltage:
            return 'V'
        elif self.type == NgSpiceShared.simulation_type.current:
            return 'A'
        elif self.type == NgSpiceShared.simulation_type.time:
            return 's'
        elif self.type == NgSpiceShared.simulation_type.frequency:
            return 'Hz'
        else:
            return ''

    ##############################################

    def to_waveform(self, abscissa=None, to_real=False, to_float=False):

        """ Return a :obj:`PySpice.Probe.WaveForm` instance. """

        data = self.data
        if to_real:
            data = data.real
        if to_float:
            data = float(data[0])

        return WaveForm(self.simplified_name, self.unit, data, abscissa=abscissa)

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
                if variable.is_voltage_node()]

    ##############################################

    def branches(self, to_float=False, abscissa=None):

        return [variable.to_waveform(abscissa, to_float=to_float)
                for variable in self.values()
                if variable.is_branch_current()]

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
        )

    ##############################################

    def _to_sensitivity_analysis(self):

        # Fixme: separate v(vinput), analysis.R2.m
        return SensitivityAnalysis(
            simulation=self._simulation,
            elements=self.elements(),
        )

    ##############################################

    def _to_dc_analysis(self):

        if 'v(v-sweep)' in self:
            sweep_variable = self['v(v-sweep)']
        elif 'v(i-sweep)' in self:
            sweep_variable = self['v(i-sweep)']
        else:
            raise NotImplementedError
        sweep = sweep_variable.to_waveform()
        return DcAnalysis(
            simulation=self._simulation,
            sweep=sweep,
            nodes=self.nodes(),
            branches=self.branches(),
        )

    ##############################################

    def _to_ac_analysis(self):

        frequency = self['frequency'].to_waveform(to_real=True)
        return AcAnalysis(
            simulation=self._simulation,
            frequency=frequency,
            nodes=self.nodes(),
            branches=self.branches(),
        )

    ##############################################

    def _to_transient_analysis(self):

        time = self['time'].to_waveform(to_real=True)
        return TransientAnalysis(
            simulation=self._simulation,
            time=time,
            nodes=self.nodes(abscissa=time),
            branches=self.branches(abscissa=time),
        )

####################################################################################################

class NgSpiceShared:

    _logger = _module_logger.getChild('NgSpiceShared')

    simulation_type = EnumFactory('SimulationType', (
        'no_type',
        'time',
        'frequency',
        'voltage',
        'current',
        'output_noise_density',
        'output_noise',
        'input_noise_density',
        'input_noise',
        'pole',
        'zero',
        's_parameter',
        'temperature',
        'res',
        'impedance',
        'admittance',
        'power',
        'phase',
        'db',
        'capacitance',
        'charge'))

    ##############################################

    def __init__(self, ngspice_id=0, send_data=False):

        """ Set the *send_data* flag if you want to enable the output callback.

        Set the *ngspice_id* to an integer value if you want to run NgSpice in parallel.
        """

        self._ngspice_id = ngspice_id

        self._load_library()
        self._init_ngspice(send_data)

    ##############################################

    def _load_library(self):

        api_path = os.path.join(os.path.dirname(__file__), 'api.h')
        with open(api_path) as f:
            ffi.cdef(f.read())

        if not self._ngspice_id:
            library_prefix = ''
        else:
            library_prefix = '{}'.format(self._ngspice_id)
        library_file = 'libngspice{}.so'.format(library_prefix)
        self._ngspice_shared = ffi.dlopen(library_file)

    ##############################################

    def _init_ngspice(self, send_data):

        self._send_char_c = ffi.callback('int (char *, int, void *)', self._send_char)
        self._send_stat_c = ffi.callback('int (char *, int, void *)', self._send_stat)
        self._exit_c = ffi.callback('int (int, bool, bool, int, void *)', self._exit)
        self._send_init_data_c = ffi.callback('int (pvecinfoall, int, void *)', self._send_init_data)

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
                                               ffi.NULL, # BGThreadRunning
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

    ##############################################

    @staticmethod
    def _send_char(message, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        return self.send_char(ffi_string_utf8(message), ngspice_id)

    ##############################################

    @staticmethod
    def _send_stat(message, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        return self.send_stat(ffi_string_utf8(message), ngspice_id)

    ##############################################

    @staticmethod
    def _exit(exit_status, immediate_unloding, quit_exit, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        self._logger.debug('ngspice_id-{} exit {} {} {} {}'.format(ngspice_id,
                                                                   exit_status,
                                                                   immediate_unloding,
                                                                   quit_exit))
        return exit_status

    ##############################################

    @staticmethod
    def _send_data(data, number_of_vectors, ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        self._logger.debug('ngspice_id-{} send_data [{}]'.format(ngspice_id, data.vecindex))
        actual_vector_values = {}
        for i in range(int(number_of_vectors)):
            actual_vector_value = data.vecsa[i]
            vector_name = ffi_string_utf8(actual_vector_value.name)
            value = complex(actual_vector_value.creal, actual_vector_value.cimag)
            actual_vector_values[vector_name] = value
            self._logger.debug('    Vector: {} {}'.format(vector_name, value))
        return self.send_data(actual_vector_values, number_of_vectors, ngspice_id)

    ##############################################

    @staticmethod
    def _send_init_data(data,  ngspice_id, user_data):
        """FFI Callback"""
        self = ffi.from_handle(user_data)
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('ngspice_id-{} send_init_data'.format(ngspice_id))
            number_of_vectors = data.veccount
            for i in range(number_of_vectors):
                self._logger.debug('  Vector: ' + ffi_string_utf8(data.vecs[i].vecname))
        return self.send_init_data(data, ngspice_id) # Fixme: should be a Python object

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
        self._logger.debug('ngspice-{} send_char {}'.format(ngspice_id, message))
        return 0

    ##############################################

    def send_stat(self, message, ngspice_id):
        """ Reimplement this callback in a subclass to process statistic messages from the simulator. """
        self._logger.debug('ngspice-{} send_stat {}'.format(ngspice_id, message))
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

    def load_circuit(self, circuit):

        """ Load the given circuit string. """

        circuit_lines = [line for line in str(circuit).split('\n') if line]
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

    def run(self):

        """ Run the simulation in the background thread and wait until the simulation is done. """

        rc = self._ngspice_shared.ngSpice_Command(b'bg_run')
        if rc:
            raise NameError("ngSpice_Command bg_run returned {}".format(rc))

        time.sleep(.1) # required before to test if the simulation is running
        while (self._ngspice_shared.ngSpice_running()):
            time.sleep(.1)
        self._logger.debug("Simulation is done")

    ##############################################

    def _convert_string_array(self, array):

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

    @property
    def plot_names(self):

        """ Return the list of plot names. """

        return self._convert_string_array(self._ngspice_shared.ngSpice_AllPlots())

    ##############################################

    def plot(self, simulation, plot_name):

        """ Return the corresponding plot. """

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
                vector_type = vector_info.v_type
                length = vector_info.v_length
                self._logger.debug("vector[{}] {} type {} flags {} length {}".format(i,
                                                                                     vector_name,
                                                                                     vector_type,
                                                                                     vector_info.v_flags,
                                                                                     length))
                # flags: VF_REAL = 1 << 0, VF_COMPLEX = 1 << 1
                if vector_info.v_compdata == ffi.NULL:
                    # for k in xrange(length):
                    #     print("  [{}] {}".format(k, vector_info.v_realdata[k]))
                    array = np.frombuffer(ffi.buffer(vector_info.v_realdata, length*8), dtype=np.float64)
                else:
                    # for k in xrange(length):
                    #     value = vector_info.v_compdata[k]
                    #     print(ffi.addressof(value, field='cx_real'), ffi.addressof(value, field='cx_imag'))
                    #     print("  [{}] {} + i {}".format(k, value.cx_real, value.cx_imag))
                    tmp_array = np.frombuffer(ffi.buffer(vector_info.v_compdata, length*8*2), dtype=np.float64)
                    array = np.array(tmp_array[0::2], dtype=np.complex64)
                    array.imag = tmp_array[1::2]
                plot[vector_name] = Vector(vector_name, self.simulation_type[vector_type], array)
            i += 1

        return plot
