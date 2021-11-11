###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
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

__all__ = ['Simulator']

####################################################################################################

"""This module provides the base class for simulator and a factory method.

"""

####################################################################################################

import logging

####################################################################################################

from ..Config import ConfigInstall
from .Simulation import Simulation

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: DOC: Each analysis mode is performed by a method that return the measured probes.

class Simulator:

    """Base class to implement a simulator.

    """

    _logger = _module_logger.getChild('Simulator')

    #: Define the default simulator
    DEFAULT_SIMULATOR = None
    if ConfigInstall.OS.on_windows:
        DEFAULT_SIMULATOR = 'ngspice-shared'
    else:
        # DEFAULT_SIMULATOR = 'ngspice-subprocess'
        DEFAULT_SIMULATOR = 'ngspice-shared'
        # DEFAULT_SIMULATOR = 'xyce-serial'
        # DEFAULT_SIMULATOR = 'xyce-parallel'

    SIMULATORS = (
        'ngspice',
        'ngspice-shared',
        'ngspice-subprocess',
        'xyce',
        'xyce-serial',
        'xyce-parallel',
    )

    SIMULATOR = None   # for subclass

    ##############################################

    @classmethod
    def factory(cls, *args, **kwargs):

        """Factory to instantiate a simulator.

        By default, it instantiates the simulator defined in :obj:`DEFAULT_SIMULATOR`, however you
        can set the simulator using the :obj:`simulator` parameter.

        Available simulators are:

        * :code:`ngspice` **alias for shared**
        * :code:`ngspice-shared` **DEFAULT**
        * :code:`ngspice-subprocess`
        * :code:`xyce` **alias for serial**
        * :code:`xyce-serial`
        * :code:`xyce-parallel`

        Return a :obj:`PySpice.Spice.Simulator` subclass.

        """

        # Fixme: purpose ??? simplify import...

        simulator = kwargs.pop('simulator', cls.DEFAULT_SIMULATOR)
        sub_cls = None

        if simulator not in cls.SIMULATORS:
            raise NameError(f"Unknown simulator {simulator}")

        if simulator.startswith('ngspice'):
            if simulator == 'ngspice-subprocess':
                from .NgSpice.Simulator import NgSpiceSubprocessSimulator
                sub_cls = NgSpiceSubprocessSimulator
            elif simulator in ('ngspice', 'ngspice-shared'):
                from .NgSpice.Simulator import NgSpiceSharedSimulator
                sub_cls = NgSpiceSharedSimulator

        elif simulator.startswith('xyce'):
            from .Xyce.Simulator import XyceSimulator
            sub_cls = XyceSimulator
            if simulator == 'xyce-parallel':
                kwargs['parallel'] = True

        if sub_cls is not None:
            obj = sub_cls(*args, **kwargs)
            obj._AS_SIMULATOR = simulator
            return obj
        else:
            raise ValueError('Unknown simulator')

    ##############################################

    def __getstate__(self):
        # Pickle: protection for cffi
        return self.__class__.__name__

    ##############################################

    def simulation(self, circuit, **kwargs):
        """Create a new simulation for the circuit.

        Return a :obj:`PySpice.Spice.Simulation` instance`

        """
        # Note: simulation is simulator dependent, thus subclass this method if needed
        return Simulation(self, circuit, **kwargs)

    ##############################################

    @property
    def simulator_version(self):
        raise NotImplementedError

    ##############################################

    def customise(self, simulation):
        """Customise the simulation"""
        pass

    ##############################################

    def run(self, simulation):
        """Run the simulation and return the waveforms."""
        raise NotImplementedError
