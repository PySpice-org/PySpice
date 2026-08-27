###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This modules implements classes to perform simulations.
"""

####################################################################################################

from typing import TYPE_CHECKING
import logging

####################################################################################################

from ..Simulator import Simulator
from .Server import SpiceServer
from .Shared import NgSpiceShared

if TYPE_CHECKING:
    from PySpice.Probe.WaveForm import Analysis
    from ..Simulation import Simulation

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class NgSpiceSimulator(Simulator):
    SIMULATOR = 'ngspice'

####################################################################################################

class NgSpiceSubprocessSimulator(NgSpiceSimulator):

    _logger = _module_logger.getChild('NgSpiceSubprocessSimulator')

    ##############################################

    def __init__(self, **kwargs) -> None:
        # super().__init__(**kwargs)
        # Fixme: to func ?
        server_kwargs = {x: kwargs[x] for x in ('spice_command',) if x in kwargs}
        self._spice_server = SpiceServer(**server_kwargs)

    ##############################################

    @property
    def version(self) -> str:
        # Fixme: How to implement ?
        return ''

    ##############################################

    def customise(self, simulation: 'Simulation') -> None:
        # quicker to subclass...
        simulation.options('NOINIT')
        simulation.options(filetype='binary')

    ##############################################

    def run(self, simulation: 'Simulation', *args, **kwargs):
        raw_file = self._spice_server(spice_input=str(simulation))
        raw_file.simulation = simulation
        # for field in raw_file.variables:
        #     print field
        return raw_file.to_analysis()

####################################################################################################

class NgSpiceSharedSimulator(NgSpiceSimulator):

    _logger = _module_logger.getChild('NgSpiceSharedSimulator')

    ##############################################

    def __init__(self, **kwargs) -> None:
        # super().__init__(**kwargs)
        ngspice_shared = kwargs.get('ngspice_shared', None)
        if ngspice_shared is None:
            self._ngspice_shared = NgSpiceShared.new_instance()
        else:
            self._ngspice_shared = ngspice_shared

    ##############################################

    @property
    def ngspice(self) -> NgSpiceShared:
        return self._ngspice_shared

    ##############################################

    @property
    def version(self) -> str:
        return self._ngspice_shared.ngspice_version

    ##############################################

    def run(self, simulation: 'Simulation') -> 'Analysis':
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
