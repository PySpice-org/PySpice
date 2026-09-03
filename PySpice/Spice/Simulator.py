###################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This module provides the base class for simulator and a factory method.

"""

####################################################################################################

__all__ = ['Simulator']

####################################################################################################

import logging
from typing import TYPE_CHECKING, NotRequired, TypedDict, Unpack

from ..Config import ConfigInstall
from .Simulation import Simulation, SimulationParams

if TYPE_CHECKING:
    from PySpice.Probe.WaveForm import Analysis

    from .Netlist import Circuit

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# Fixme: DOC: Each analysis mode is performed by a method that return the measured probes.

class SimulatorParams(TypedDict):
    simulator: NotRequired[str | None]  # = None
    parallel: NotRequired[bool]  # = False for Xyce

class Simulator:

    """Base class to implement a simulator.

    """

    _logger = _module_logger.getChild('Simulator')

    #: Define the default simulator
    DEFAULT_SIMULATOR = None
    if ConfigInstall.OS.on_windows:  # ruff: ignore[if-else-block-instead-of-if-exp]
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

    SIMULATOR = None  # for subclass

    ##############################################

    @classmethod
    def factory(cls, *args, **kwargs: Unpack[SimulatorParams]) -> Simulator:
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
            raise ValueError(f"Unknown simulator {simulator}")

        if simulator.startswith('ngspice'):
            match simulator:
                case 'ngspice-subprocess':
                    from .NgSpice.Simulator import NgSpiceSubprocessSimulator
                    sub_cls = NgSpiceSubprocessSimulator
                case 'ngspice' | 'ngspice-shared':
                    from .NgSpice.Simulator import NgSpiceSharedSimulator
                    sub_cls = NgSpiceSharedSimulator

        elif simulator.startswith('xyce'):
            from .Xyce.Simulator import XyceSimulator
            sub_cls = XyceSimulator
            if simulator == 'xyce-parallel':
                kwargs['parallel'] = True

        if sub_cls is not None:
            obj = sub_cls(*args, **kwargs)
            # Fixme: pass as arg ?
            obj._as_simulator = simulator
            cls._logger.info(f"Simulator is {sub_cls.__name__}")
            return obj
        else:
            raise ValueError(f"Unknown simulator {simulator}")

    ##############################################

    def __init__(self) -> None:
        self._as_simulator: str

    ##############################################

    def __getstate__(self) -> str:
        # Pickle: protection for cffi
        return self.__class__.__name__

    ##############################################

    def simulation(self, circuit: Circuit, **kwargs: Unpack[SimulationParams]) -> Simulation:
        """Create a new simulation for the circuit.

        Return a :obj:`PySpice.Spice.Simulation` instance`

        """
        # Note: simulation is simulator dependent, thus subclass this method if needed
        return Simulation(self, circuit, **kwargs)

    ##############################################

    @property
    def name(self) -> str:
        return self._as_simulator

    @property
    def version(self) -> str:
        raise NotImplementedError

    ##############################################

    def customise(self, simulation: Simulation) -> None:
        """Customise the simulation"""

    ##############################################

    def run(self, simulation: Simulation) -> Analysis:
        """Run the simulation and return the waveforms."""
        raise NotImplementedError
