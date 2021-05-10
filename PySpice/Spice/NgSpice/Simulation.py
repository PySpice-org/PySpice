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

from ..Simulation import CircuitSimulator
from .Server import SpiceServer
from .Shared import NgSpiceShared

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class NgSpiceCircuitSimulator(CircuitSimulator):

    SIMULATOR = 'ngspice'

    ##############################################

    def __init__(self, circuit, **kwargs):

        super().__init__(circuit, **kwargs)

        if kwargs.get('pipe', True):
            self.options('NOINIT')
            self.options(filetype='binary')

####################################################################################################

class NgSpiceSubprocessCircuitSimulator(NgSpiceCircuitSimulator):

    _logger = _module_logger.getChild('NgSpiceSubprocessCircuitSimulator')

    ##############################################

    def __init__(self, circuit, **kwargs):

        super().__init__(circuit, pipe=True, **kwargs)

        # Fixme: to func ?
        server_kwargs = {x:kwargs[x] for x in ('spice_command',) if x in kwargs}
        self._spice_server = SpiceServer(**server_kwargs)

    ##############################################

    def _run(self, analysis_method, *args, **kwargs):

        super()._run(analysis_method, *args, **kwargs)

        raw_file = self._spice_server(spice_input=str(self))
        self.reset_analysis()
        raw_file.simulation = self

        # for field in raw_file.variables:
        #     print field

        return raw_file.to_analysis()

####################################################################################################

class NgSpiceSharedCircuitSimulator(NgSpiceCircuitSimulator):

    _logger = _module_logger.getChild('NgSpiceSharedCircuitSimulator')

    ##############################################

    def __init__(self, circuit, **kwargs):

        super().__init__(circuit, pipe=False, **kwargs)

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

    def _run(self, analysis_method, *args, **kwargs):

        super()._run(analysis_method, *args, **kwargs)

        self._ngspice_shared.destroy()
        # load circuit and simulation
        # Fixme: Error: circuit not parsed.
        self._ngspice_shared.load_circuit(str(self))
        self._ngspice_shared.run()
        self._logger.debug(str(self._ngspice_shared.plot_names))
        self.reset_analysis()

        plot_name = self._ngspice_shared.last_plot
        if plot_name == 'const':
            raise NameError('Simulation failed')

        return self._ngspice_shared.plot(self, plot_name).to_analysis()
