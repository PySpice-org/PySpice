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

# Fixme: self._

"""This module implements classes to handle analysis output.

"""

####################################################################################################

import os

import numpy as np

####################################################################################################

class WaveForm(np.ndarray):

    """This class implements waveform on top of a Numpy Array.

    Public Attributes:

      :attr:`name`

      :attr:`unit`

      :attr:`title`

      :attr:`abscissa`
        Numpy array of the analysis abscissa

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

    """Base class for the simulation output.

    Depending of the simulation type, the simulator will return waveforms as a function of

      * time
      * frequency
      * sweep
      * ...

    and corresponding to

      * a node's voltage
      * a source's current
      * ...

    The name of a waveform is

      * node's voltage: node's name
      * source's current: source'name
      * ...

    If the waveform name is a valid Python identifier, then you can get the corresponding waveform using::

      analysis.waveforme_name

    else you have to use this fallback::

      analysis['waveforme_name']

    Examples of usages::

        # Operating point analysis
        for node in analysis.nodes.values():
            print('Node {}: {:5.2f} V'.format(str(node), float(node)))
        for node in analysis.branches.values():
            print('Node {}: {:5.2f} A'.format(str(node), float(node)))

        # DC sensitivity analysis
        for element in analysis.elements.values():
            print(element, float(element))

        # Plot the voltage of the "out" node
        plt.plot(analysis.out.abscissa, analysis.out)

    Public Attributes:

      :attr:`nodes`
        Dictionary for node voltages indexed by node names

      :attr:`branches`
        Dictionary for branch currents indexed by source names

      :attr:`elements`
        Dictionary for elements ...

    """

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
        """Return the simulation instance"""
        return self._simulation

    ##############################################

    def _get_item(self, name):

        if name in self.nodes:
            return self.nodes[name]
        elif name in self.branches:
            return self.branches[name]
        elif name in self.elements:
            return self.elements[name]
        else:
            raise IndexError(name)

    ##############################################

    def __getitem__(self, name):

        try:
            return self._get_item(name)
        except IndexError:
            return self._get_item(name.lower())

    ##############################################

    @staticmethod
    def _format_dict(d):

        return os.linesep.join([' '*2 + str(x) for x in d])

    ##############################################

    def __getattr__(self, name):

        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(name + os.linesep +
                                 'Nodes :' + os.linesep + self._format_dict(self.nodes) + os.linesep +
                                 'Branches :' + os.linesep + self._format_dict(self.branches) + os.linesep +
                                 'Elements :' + os.linesep + self._format_dict(self.elements))

####################################################################################################

class OperatingPoint(Analysis):
    """This class implements an operating point analysis."""
    pass

####################################################################################################

class SensitivityAnalysis(Analysis):

    """This class implements an sensitivity analysis."""

    ##############################################

    def __init__(self, simulation, elements):

        super().__init__(simulation=simulation, elements=elements)

####################################################################################################

class DcAnalysis(Analysis):

    """This class implements a DC analysis.

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
        """Return an Numpy array for the sweep abscissa"""
        return self._sweep

####################################################################################################

class AcAnalysis(Analysis):

    """This class implements an AC analysis."""

    ##############################################

    def __init__(self, simulation, frequency, nodes, branches):

        super().__init__(simulation=simulation, nodes=nodes, branches=branches)

        self._frequency = frequency

    ##############################################

    @property
    def frequency(self):
        """Return an Numpy array for the frequency abscissa"""
        return self._frequency

####################################################################################################

class TransientAnalysis(Analysis):

    """This class implements a transient analysis."""

    ##############################################

    def __init__(self, simulation, time, nodes, branches):

        super().__init__(simulation=simulation, nodes=nodes, branches=branches)

        self._time = time

    ##############################################

    @property
    def time(self):
        """Return an Numpy array for the time abscissa"""
        return self._time
