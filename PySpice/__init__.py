####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'Circuit',
    'Simulator',
    'SpiceLibrary',
    'plot',
]

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Spice.Simulator import Simulator

####################################################################################################

__version__ = '1.6'
GIT_TAG = 'v1.6-branched'

def show_version():
    print(f'PySpice Version {__version__}')
