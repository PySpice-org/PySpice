####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) 2014 Fabrice Salvaire
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
        location = stdout.find('Doing analysis')
        if location == -1:
            raise NameError("Wrong simulation output")
        else:
            lines = stdout[:location].splitlines()
            for line_index, line in enumerate(lines):
                if line.startswith('Error '):
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
                raise NameError("Simulation aborted")
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
        stdout, stderr = process.communicate(str(spice_input))

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
