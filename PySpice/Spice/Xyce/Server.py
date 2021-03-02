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

"""This module provides an interface to run xyce and get back the simulation
output.

"""

####################################################################################################

import logging
import os
import shutil
import subprocess
import tempfile

from PySpice.Config import ConfigInstall
from .RawFile import RawFile

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class XyceServer:

    """This class wraps the execution of Xyce and convert the output to a Python data structure.

    Example of usage::

      spice_server = XyceServer(xyce_command='/path/to/Xyce')
      raw_file = spice_server(spice_input)

    It returns a :obj:`PySpice.Spice.RawFile` instance.

    Default Xyce path is set in `XyceServer.XYCE_COMMAND`.

    """

    if ConfigInstall.OS.on_linux:
        XYCE_COMMAND = 'Xyce'
    elif ConfigInstall.OS.on_osx:
        XYCE_COMMAND = 'Xyce'
    elif ConfigInstall.OS.on_windows:
        XYCE_COMMAND = 'C:\\Program Files\\Xyce 6.10 OPENSOURCE\\bin\\Xyce.exe'
    else:
        raise NotImplementedError

    _logger = _module_logger.getChild('XyceServer')

    ##############################################

    def __init__(self, **kwargs):

        self._xyce_command = kwargs.get('xyce_command') or self.XYCE_COMMAND

    ##############################################

    def _parse_stdout(self, stdout):

        """Parse stdout for errors."""

        # log Spice output
        self._logger.info(os.linesep + stdout.decode('utf-8'))

        error_found = False
        simulation_failed = False
        warning_found = False
        lines = stdout.splitlines()
        for line_index, line in enumerate(lines):
            if line.startswith(b'Netlist warning'):
                warning_found = True
                # Fixme: highlight warnings
                self._logger.warning(os.linesep + line.decode('utf-8'))
            elif line.startswith(b'Netlist error'):
                error_found = True
                self._logger.error(os.linesep + line.decode('utf-8'))
            elif b'Transient failure history' in line:
                simulation_failed = True
                self._logger.error(os.linesep + line.decode('utf-8'))
        if error_found:
            raise NameError("Errors was found by Xyce")
        elif simulation_failed:
            raise NameError("Xyce simulation failed")

    ##############################################

    def __call__(self, spice_input):

        """Run SPICE in server mode as a subprocess for the given input and return a
        :obj:`PySpice.RawFile.RawFile` instance.

        """

        self._logger.debug('Start the xyce subprocess')

        tmp_dir = tempfile.mkdtemp()
        input_filename = os.path.join(tmp_dir, 'input.cir')
        output_filename = os.path.join(tmp_dir, 'output.raw')
        with open(input_filename, 'w') as f:
            f.write(str(spice_input))

        command = (self._xyce_command, '-r', output_filename, input_filename)
        self._logger.info('Run {}'.format(' '.join(command)))
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        self._parse_stdout(stdout)

        with open(output_filename, 'rb') as f:
            output = f.read()
        # self._logger.debug(output)

        raw_file = RawFile(output)
        shutil.rmtree(tmp_dir)

        return raw_file
