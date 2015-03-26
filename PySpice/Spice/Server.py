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
import re
import subprocess

####################################################################################################

from .RawFile import RawFile

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceServer(object):

    """ This class wraps the execution of SPICE in server mode and convert the output in Python data
    structure.

    Example of usage::

      spice_server = SpiceServer(spice_command='/path/to/ngspice')
      raw_file = spice_server(spice_input)

    It returns a :obj:`PySpice.Spice.RawFile` instance.

    """

    _logger = _module_logger.getChild('SpiceServer')

    ##############################################

    def __init__(self, spice_command='ngspice'):

        self._spice_command = spice_command

    ##############################################

    def _decode_number_of_points(self, line):

        """ Decode the number of points in stderr line. """

        match = re.match(r'@@@ (\d+) (\d+)', line)
        if match is not None:
            return int(match.group(2))
        else:
            raise NameError("Cannot decode the number of points")

    ##############################################

    def _parse_stdout(self, stdout):

        """ Parse stdout for errors. """

        # self._logger.debug('\n' + stdout)

        error_found = False
        lines = stdout.splitlines()
        for line_index, line in enumerate(lines):
            if line.startswith(b'Error '):
                error_found = True
                self._logger.error('\n' + line + '\n' + lines[line_index+1])
        if error_found:
            raise NameError("Errors was found by Spice")

    ##############################################

    def _parse_stderr(self, stderr):

        """ Parse stderr for warnings and return the number of points. """

        stderr_lines = stderr.splitlines()
        number_of_points = None
        for line in stderr_lines:
            if line.startswith('Warning:'):
                self._logger.warning(line[len('Warning :'):])
            elif line == 'run simulation(s) aborted':
                raise NameError("Simulation aborted\n" + stderr)
            elif line.startswith('@@@'):
                number_of_points = self._decode_number_of_points(line)

        return number_of_points

    ##############################################

    def __call__(self, spice_input):

        """Run SPICE as a subprocess in server mode for the given input and return a
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
            raise NameError("The number of points was not found in the standard error buffer")

        return RawFile(stdout, number_of_points)

####################################################################################################
# 
# End
# 
####################################################################################################
