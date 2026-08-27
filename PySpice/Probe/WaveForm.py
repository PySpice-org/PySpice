####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

__ALL__ = [
    'AcAnalysis',
    'Analysis',
    'DcAnalysis',
    'DistortionAnalysis',
    'NoiseAnalysis',
    'OperatingPoint',
    'PoleZeroAnalysis',
    'SensitivityAnalysis',
    'TransferFunctionAnalysis',
    'TransientAnalysis',
    'WaveForm',
]

####################################################################################################
#
# Note:
#   PR #136 has non understood changes
#     https://github.com/FabriceSalvaire/PySpice/pull/136/files
#
####################################################################################################

####################################################################################################

"""This module implements classes to handle analysis output.

"""

# https://numpy.org/doc/stable/user/basics.subclassing.html#basics-subclassing

####################################################################################################

from typing import TYPE_CHECKING
import logging
import os

from PySpice.Unit.Unit import PrefixedUnit, UnitValues

if TYPE_CHECKING:
    import numpy as np
    from PySpice.Spice.Simulation import Simulation

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class WaveForm(UnitValues):

    """This class implements waveform on top of a Numpy Array.

    Public Attributes:

      :attr:`name`

      :attr:`unit`

      :attr:`title`

      :attr:`abscissa`
        Numpy array of the analysis abscissa

    """

    _logger = _module_logger.getChild('WaveForm')

    ##############################################

    @classmethod
    def from_unit_values(
        cls,
        name: str,
        array: UnitValues,
        title: str = None,
        abscissa: 'WaveForm' = None,
    ) -> 'WaveForm':
        obj = cls(
            name,
            array.prefixed_unit,
            array.shape,
            dtype=array.dtype,
            title=title,
            abscissa=abscissa,
        )
        obj[...] = array[...]
        return obj

    ##############################################

    @classmethod
    def from_array(
        cls,
        name: str,
        array: 'np.ndarray',
        title: str = None,
        abscissa: 'WaveForm' = None,
    ) -> 'WaveForm':
        # Fixme: ok ???
        #  prefixed_unit is None
        obj = cls(name, None, array.shape, title=title, abscissa=abscissa)
        obj[...] = array[...]
        return obj

    ##############################################

    def __new__(
        cls,
        name: str,
        prefixed_unit: PrefixedUnit,
        shape,
        dtype=float, buffer=None, offset=0, strides=None, order=None,
        title: str = None,
        abscissa: 'WaveForm' = None,
    ):
        # Called first
        # cls._logger.info(str((cls, prefixed_unit, shape, dtype, buffer, offset, strides, order)))

        # call UnitValues.__new__(...)
        obj = super(WaveForm, cls).__new__(cls, prefixed_unit, shape, dtype, buffer, offset, strides, order)
        # obj = np.asarray(data).view(cls)

        # extra attributes
        obj._name = str(name)
        obj._title = title   # str(title)
        obj._abscissa = abscissa    # Numpy array

        return obj

    ##############################################

    def __array_finalize__(self, obj) -> None:
        # Called after __new__
        # self._logger.info('')

        # Fixme: ??? else _prefixed_unit is not set
        super().__array_finalize__(obj)

        # if obj is None:
        #     return

        # extra attributes
        self._name = getattr(obj, 'name', None)
        self._title = getattr(obj, 'title', None)
        self._abscissa = getattr(obj, 'abscissa', None)

    ##############################################

    # def __init__(self, name, prefixed_unit, shape,
    #              dtype=float, buffer=None, offset=0, strides=None, order=None,
    #              title=None, abscissa=None):
    #     # Called last
    #     self._logger.info('')

    ##############################################

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        result = super().__array_ufunc__(ufunc, method, *inputs, **kwargs)
        # self._logger.info("result\n{}".format(result))
        if isinstance(result, UnitValues):
            return self.from_unit_values(name='', array=result, title='', abscissa=self._abscissa)
        else:
            return result  # e.g. foo <= 0

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def abscissa(self) -> 'WaveForm':
        return self._abscissa

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value is not None:
            self._title = str(value)
        else:
            self._title = None

    ##############################################

    def __repr__(self) -> str:
        _ = super().__str__()
        return '{self.__class__.__name__} {self._name} {_}'

    ##############################################

    def __str__(self) -> str:
        if self._title is not None:
            return self._title
        else:
            return self._name

    ##############################################

    def str_data(self) -> str:
        # Fixme: ok ???
        return repr(self.as_ndarray())

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

    _logger = _module_logger.getChild('Analysis')

    ##############################################

    def __init__(
        self,
        simulation: 'Simulation',
        nodes: list[WaveForm] = (),
        branches: list[WaveForm] = (),
        elements: list[WaveForm] = (),
        internal_parameters: list[WaveForm] = ()
    ) -> None:
        # Fixme: branches are elements in fact, and elements is not yet supported ...
        self._simulation = simulation
        # Fixme: to func?
        self._nodes = {_.name: _ for _ in nodes}
        self._branches = {_.name: _ for _ in branches}
        self._elements = {_.name: _ for _ in elements}
        self._internal_parameters = {_.name: _ for _ in internal_parameters}

    ##############################################

    def __setstate__(self, state: dict) -> None:
        # Fixme: useful ???
        self.__dict__.update(state)

    ##############################################

    @property
    def simulation(self) -> 'Simulation':
        """Return the simulation instance"""
        return self._simulation

    @property
    def nodes(self) -> list[WaveForm]:
        return self._nodes

    @property
    def branches(self) -> list[WaveForm]:
        return self._branches

    @property
    def elements(self) -> list[WaveForm]:
        return self._elements

    @property
    def internal_parameters(self) -> list[WaveForm]:
        return self._internal_parameters

    ##############################################

    def _get_item(self, name: str) -> WaveForm:
        # Fixme: cache dict ???
        if name in self._nodes:
            return self._nodes[name]
        elif name in self._branches:
            return self._branches[name]
        elif name in self._elements:
            return self._elements[name]
        elif name in self._internal_parameters:
            return self._internal_parameters[name]
        else:
            raise IndexError(name)

    ##############################################

    def __getitem__(self, name: str) -> WaveForm:
        # handle analysis['foo']
        try:
            return self._get_item(name)
        except IndexError:
            return self._get_item(name.lower())

    ##############################################

    @staticmethod
    def _format_dict(d: dict) -> str:
        return NEWLINE.join([' '*2 + str(x) for x in d])

    ##############################################

    def __getattr__(self, name: str) -> WaveForm:
        # handle analysis.foo
        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(
                name + NEWLINE +
                'Nodes :' + NEWLINE + self._format_dict(self._nodes) + NEWLINE +
                'Branches :' + NEWLINE + self._format_dict(self._branches) + NEWLINE +
                'Elements :' + NEWLINE + self._format_dict(self._elements) + NEWLINE +
                'Internal Parameters :' + NEWLINE + self._format_dict(self._internal_parameters)
            )

####################################################################################################

class OperatingPoint(Analysis):
    """This class implements an operating point analysis."""

####################################################################################################

class SensitivityAnalysis(Analysis):

    """This class implements an sensitivity analysis."""

    ##############################################

    def __init__(self, simulation: 'Simulation', elements, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            elements=elements,
            internal_parameters=internal_parameters,
        )

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

    def __init__(self, simulation: 'Simulation', sweep, nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )
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

    def __init__(self, simulation: 'Simulation', frequency, nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )
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

    def __init__(self, simulation: 'Simulation', time, nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )
        self._time = time

    ##############################################

    @property
    def time(self):
        """Return an Numpy array for the time abscissa"""
        return self._time

####################################################################################################

class PoleZeroAnalysis(Analysis):

    """This class implements a Pole-Zero analysis."""

    ##############################################

    def __init__(self, simulation: 'Simulation', nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation, nodes=nodes, branches=branches,
            internal_parameters=internal_parameters,
        )

####################################################################################################

class NoiseAnalysis(Analysis):

    """This class implements Noise analysis."""

    ##############################################

    def __init__(self, simulation: 'Simulation', nodes, branches, internal_parameters):
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )

####################################################################################################

class DistortionAnalysis(Analysis):

    """This class implements Distortion analysis."""

    ##############################################

    def __init__(self, simulation: 'Simulation', frequency, nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )
        self._frequency = frequency

    ##############################################

    @property
    def frequency(self):
        """Return an Numpy array for the frequency abscissa"""
        return self._frequency

####################################################################################################

class TransferFunctionAnalysis(Analysis):

    """This class implements Transfer Function (TF) analysis."""

    ##############################################

    def __init__(self, simulation: 'Simulation', nodes, branches, internal_parameters) -> None:
        super().__init__(
            simulation=simulation,
            nodes=nodes,
            branches=branches,
            internal_parameters=internal_parameters,
        )
