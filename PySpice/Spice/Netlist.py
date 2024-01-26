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

"""This modules implements circuit and subcircuit.

The definition of a netlist follows the same conventions as SPICE. For example this SPICE netlist
is translated to Python like this:

.. code-block:: spice

    .title Voltage Divider
    Vinput in 0 10V
    R1 in out 9k
    R2 out 0 1k
    .end

.. code-block:: python3

    circuit = Circuit('Voltage Divider')
   circuit.V('input', 'in', circuit.gnd, 10)
    circuit.R(1, 'in', 'out', kilo(9))
    circuit.R(2, 'out', circuit.gnd, kilo(1))

or as a class definition:

.. code-block:: python3

      class VoltageDivider(Circuit):

          def __init__(self, **kwargs):

              super().__init__(title='Voltage Divider', **kwargs)

              self.V('input', 'in', self.gnd, '10V')
              self.R(1, 'in', 'out', kilo(9))
              self.R(2, 'out', self.gnd, kilo(1))

The circuit attribute :attr:`gnd` represents the ground of the circuit or subcircuit, usually set to
0.

We can get an element or a model using its name using these two possibilities::

    circuit['R1'] # dictionary style
    circuit.R1    # attribute style

The dictionary style always works, but the attribute only works if it complies with the Python
syntax, i.e. the element or model name is a valide attribute name (identifier), i.e. starting by a
letter and not a keyword like 'in', cf. `Python Language Reference
<https://docs.python.org/2/reference/lexical_analysis.html>`_.

We can update an element parameter like this::

    circuit.R1.resistance = kilo(1)

To simulate the circuit, we must create a simulator instance using the :meth:`Circuit.simulator`::

    simulator = circuit.simulator()

"""

####################################################################################################

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Self, Union
import keyword
import logging
import os

# import networkx

####################################################################################################

from PySpice.Tools.TextBuffer import TextBuffer
# Fixme: circular import
# from . import Library
from .DeviceModel import DeviceModel
from .Element import Pin, Element
from .StringTools import join_list, prefix_lines

if TYPE_CHECKING:
    from .Simulator import Simulator
    from . import Library

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node:

    """This class implements a node in the circuit.

    It stores a reference to the pins connected to the node.

    """

    _logger = _module_logger.getChild('Node')

    SPICE_GROUND_NUMBER = 0
    SPICE_GROUND_NAME = str(SPICE_GROUND_NUMBER)

    ##############################################

    @classmethod
    def _warn_iskeyword(cls, name: str) -> None:
        if keyword.iskeyword(name):
            cls._logger.warning(f"Node name '{name}' is a Python keyword")

    ##############################################

    def __init__(self, netlist: 'Netlist', name: str) -> None:
        self._warn_iskeyword(name)
        self._netlist = netlist
        self._name = str(name)
        self._pins = set()

    ##############################################

    def __repr__(self) -> str:
        return f'Node {self._name}'

    def __str__(self) -> str:
        return self._name

    ##############################################

    @property
    def netlist(self) -> 'Netlist':
        return self._netlist

    @property
    def name(self) -> int | str:
        return self._name

    @name.setter
    def name(self, value: int | str) -> bool:
        self._warn_iskeyword(value)
        self._name = value
        # update nodes dict
        self._netlist._update_node_name(self, value)

    @property
    def is_ground_node(self) -> bool:
        return self._name in (Node.SPICE_GROUND_NAME, 'gnd')

    ##############################################

    def __bool__(self) -> bool:
        return bool(self._pins)

    def __len__(self) -> int:
        return len(self._pins)

    def __iter__(self) -> Iterator[Pin]:
        return iter(self._pins)

    @property
    def pins(self) -> Iterator[Pin]:
        # Fixme: iter ?
        return iter(self._pins)

    def __contains__(self, pin: Pin) -> bool:
        return pin in self._pins

    ##############################################

    def connect(self, pin: Pin) -> None:
        self._logger.info(f"Connect {pin} => {self}")
        if pin not in self:
            self._pins.add(pin)
        else:
            # Fixme: could just warn ???
            raise ValueError(f"Pin {pin} is already connected to node {self}")

    ##############################################

    def disconnect(self, pin: Pin) -> None:
        self._logger.info(f"Disconnect {pin}")
        self._pins.remove(pin)

    ##############################################

    def merge(self, node: 'Node') -> None:
        self._logger.info(f"Merge {self} and {node}")
        for pin in list(node.pins):
            pin.disconnect()
            pin.connect(self)
        self._netlist._del_node(node)

    ##############################################

    def __iadd__(self, args: Union['Node', Pin, list[Union['Node', Pin]]]) -> Self:
        """Connect a node, a pin or a list of them to the node."""
        if isinstance(args, (Node, Pin)):
            args = (args,)
        for obj in args:
            if isinstance(obj, Node):
                # node <=> node
                self.merge(obj)
            elif isinstance(obj, Pin):
                # node <= pin
                if obj.connected:
                    self.merge(obj.node)
                else:
                    obj.connect(self)
            else:
                raise ValueError(f"Invalid object {type(obj)}")
        return self

####################################################################################################

class Netlist:

    """This class implements a base class for a netlist.

    .. note:: This class is completed with element shortcuts when the module is loaded.

    """

    _logger = _module_logger.getChild('Netlist')

    ##############################################

    def __init__(self) -> None:
        self._nodes = {}
        self._ground_name = Node.SPICE_GROUND_NAME   # Fixme: just here
        self._ground_node = self._add_node(self._ground_name)
        self._ground = None   # Fixme: purpose ???

        self._subcircuits = OrderedDict()   # to keep the declaration order
        self._elements = OrderedDict()   # to keep the declaration order
        self._models = {}

        self.raw_spice = ''

        # self._graph = networkx.Graph()

    ##############################################

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)

    ##############################################

    def copy_to(self, netlist: 'Netlist') -> 'Netlist':
        for subcircuit in self.subcircuits:
            netlist.subcircuit(subcircuit)
        for element in self.elements:
            element.copy_to(netlist)
        for name, model in self._models.items():
            netlist._models[name] = model.clone()
        netlist.raw_spice = str(self.raw_spice)
        return netlist

    ##############################################

    @property
    def gnd(self) -> int | str:
        # Fixme: purpose ???
        # return self._ground
        return self._ground_node

    # Note:
    #   circuit.gnd += ...
    #   call a setter...

    @property
    def nodes(self) -> Iterator[Node]:
        return self._nodes.values()

    @property
    def node_names(self) -> Iterator[str]:
        return self._nodes.keys()

    @property
    def elements(self) -> Iterator[Element]:
        return self._elements.values()

    @property
    def element_names(self) -> Iterator[str]:
        return self._elements.keys()

    @property
    def models(self) -> Iterator[DeviceModel]:
        return self._models.values()

    @property
    def model_names(self) -> Iterator[str]:
        return self._models.keys()

    @property
    def subcircuits(self) -> Iterator['SubCircuit']:
        return self._subcircuits.values()

    @property
    def subcircuit_names(self) -> Iterator[str]:
        return self._subcircuits.keys()

    ##############################################

    def element(self, name: str) -> Element:
        return self._elements[name]

    # Fixme: clash with
    #    def model(self, name, modele_type, **parameters):
    # def model(self, name):
    #     return self._models[name]

    # Fixme: versus get node ???
    def node(self, name: str) -> Node:
        return self._nodes[str(name)]

    ##############################################

    def __getitem__(self, attribute_name) -> Element:
        if attribute_name in self._elements:
            return self.element(attribute_name)
        elif attribute_name in self._models:
            # Fixme: error missing modele_type ?
            return self.model(attribute_name)
        # Fixme: subcircuits
        elif attribute_name in self._nodes:
            return self.node(attribute_name)
        else:
            raise IndexError(attribute_name)   # KeyError

    ##############################################

    def __getattr__(self, attribute_name):
        try:
            return self.__getitem__(attribute_name)
        except IndexError:
            raise AttributeError(attribute_name)

    ##############################################

    def _add_node(self, node_name: int | str) -> Node:
        node_name = str(node_name)
        if node_name not in self._nodes:
            self._logger.info(f'Create node "{node_name}"')
            node = Node(self, node_name)
            self._nodes[node_name] = node
            return node
        else:
            raise ValueError(f"Node {node_name} is already defined")

    ##############################################

    def _del_node(self, node) -> None:
        del self._nodes[node.name]

    ##############################################

    def _update_node_name(self, node, new_name) -> None:
        """Update the node's map for the new node's name"""
        # Fixme: check node is None ???
        if node.name not in self._nodes:
            # should not happen
            raise ValueError(f"Unknown node {node}")
        self._nodes[new_name] = self._nodes.pop(node.name)

    ##############################################

    def get_node(self, node: Node | int | str, create: bool = False) -> Node:
        """Return a node. `node` can be a node instance or node name.  A node is created if `create` is set
        and the node don't yet exist.

        """
        # Fixme: dangling...
        if node is None:
            return None
        # Fixme: always ok ???
        if isinstance(node, Node):
            return node
        else:
            str_node = str(node)
            if str_node in self._nodes:
                return self._nodes[str_node]
            elif create:
                return self._add_node(str_node)
            else:
                raise KeyError(f"Node {node} doesn't exists")

    ##############################################

    def has_ground_node(self) -> bool:
        """Test if ground node is connected"""
        return bool(self._ground_node)

    ##############################################

    def _add_element(self, element: Element) -> None:
        """Add an element."""
        if element.name not in self._elements:
            self._elements[element.name] = element
        else:
            raise NameError(f"Element name {element.name} is already defined")

    ##############################################

    def _remove_element(self, element: Element) -> None:
        try:
            del self._elements[element.name]
        except KeyError:
            raise NameError(f"Cannot remove undefined element {element}")

    ##############################################

    def model(self, name: str, modele_type: str, **parameters) -> DeviceModel:
        """Add a model."""
        _ = DeviceModel(name, modele_type, **parameters)
        if _.name not in self._models:
            self._models[_.name] = _
        else:
            raise NameError(f"Model name {name} is already defined")
        return _

    ##############################################

    def subcircuit(self, subcircuit: 'SubCircuit') -> None:
        """Add a sub-circuit."""
        # Fixme: subcircuit is a class
        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def __str__(self) -> str:
        """ Return the formatted list of element and model definitions. """
        # Fixme: order ???
        netlist = TextBuffer()
        netlist += self._str_raw_spice()
        netlist += self._str_subcircuits()   # before elements
        netlist += self._str_elements()
        netlist += self._str_models()
        return str(netlist)

    ##############################################

    def _str_raw_spice(self) -> str:
        return self.raw_spice.rstrip()

    ##############################################

    def _str_subcircuits(self) -> list:
        # ensure list instead of odict_values
        return list(self.subcircuits)

    ##############################################

    def _str_elements(self) -> list:
        return [element for element in self.elements if element.enabled]

    ##############################################

    def _str_models(self) -> list:
        # ensure list instead of dict_values
        return list(self.models)

####################################################################################################

class SubCircuit(Netlist):

    """This class implements a sub-cicuit netlist."""

    ##############################################

    def __init__(self, name: str, *nodes, **kwargs) -> None:
        if len(set(nodes)) != len(nodes):
            raise ValueError(f"Duplicated nodes in {nodes}")

        super().__init__()

        self._name = str(name)
        self._external_nodes = nodes

        # Fixme: ok ?
        self._ground = kwargs.pop('ground', Node.SPICE_GROUND_NUMBER)

        self._parameters = kwargs

    ##############################################

    def clone(self, name: str = None) -> None:
        if name is None:
            name = self._name

        # Fixme: clone parameters ???
        kwargs = dict(self._parameters)
        kwargs['ground'] = self._ground

        subcircuit = self.__class__(name, list(self._external_nodes), **kwargs)
        self.copy_to(subcircuit)

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def external_nodes(self) -> list[Node]:
        return self._external_nodes

    @property
    def parameters(self) -> dict:
        """Parameters"""
        return self._parameters

    ##############################################

    def check_nodes(self) -> None:
        """Check for dangling nodes in the subcircuit."""
        nodes = self._external_nodes
        connected_nodes = set()
        for element in self.elements:
            connected_nodes.add(nodes & element.nodes)
        not_connected_nodes = nodes - connected_nodes
        if not_connected_nodes:
            raise NameError(f"SubCircuit Nodes {not_connected_nodes} are not connected")

    ##############################################

    def __str__(self) -> str:
        """Return the formatted subcircuit definition."""
        netlist = TextBuffer()
        nodes = join_list(self._external_nodes)
        parameters = join_list(['f{key}={value}'
                                for key, value in self._parameters.items()])
        netlist += '.subckt ' + join_list((self._name, nodes, parameters))
        netlist += super().__str__()
        netlist += '.ends ' + self._name
        return str(netlist)

####################################################################################################

class SubCircuitFactory(SubCircuit):

    NAME = None
    NODES = None

    ##############################################

    def __init__(self, **kwargs) -> None:
        super().__init__(self.NAME, *self.NODES, **kwargs)

####################################################################################################

class Circuit(Netlist):

    """This class implements a cicuit netlist.

    To get the corresponding Spice netlist use::

       circuit = Circuit()
       ...
       str(circuit)

    """

    _logger = _module_logger.getChild('Circuit')

    ##############################################

    def __init__(
        self,
        title: str,   # pylint issue
        ground: int | str = Node.SPICE_GROUND_NUMBER,   # Fixme: gnd = Node.SPICE_GROUND_NUMBER
        global_nodes: list[int | str] = (),
    ) -> None:
        super().__init__()

        self.title = str(title)
        self._ground = ground
        self._global_nodes = set(global_nodes)   # .global
        self._includes = []   # .include
        self._libs = []   # .lib, contains a (name, section) tuple
        self._parameters = {}   # .param

        # Fixme: not implemented
        #  .csparam
        #  .func
        #  .if

    ##############################################

    def clone(self, title: str = None) -> 'Circuit':
        if title is None:
            title = self.title

        circuit = self.__class__(title, self._ground, set(self._global_nodes))
        self.copy_to(circuit)

        for include in self._includes:
            circuit.include(include)
        for name, value in self._parameters.items():
            self.parameter(name, value)

        return circuit

    ##############################################

    @property
    def includes(self) -> Iterator[Path]:
        return iter(self._includes)

    ##############################################

    def include(self, path: Union[Path, str, 'Library.SubCircuit'], warn: bool = True) -> None:
        """Include a file."""
        # Fixme: str(path) ?
        # Fixme: circular import...
        from . import Library
        if isinstance(path, Library.Subcircuit):
            path = path.path
        path = Path(path).resolve()
        if path not in self._includes:
            self._includes.append(path)
        elif warn:
            self._logger.warn(f"Duplicated include {path}")

    ##############################################

    def lib(self, name: str, section: str = None) -> None:
        """Load a library."""
        v = (name, section)
        if v not in self._libs:
            self._libs.append(v)
        else:
            self._logger.warn(f"Duplicated lib {v}")

    ##############################################

    def parameter(self, name: str, expression: str) -> None:
        """Set a parameter."""
        self._parameters[str(name)] = str(expression)

    ##############################################

    def str(self, simulator: 'Simulator' = None) -> str:
        """Return the formatted desk.

        :param simulator: simulator instance to select the flavour of a Spice library

        """
        # if not self.has_ground_node():
        #     raise NameError("Circuit don't have ground node")
        _ = TextBuffer()
        _ += self._str_title()
        _ += self._str_includes(simulator)
        _ += self._str_libs(simulator)
        _ += self._str_globals()
        _ += self._str_parameters()
        _ += super().__str__()
        return str(_) + os.linesep    # Fixme: linesep here ???

    ##############################################

    def _str_title(self) -> str:
        return f'.title {self.title}'

    ##############################################

    def _str_includes(self, simulator: 'Simulator' = None) -> list[str]:
        if self._includes:
            # ngspice don't like // in path, thus ensure we write real paths
            real_paths = []
            for path in self._includes:
                if simulator:
                    path_flavour = path.parent.joinpath(f"{path.name}@{simulator}")
                    if path_flavour.exists():
                        path = path_flavour
                real_paths.append(path)
            return prefix_lines(real_paths, prefix='.include ')
        else:
            return None

    ##############################################

    def _str_libs(self, simulator: 'Simulator' = None) -> list[str]:
        if self._libs:
            libs = []
            for lib, section in self._libs:
                lib = Path(str(lib)).resolve()
                if simulator:
                    lib_flavour = Path(f"{lib}@{simulator}")
                    if lib_flavour.exists():
                        lib = lib_flavour
                s = f".lib {lib}"
                if section:
                    s += f" {section}"
                libs.append(s)
            return libs
        else:
            return None

    ##############################################

    def _str_globals(self) -> str:
        if self._global_nodes:
            return '.global ' + join_list(self._global_nodes)
        else:
            return None

    ##############################################

    def _str_parameters(self) -> list[str]:
        if self._parameters:
            return [f'.param {key}={value}' for key, value in self._parameters.items()]
        else:
            return None

    ##############################################

    def __str__(self) -> str:
        return self.str(simulator=None)

    ##############################################

    def str_end(self) -> str:
        return str(self) + '.end'

    ##############################################

    def simulator(self, *args, **kwargs):
        # return CircuitSimulator.factory(self, *args, **kwargs)
        raise NameError("Deprecated API")
