####################################################################################################
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

####################################################################################################
#
# op: value
# transient: time
# dc: v-sweep
# ac: frequency
# sens: element parameters
#
# Probes
#
# Nodes:
#   Voltage versus gnd
#   real or complex
#   static or (temporale/transient, v-sweep, frequency)
#
#   static waveform: (node->, unit, value)
#   waveform: (node->, unit, values, abscissa->)
#
#   analysis.1.v !
#   analysis.in.v !
#   analysis['1'].v
#   analysis.n1.v
#
# Source:
#   Current
#
#   analysis.Vinput.i
#
# Vinput -> lower case
#
# axe.plot(x, y, *args, **kwargs)
#
###################################################################################################

####################################################################################################
#
# Analysis versus Simulation
#
####################################################################################################

####################################################################################################

import numpy as np

####################################################################################################

# Fixme: self._

class WaveForm(np.ndarray):

    """This class implements a waveform on top of Numpy Array.
    """

    ##############################################

    def __new__(cls, name, unit, data, title=None, abscissa=None):

        obj = np.asarray(data).view(cls)

        obj.name = str(name)
        obj.unit = unit
        obj.title = title # str(title)
        obj.abscissa = abscissa

        return obj

    ##############################################

    def __array_finalize__(self, obj):

        if obj is None:
            return

        self.name = getattr(obj, 'name', None)
        self.unit = getattr(obj, 'unit', None)
        self.title = getattr(obj, 'title', None)
        self.abscissa = getattr(obj, 'abscissa', None)

    ##############################################

    def __repr__(self):

        return 'variable {0.name} [{0.unit}]'.format(self)

    ##############################################

    def __str__(self):

        if self.title is not None:
            return self.title
        else:
            return '{0.name} [{0.unit}]'.format(self)

    ##############################################

    def str_data(self):

        return super().__repr__()

####################################################################################################

class Analysis:

    ##############################################

    def __init__(self, simulation, nodes=(), branches=(), elements=()):

        # Fixme: branches are elements in fact, and elements is not yet supported ...

        self._simulation = simulation
        # Fixme: to func?
        self.nodes = {waveform.name:waveform for waveform in nodes}
        self.branches = {waveform.name:waveform for waveform in branches}
        self.elements = {waveform.name:waveform for waveform in elements}

    ##############################################

    @property
    def simulation(self):
        return self._simulation

    ##############################################

    def __getitem__(self, name):

        if name in self.nodes:
            return self.nodes[name]
        elif name in self.branches:
            return self.branches[name]
        elif name in self.elements:
            return self.elements[name]
        else:
            raise IndexError(name)

    ##############################################

    def __getattr__(self, name):

        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(name)

####################################################################################################

class OperatingPoint(Analysis):
    pass

####################################################################################################

class SensitivityAnalysis(Analysis):

    ##############################################

    def __init__(self, simulation, elements):

        super().__init__(simulation=simulation, elements=elements)

####################################################################################################

class DcAnalysis(Analysis):

    """

    When the DC analysis is performed with multiple sources, sweep is the last source.

    The loop scheme is::

        for v1 in vsource1:
             for v2 in vsource2:
                 ...

    """

    ##############################################

    def __init__(self, simulation, sweep, nodes, branches):

        super().__init__(simulation=simulation, nodes=nodes, branches=branches)

        self._sweep = sweep

    ##############################################

    @property
    def sweep(self):
        return self._sweep

####################################################################################################

class AcAnalysis(Analysis):

    ##############################################

    def __init__(self, simulation, frequency, nodes, branches):

        super().__init__(simulation=simulation, nodes=nodes, branches=branches)

        self._frequency = frequency

    ##############################################

    @property
    def frequency(self):
        return self._frequency

####################################################################################################

class TransientAnalysis(Analysis):

    ##############################################

    def __init__(self, simulation, time, nodes, branches):

        super().__init__(simulation=simulation, nodes=nodes, branches=branches)

        self._time = time

    ##############################################

    @property
    def time(self):
        return self._time
