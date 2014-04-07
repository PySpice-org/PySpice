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

    _logger = _module_logger.getChild('SpiceServer')

    ##############################################

    def __init__(self, spice_command='ngspice'):

        self._spice_command = spice_command

    ##############################################

    def _decode_number_of_points(self, line):

        match = re.match(r'@@@ (\d+) (\d+)', line)
        if match is not None:
            return int(match.group(2))
        else:
            raise NameError("Cannot decode the number of points")

    ##############################################

    def _parse_stdout(self, stdout):

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
            raise NameError("Errors was found by spice")

    ##############################################

    def _parse_stderr(self, stderr):

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

    def __call__(self, desk):

        self._logger.info("Start server")

        process = subprocess.Popen((self._spice_command, '-s'),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(str(desk))

        self._parse_stdout(stdout)
        number_of_points = self._parse_stderr(stderr)
        if number_of_points is None:
            raise NameError("Number of points was not found")

        return RawFile(stdout, number_of_points)

####################################################################################################
# 
# End
# 
####################################################################################################
