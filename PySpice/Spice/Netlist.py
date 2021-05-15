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
import keyword
import logging
import os

# import networkx

####################################################################################################

from ..Tools.StringTools import join_lines, join_list

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Node:

    """This class implements a node in the circuit. It stores a reference to the pins connected to
    the node.

    """

    _logger = _module_logger.getChild('Node')

    ##############################################

    def __init__(self, netlist, name):

        if keyword.iskeyword(name):
            self._logger.warning(f"Node name '{name}' is a Python keyword")

    ##############################################

        self._netlist = netlist
        self._name = str(name)

        self._pins = set()

    ##############################################

    def __repr__(self):
        return f'Node {self._name}'

    def __str__(self):
        return self._name

    ##############################################

    @property
    def netlist(self):
        return self._netlist

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._netlist._update_node_name(self, value)   # update nodes dict
        self._name = value

    @property
    def pins(self):
        return self._pins

    ##############################################

    @property
    def is_ground_node(self):
        return self._name in ('0', 'gnd')

    ##############################################

    def __bool__(self):
        return bool(self._pins)

    ##############################################

    def __iter__(self):
        return iter(self._pins)

    ##############################################

    def connect(self, pin):
        if pin not in self._pins:
            self._pins.add(pin)
        else:
            # Fixme: could just warn ???
            raise ValueError(f"Pin {pin} is already connected to node {self}")

    ##############################################

    def disconnect(self, pin):
        self._pins.remove(pin)

####################################################################################################

class Netlist:

    """This class implements a base class for a netlist.

    .. note:: This class is completed with element shortcuts when the module is loaded.

    """

    _logger = _module_logger.getChild('Netlist')

    ##############################################

    def __init__(self):

        self._ground_name = 0
        self._nodes = {}
        self._ground_node = self._add_node(self._ground_name)

        self._subcircuits = OrderedDict()   # to keep the declaration order
        self._elements = OrderedDict()   # to keep the declaration order
        self._models = {}

        self.raw_spice = ''

        # self._graph = networkx.Graph()

    ##############################################

    def __setstate__(self, state):
        self.__dict__.update(state)

    ##############################################

    def copy_to(self, netlist):

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
    def gnd(self):
        return self._ground

    @property
    def nodes(self):
        return self._nodes.values()

    @property
    def node_names(self):
        return self._nodes.keys()

    @property
    def elements(self):
        return self._elements.values()

    @property
    def element_names(self):
        return self._elements.keys()

    @property
    def models(self):
        return self._models.values()

    @property
    def model_names(self):
        return self._models.keys()

    @property
    def subcircuits(self):
        return self._subcircuits.values()

    @property
    def subcircuit_names(self):
        return self._subcircuits.keys()

    ##############################################

    def element(self, name):
        return self._elements[name]

    def model(self, name):
        return self._models[name]

    def node(self, name):
        return self._nodes[name]

    ##############################################

    def __getitem__(self, attribute_name):

        if attribute_name in self._elements:
            return self.element(attribute_name)
        elif attribute_name in self._models:
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

    def _add_node(self, node_name):
        node_name = str(node_name)
        if node_name not in self._nodes:
            node = Node(self, node_name)
            self._nodes[node_name] = node
            return node
        else:
            raise ValueError(f"Node {node_name} is already defined")

    ##############################################

    def _update_node_name(self, node, new_name):
        if node.name not in self._nodes:
            # should not happen
            raise ValueError("Unknown node")
        del self._nodes[node.name]
        self._nodes[new_name] = node

    ##############################################

    def get_node(self, node, create=False):
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

    def has_ground_node(self):
        return bool(self._ground_node)

    ##############################################

    def _add_element(self, element):
        """Add an element."""
        if element.name not in self._elements:
            self._elements[element.name] = element
        else:
            raise NameError(f"Element name {element.name} is already defined")

    ##############################################

    def _remove_element(self, element):
        try:
            del self._elements[element.name]
        except KeyError:
            raise NameError(f"Cannot remove undefined element {element}")

    ##############################################

    def model(self, name, modele_type, **parameters):
        """Add a model."""
        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model
        else:
            raise NameError(f"Model name {name} is already defined")

        return model

    ##############################################

    def subcircuit(self, subcircuit):
        """Add a sub-circuit."""
        # Fixme: subcircuit is a class
        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def __str__(self):
        """ Return the formatted list of element and model definitions. """
        # Fixme: order ???
        netlist = self._str_raw_spice()
        netlist += self._str_subcircuits() # before elements
        netlist += self._str_elements()
        netlist += self._str_models()
        return netlist

    ##############################################

    def _str_elements(self):
        elements = [element for element in self.elements if element.enabled]
        return join_lines(elements) + os.linesep

    ##############################################

    def _str_models(self):
        if self._models:
            return join_lines(self.models) + os.linesep
        else:
            return ''

    ##############################################

    def _str_subcircuits(self):
        if self._subcircuits:
            return join_lines(self.subcircuits)
        else:
            return ''

    ##############################################

    def _str_raw_spice(self):
        netlist = self.raw_spice
        if netlist and not netlist.endswith(os.linesep):
            netlist += os.linesep
        return netlist

####################################################################################################

class SubCircuit(Netlist):

    """This class implements a sub-cicuit netlist."""

    ##############################################

    def __init__(self, name, *nodes, **kwargs):

        if len(set(nodes)) != len(nodes):
            raise ValueError(f"Duplicated nodes in {nodes}")

        super().__init__()

        self._name = str(name)
        self._external_nodes = nodes

        # Fixme: ok ?
        self._ground = kwargs.get('ground', 0)
        if 'ground' in kwargs:
            del kwargs['ground']

        self._parameters = kwargs

    ##############################################

    def clone(self, name=None):

        if name is None:
            name = self._name

        # Fixme: clone parameters ???
        kwargs = dict(self._parameters)
        kwargs['ground'] = self._ground

        subcircuit = self.__class__(name, list(self._external_nodes), **kwargs)
        self.copy_to(subcircuit)

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def external_nodes(self):
        return self._external_nodes

    @property
    def parameters(self):
        """Parameters"""
        return self._parameters

    ##############################################

    def check_nodes(self):

        """Check for dangling nodes in the subcircuit."""

        nodes = self._external_nodes
        connected_nodes = set()
        for element in self.elements:
            connected_nodes.add(nodes & element.nodes)
        not_connected_nodes = nodes - connected_nodes
        if not_connected_nodes:
            raise NameError(f"SubCircuit Nodes {not_connected_nodes} are not connected")

    ##############################################

    def __str__(self):
        """Return the formatted subcircuit definition."""
        nodes = join_list(self._external_nodes)
        parameters = join_list(['f{key}={value}'
                                for key, value in self._parameters.items()])
        netlist = '.subckt ' + join_list((self._name, nodes, parameters)) + os.linesep
        netlist += super().__str__()
        netlist += '.ends ' + self._name + os.linesep
        return netlist

####################################################################################################

class SubCircuitFactory(SubCircuit):

    NAME = None
    NODES = None

    ##############################################

    def __init__(self, **kwargs):
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

    def __init__(self, title,
                 ground=0,   # Fixme: gnd = 0
                 global_nodes=(),
                 ):

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

    def clone(self, title=None):

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

    def include(self, path):
        """Include a file."""
        if path not in self._includes:
            self._includes.append(path)
        else:
            self._logger.warn("Duplicated include")

    ##############################################

    def lib(self, name, section=None):
        """Load a library."""
        v = (name, section)
        if v not in self._libs:
            self._libs.append(v)
        else:
            self._logger.warn(f"Duplicated lib {v}")

    ##############################################

    def parameter(self, name, expression):
        """Set a parameter."""
        self._parameters[str(name)] = str(expression)

    ##############################################

    def str(self, simulator=None):
        """Return the formatted desk.

        :param simulator: simulator instance to select the flavour of a Spice library

        """
        # if not self.has_ground_node():
        #     raise NameError("Circuit don't have ground node")
        netlist = self._str_title()
        netlist += self._str_includes(simulator)
        netlist += self._str_libs(simulator)
        netlist += self._str_globals()
        netlist += self._str_parameters()
        netlist += super().__str__()
        return netlist

    ##############################################

    def _str_title(self):
        return f'.title {self.title}' + os.linesep

    ##############################################

    def _str_includes(self, simulator=None):
        if self._includes:
            # ngspice don't like // in path, thus ensure we write real paths
            real_paths = []
            for path in self._includes:
                path = Path(str(path)).resolve()
                if simulator:
                    path_flavour = Path(str(path) + '@' + simulator)
                    if path_flavour.exists():
                        path = path_flavour
                real_paths.append(path)

            return join_lines(real_paths, prefix='.include ') + os.linesep
        else:
            return ''

    ##############################################

    def _str_libs(self, simulator=None):
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
            return os.linesep.join(libs) + os.linesep
        else:
            return ''

    ##############################################

    def _str_globals(self):
        if self._global_nodes:
            return '.global ' + join_list(self._global_nodes) + os.linesep
        else:
            return ''

    ##############################################

    def _str_parameters(self):
        if self._parameters:
            return ''.join([f'.param {key}={value}' + os.linesep
                            for key, value in self._parameters.items()])
        else:
            return ''

    ##############################################

    def __str__(self):
        return self.str(simulator=None)

    ##############################################

    def str_end(self):
        return str(self) + '.end' + os.linesep

    ##############################################

    def simulator(self, *args, **kwargs):
        # return CircuitSimulator.factory(self, *args, **kwargs)
        raise NameError("Deprecated API")
