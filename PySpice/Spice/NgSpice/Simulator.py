###################################################################################################
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

"""This modules implements classes to perform simulations.
"""

####################################################################################################

import logging

####################################################################################################

from ..Simulator import Simulator
from .Server import SpiceServer
from .Shared import NgSpiceShared

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class NgSpiceSimulator(Simulator):
    SIMULATOR = 'ngspice'

####################################################################################################

class NgSpiceSubprocessSimulator(NgSpiceSimulator):

    _logger = _module_logger.getChild('NgSpiceSubprocessSimulator')

    ##############################################

    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        # Fixme: to func ?
        server_kwargs = {x:kwargs[x] for x in ('spice_command',) if x in kwargs}
        self._spice_server = SpiceServer(**server_kwargs)

    ##############################################

    def customise(self, simulation):
        # quicker to subclass...
        simulation.options('NOINIT')
        simulation.options(filetype='binary')

    ##############################################

    def run(self, simulation, *args, **kwargs):
        raw_file = self._spice_server(spice_input=str(simulation))
        raw_file.simulation = simulation
        # for field in raw_file.variables:
        #     print field
        return raw_file.to_analysis()

####################################################################################################

class NgSpiceSharedSimulator(NgSpiceSimulator):

    _logger = _module_logger.getChild('NgSpiceSharedSimulator')

    ##############################################

    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        ngspice_shared = kwargs.get('ngspice_shared', None)
        if ngspice_shared is None:
            self._ngspice_shared = NgSpiceShared.new_instance()
        else:
            self._ngspice_shared = ngspice_shared

    ##############################################

    @property
    def ngspice(self):
        return self._ngspice_shared

    ##############################################

    def run(self, simulation):

        # Release the memory holding the output data
        self._ngspice_shared.destroy()

        # load circuit and simulation
        # Fixme: Error: circuit not parsed.
        self._ngspice_shared.load_circuit(str(simulation))
        self._ngspice_shared.run()
        self._logger.debug(str(self._ngspice_shared.plot_names))

        plot_name = self._ngspice_shared.last_plot
        if plot_name == 'const':
            raise NameError('Simulation failed')

        return self._ngspice_shared.plot(simulation, plot_name).to_analysis()
