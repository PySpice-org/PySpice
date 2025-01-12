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

"""This module provides an interface to run OpenSPICE and get back the simulation
output.

"""

####################################################################################################

import logging
import os
import shutil
import subprocess
import tempfile
# TODO: Change
from .OpenSPICE import run

from PySpice.Config import ConfigInstall
from .RawFile import RawFile

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class OpenSPICEServer:

    """This class wraps the execution of OpenSPICE and convert the output to a Python data structure.

    Example of usage::

      spice_server = OpenSPICEServer()
      raw_file = spice_server(spice_input)

    It returns a :obj:`PySpice.Spice.RawFile` instance.

    """

    OpenSPICE_COMMAND = 'python3 -m OpenSPICE'

    _logger = _module_logger.getChild('OpenSPICEServer')

    ##############################################

    def __init__(self, **kwargs):

        self._OpenSPICE_command = kwargs.get('OpenSPICE_command') or self.OpenSPICE_COMMAND

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
            raise NameError("Error were found by OpenSPICE")
        elif simulation_failed:
            raise NameError("OpenSPICE simulation failed")

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

        run(input_filename, output_filename)

        with open(output_filename, 'rb') as f:
            output = f.read()

        raw_file = RawFile(output)
        shutil.rmtree(tmp_dir)

        return raw_file
