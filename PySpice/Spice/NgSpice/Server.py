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

"""This module provides an interface to run ngspice in server mode and get back the simulation
output.

When ngspice runs in server mode, it writes on the standard output an header and then the simulation
output in binary format.  At the end of the simulation, it writes on the standard error a line of
the form:

    .. code::

        @@@ \d+ \d+

where the second number is the number of points of the simulation.  Due to the iterative and
adaptive nature of a transient simulation, the number of points is only known at the end.

Any line starting with "Error" in the standard output indicates an error in the simulation process.
The line "run simulation(s) aborted" in the standard error indicates the simulation aborted.

Any line starting with *Warning* in the standard error indicates non critical error in the
simulation process.

"""

####################################################################################################

import logging
import os
import re
import subprocess

####################################################################################################

from .RawFile import RawFile

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceServer:

    """This class wraps the execution of ngspice in server mode and convert the output to a Python data
    structure.

    Example of usage::

      spice_server = SpiceServer(spice_command='/path/to/ngspice')
      raw_file = spice_server(spice_input)

    It returns a :obj:`PySpice.Spice.RawFile` instance.

    """

    _logger = _module_logger.getChild('SpiceServer')

    SPICE_COMMAND = 'ngspice'

    ##############################################

    def __init__(self, **kwargs):

        self._spice_command = kwargs.get('spice_command') or self.SPICE_COMMAND

    ##############################################

    def _decode_number_of_points(self, line):

        """Decode the number of points in the given line."""

        match = re.match(r'@@@ (\d+) (\d+)', line)
        if match is not None:
            return int(match.group(2))
        else:
            raise NameError("Cannot decode the number of points")

    ##############################################

    def _parse_stdout(self, stdout):

        """Parse stdout for errors."""

        # self._logger.debug(os.linesep + stdout)

        error_found = False
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 870: invalid start byte
        # lines = stdout.decode('utf-8').splitlines()
        lines = stdout.splitlines()
        for line_index, line in enumerate(lines):
            if line.startswith(b'Error '):
                error_found = True
                self._logger.error(os.linesep + line.decode('utf-8') + os.linesep + lines[line_index+1].decode('utf-8'))
        if error_found:
            raise NameError("Errors was found by Spice")

    ##############################################

    def _parse_stderr(self, stderr):

        """Parse stderr for warnings and return the number of points."""

        self._logger.debug(os.linesep + stderr)

        stderr_lines = stderr.splitlines()
        number_of_points = None
        for line in stderr_lines:
            if line.startswith('Warning:'):
                self._logger.warning(line[len('Warning :'):])
            elif line == 'run simulation(s) aborted':
                raise NameError('Simulation aborted' + os.linesep + stderr)
            elif line.startswith('@@@'):
                number_of_points = self._decode_number_of_points(line)

        return number_of_points

    ##############################################

    def __call__(self, spice_input):

        """Run SPICE in server mode as a subprocess for the given input and return a
        :obj:`PySpice.RawFile.RawFile` instance.

        """

        self._logger.info("Start the spice subprocess")

        process = subprocess.Popen((self._spice_command, '-s'),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        input_ = str(spice_input).encode('utf-8')
        stdout, stderr = process.communicate(input_)
        # stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        self._parse_stdout(stdout)
        number_of_points = self._parse_stderr(stderr)
        if number_of_points is None:
            raise NameError('The number of points was not found in the standard error buffer,'
                            ' ngspice returned:' + os.linesep +
                            stderr)

        return RawFile(stdout, number_of_points)
