###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

"""This modules implements classes to perform simulations.
"""

####################################################################################################

import logging

####################################################################################################

from ..Simulator import Simulator
from .Server import XyceServer
from .Simulation import XyceSimulation

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class XyceSimulator(Simulator):

    _logger = _module_logger.getChild('XyceSimulator')

    SIMULATOR = 'xyce'

    ##############################################

    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        xyce_command = kwargs.get('xyce_command', None)
        self._xyce_server = XyceServer(xyce_command=xyce_command)

    ##############################################

    @property
    def version(self):
        # Fixme: How to implement ?
        return ''

    ##############################################

    def simulation(self, circuit, **kwargs):
        return XyceSimulation(self, circuit, **kwargs)

    ##############################################

    def run(self, simulation, *args, **kwargs):

        # Fixme: NEED TO BE TESTED !!!
        raw_file = self._xyce_server(spice_input=str(self))
        raw_file.simulation = simulation

        # for field in raw_file.variables:
        #     print field

        return raw_file.to_analysis()
