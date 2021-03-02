###################################################################################################
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

"""This modules implements classes to perform simulations.
"""

####################################################################################################

import logging

####################################################################################################

from ..Simulation import CircuitSimulator
from .Server import XyceServer

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class XyceCircuitSimulator(CircuitSimulator):

    _logger = _module_logger.getChild('XyceCircuitSimulator')

    SIMULATOR = 'xyce'

    ##############################################

    def __init__(self, circuit, **kwargs):

        super().__init__(circuit, **kwargs)

        xyce_command = kwargs.get('xyce_command', None)
        self._xyce_server = XyceServer(xyce_command=xyce_command)

    ##############################################

    def str_options(self):

        return super().str_options(unit=False)

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        super()._run(analysis_method, *args, **kwargs)

        raw_file = self._xyce_server(spice_input=str(self))
        self.reset_analysis()
        raw_file.simulation = self

        # for field in raw_file.variables:
        #     print field

        return raw_file.to_analysis()
