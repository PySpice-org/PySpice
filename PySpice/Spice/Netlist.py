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

    circuit['R1'] # dictionnary style
    circuit.R1    # attribute style

The dictionnary style always works, but the attribute only works if it complies with the Python
syntax, i.e. the element or model name is a valide attribute name (identifier), i.e. starting by a
letter and not a keyword like 'in', cf. `Python Language Reference
<https://docs.python.org/2/reference/lexical_analysis.html>`_.

We can update an element parameter like this::

    circuit.R1.resistance = kilo(1)

To simulate the circuit, we must create a simulator instance using the :meth:`Circuit.simulator`::

    simulator = circuit.simulator()

"""

####################################################################################################
#
# Graph:
#   dipole
#   n-pole: transistor (be, bc) ?
#
# circuit -> element -> node
#   circuit.Q1.b
#   Element -> ElementQ
#   use prefix?
#
####################################################################################################

####################################################################################################

from collections import OrderedDict
import keyword
import logging
import os

# import networkx

####################################################################################################

from ..Tools.StringTools import join_lines, join_list, join_dict
from .ElementParameter import (ParameterDescriptor,
                               PositionalElementParameter,
                               FlagParameter, KeyValueParameter)
from .Simulation import CircuitSimulator, SubprocessCircuitSimulator, NgSpiceSharedCircuitSimulator

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class DeviceModel:

    """ This class implements a device model.

    Ngspice model types:

    +------+-------------------------------+
    | Code + Model Type                    |
    +------+-------------------------------+
    | R    + Semiconductor resistor model  |
    +------+-------------------------------+
    | C    + Semiconductor capacitor model |
    +------+-------------------------------+
    | L    + Inductor model                |
    +------+-------------------------------+
    | SW   + Voltage controlled switch     |
    +------+-------------------------------+
    | CSW  + Current controlled switch     |
    +------+-------------------------------+
    | URC  + Uniform distributed RC model  |
    +------+-------------------------------+
    | LTRA + Lossy transmission line model |
    +------+-------------------------------+
    | D    + Diode model                   |
    +------+-------------------------------+
    | NPN  + NPN BJT model                 |
    +------+-------------------------------+
    | PNP  + PNP BJT model                 |
    +------+-------------------------------+
    | NJF  + N-channel JFET model          |
    +------+-------------------------------+
    | PJF  + P-channel JFET model          |
    +------+-------------------------------+
    | NMOS + N-channel MOSFET model        |
    +------+-------------------------------+
    | PMOS + P-channel MOSFET model        |
    +------+-------------------------------+
    | NMF  + N-channel MESFET model        |
    +------+-------------------------------+
    | PMF  + P-channel MESFET model        |
    +------+-------------------------------+

    """

    ##############################################

    def __init__(self, name, modele_type, **parameters):

        self._name = str(name)
        self._model_type = str(modele_type)
        self._parameters = dict(**parameters)

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    @property
    def model_type(self):
        return self._model_type

    ##############################################

    def __repr__(self):

        return str(self.__class__) + ' ' + self.name

    ##############################################

    def __str__(self):

        return ".model {} {} ({})".format(self._name, self._model_type, join_dict(self._parameters))

####################################################################################################

class Pin:

    """This class implements a pin of an element. It stores a reference to the element, the name of the
    pin and the node.
    """

    _logger = _module_logger.getChild('Pin')

    ##############################################

    def __init__(self, element, name, node):

        if keyword.iskeyword(node):
            self._logger.warning("Node {} is a Python keyword".format(node))

        self._element = element
        self._name = name
        self._node = node # Fixme: name, not a Node instance, cf. Netlist.nodes

    ##############################################

    @property
    def element(self):
        return self._element

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    @property
    def node(self):
        return self._node

    ##############################################

    def __repr__(self):

        return "Pin {} of {} on node {}".format(self._name, self._element.name, self._node)

    ##############################################

    def add_current_probe(self, circuit):

        """Add a current probe between the node and the pin.

        The ammeter is named *ElementName_PinName*.

        """

        # Fixme: require a reference to circuit
        # Fixme: add it to a list

        node = self._node
        self._node = '_'.join((self._element.name, self._name))
        circuit.V(self._node, node, self._node, '0')

####################################################################################################

class ElementParameterMetaClass(type):

    """ Metaclass to implements the element parameter machinery. """

    __classes__ = {}

    ##############################################

    def __new__(cls, class_name, base_classes, attributes):

        # Collect positional and optional parameters from class attribute dict
        positional_parameters = {}
        parameters = {}
        for attribute_name, obj in attributes.items():
            if isinstance(obj, ParameterDescriptor):
                obj.attribute_name = attribute_name
                if isinstance(obj, PositionalElementParameter):
                    d = positional_parameters
                elif isinstance(obj, (FlagParameter, KeyValueParameter)):
                    d = parameters
                # else:
                #     raise NotImplementedError
                d[attribute_name] = obj

        # Build dictionnary : attribute_name -> parameter
        attributes['_positional_parameters'] = OrderedDict(sorted(list(positional_parameters.items()),
                                                                  key=lambda t: t[1].position))

        # optional parameter order is not required for SPICE, but for unit test
        attributes['_optional_parameters'] = OrderedDict(sorted(list(parameters.items()), key=lambda t: t[0]))

        # Positional parameter array
        attributes['_parameters_from_args'] = [parameter
                                               for parameter in sorted(positional_parameters.values())
                                               if not parameter.key_parameter]

        # Implement alias for parameters
        attributes['_spice_to_parameters'] = {parameter.spice_name:parameter
                                              for parameter in attributes['_optional_parameters'].values()}
        for parameter in attributes['_spice_to_parameters'].values():
            if (parameter.spice_name in attributes
                and parameter.spice_name != parameter.attribute_name):
                _module_logger.error('Spice parameter "{}" clash with attributes'.format(parameter.spice_name))

        return super().__new__(cls, class_name, base_classes, attributes)

    ##############################################

    def __init__(cls, class_name, base_classes, attributes):

        type.__init__(cls, class_name, base_classes, attributes)

        # Collect basic element classes
        if 'prefix' in attributes:
            prefix = attributes['prefix']
            if prefix is not None:
                classes = ElementParameterMetaClass.__classes__
                if prefix in classes:
                    classes[prefix].append(cls)
                else:
                    classes[prefix] = [cls]

    ##############################################

    # Notes: These properties are only accessible from the class object, e.g. instance.__class__

    @property
    def number_of_pins(cls):
        return cls._number_of_pins

    @property
    def number_of_positional_parameters(cls):
        return len(cls._positional_parameters)

    @property
    def positional_parameters(cls):
        return cls._positional_parameters

    @property
    def optional_parameters(cls):
        return cls._optional_parameters

    @property
    def parameters_from_args(cls):
        return cls._parameters_from_args

    @property
    def spice_to_parameters(cls):
        return cls._spice_to_parameters

####################################################################################################

class Element(metaclass=ElementParameterMetaClass):

    """ This class implements a base class for an element.

    It use a metaclass machinery for the declaration of the parameters.
    """

    # These attributes are defined in subclasses or via the metaclass.
    _number_of_pins = None
    _positional_parameters = None
    _optional_parameters = None
    _parameters_from_args = None
    _spice_to_parameters = None

    # Fixme: _prefix

    #: SPICE element prefix
    prefix = None

    ##############################################

    def __init__(self, name, pins, *args, **kwargs):

        self._name = str(name)
        self._pins = list(pins) # Fixme: pins is not a ordered dict, cf. property

        # self._parameters = list(args)

        for parameter, value in zip(self._parameters_from_args, args):
            setattr(self, parameter.attribute_name, value)
        for key, value in kwargs.items():
            if key in self._positional_parameters or self._optional_parameters:
                setattr(self, key, value)

    ##############################################

    @property
    def name(self):
        return self.prefix + self._name

    @property
    def pins(self):
        return self._pins

    ##############################################

    @property
    def nodes(self):
        return [pin.node for pin in self._pins]

    ##############################################

    def __repr__(self):
        return self.__class__.__name__ + ' ' + self.name

    ##############################################

    def __setattr__(self, name, value):

        # Implement alias for parameters
        if name in self._spice_to_parameters:
            parameter = self._spice_to_parameters[name]
            object.__setattr__(self, parameter.attribute_name, value)
        else:
            object.__setattr__(self, name, value)

    ##############################################

    def __getattr__(self, name):

        # Implement alias for parameters
        if name in self._spice_to_parameters:
            parameter = self._spice_to_parameters[name]
            return object.__getattribute__(self, parameter.attribute_name)
        else:
            raise AttributeError(name)

    ##############################################

    def format_node_names(self):
        """ Return the formatted list of nodes. """
        return join_list((self.name, join_list(self.nodes)))

    ##############################################

    def parameter_iterator(self):
        """ This iterator returns the parameter in the right order. """
        for parameter_dict in self._positional_parameters, self._optional_parameters:
            for parameter in parameter_dict.values():
                if parameter.nonzero(self):
                    yield parameter

    ##############################################

    # @property
    # def parameters(self):
    #     return self._parameters

    ##############################################

    def format_spice_parameters(self):
        """ Return the formatted list of parameters. """
        return join_list([parameter.to_str(self) for parameter in self.parameter_iterator()])

    ##############################################

    def __str__(self):
        """ Return the SPICE element definition. """
        return join_list((self.format_node_names(), self.format_spice_parameters()))

####################################################################################################

class NPinElement(Element):
    pass

####################################################################################################

class AnyPinElement(Element):
    _number_of_pins = 0

####################################################################################################

class TwoPinElement(Element):

    """ This class implements a base class for a two-pin element. """

    # dipole

    _number_of_pins = 2

    ##############################################

    def __init__(self, name, node_plus, node_minus, *args, **kwargs):

        pins = (Pin(self, 'plus', node_plus), Pin(self, 'minus', node_minus))

        super().__init__(name, pins, *args, **kwargs)

    ##############################################

    @property
    def plus(self):
        return self.pins[0]

    ##############################################

    @property
    def minus(self):
        return self.pins[1]

####################################################################################################

class ThreePinElement(Element):
    _number_of_pins = 3

####################################################################################################

class FourPinElement(Element):
    _number_of_pins = 4

####################################################################################################

class TwoPortElement(Element):

    """ This class implements a base class for a two-port element.

    .. warning:: As opposite to Spice, the input nodes are specified before the output nodes.
    """

    _number_of_pins = 4

    ##############################################

    # Fixme: Why the order the inverted ?

    def __init__(self, name,
                 input_node_plus, input_node_minus,
                 output_node_plus, output_node_minus,
                 *args, **kwargs):

        pins = (Pin(self, 'output_plus', output_node_plus),
                Pin(self, 'output_minus', output_node_minus),
                Pin(self, 'input_plus', input_node_plus),
                Pin(self, 'input_minus', input_node_minus))

        super().__init__(name, pins, *args, **kwargs)

    ##############################################

    @property
    def output_plus(self):
        return self.pins[0]

    ##############################################

    @property
    def output_minus(self):
        return self.pins[1]

    ##############################################

    @property
    def input_plus(self):
        return self.pins[2]

    ##############################################

    @property
    def input_minus(self):
        return self.pins[3]

####################################################################################################

class Node:

    """This class implements a node in the circuit. It stores a reference to the elements connected to
    the node."""

    # Fixme: but not directly to the pins!

    ##############################################

    def __init__(self, name):

        self._name = str(name)
        self._elements = set()

    ##############################################

    def __repr__(self):
        return 'Node {}'.format(self._name)

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def elements(self):
        return self._elements

    ##############################################

    def add_element(self, element):
        self._elements.add(element)

####################################################################################################

class Netlist:

    """ This class implements a base class for a netlist.

    .. note:: This class is completed at running time with elements.
    """

    ##############################################

    def __init__(self):

        self._ground = None
        self._elements = OrderedDict() # to keep the declaration order
        self._models = {}
        self._dirty = True
        # self._nodes = set()
        self._nodes = {}

        # self._graph = networkx.Graph()

    ##############################################

    def element_iterator(self):

        return iter(self._elements.values())

    ##############################################

    def element_names(self):

        return [element.name for element in self.element_iterator()]

    ##############################################

    def model_iterator(self):

        return iter(self._models.values())

    ##############################################

    def __str__(self):

        """ Return the formatted list of element and model definitions. """

        netlist = join_lines(self.element_iterator()) + os.linesep
        if self._models:
            netlist += join_lines(self.model_iterator()) + os.linesep
        return netlist

    ##############################################

    def _add_element(self, element):

        """Add an element."""

        if element.name not in self._elements:
            self._elements[element.name] = element
            self._dirty = True
        else:
            raise NameError("Element name {} is already defined".format(element.name))

    ##############################################

    def model(self, name, modele_type, **parameters):

        """Add a model."""

        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model
        else:
            raise NameError("Model name {} is already defined".format(name))

    ##############################################

    @property
    def nodes(self):

        """Return the nodes."""

        if self._dirty:
            # nodes = set()
            # for element in self.element_iterator():
            #     nodes |= set(element.nodes)
            # if self._ground is not None:
            #     nodes -= set((self._ground,))
            # self._nodes = nodes
            self._nodes.clear()
            for element in self.element_iterator():
                for node_name in element.nodes:
                    if node_name not in self._nodes:
                        node = Node(node_name)
                        self._nodes[node_name] = node
                    else:
                        node = self._nodes[node_name]
                    node.add_element(element)
        return list(self._nodes.values())

    ##############################################

    def node_names(self):

        return [node.name for node in self.nodes]

    ##############################################

    def __getitem__(self, attribute_name):

        if attribute_name in self._elements:
            return self._elements[attribute_name]
        elif attribute_name in self._models:
            return self._models[attribute_name]
        elif attribute_name in self._nodes:
            return attribute_name
        else:
            raise IndexError(attribute_name)

    ##############################################

    def __getattr__(self, attribute_name):

        try:
            return self.__getitem__(attribute_name)
        except IndexError:
            raise AttributeError(attribute_name)

####################################################################################################

class SubCircuit(Netlist):

    """This class implements a sub-cicuit netlist."""

    ##############################################

    def __init__(self, name, *nodes, **kwargs):

        super().__init__()

        self.name = str(name)
        self._external_nodes = list(nodes)
        # Fixme: ok ?
        self._ground = kwargs.get('ground', 0)
        if 'ground' in kwargs:
            del kwargs['ground']
        self._parameters = kwargs

    ##############################################

    @property
    def gnd(self):
        """ Local ground """
        return self._ground

    ##############################################

    @property
    def parameters(self):
        """Parameters"""
        return self._parameters

    ##############################################

    def check_nodes(self):

        """Check for dangling nodes in the subcircuit."""

        nodes = set(self._external_nodes)
        connected_nodes = set()
        for element in self.element_iterator():
            connected_nodes.add(nodes & element.nodes)
        not_connected_nodes = nodes - connected_nodes
        if not_connected_nodes:
            raise NameError("SubCircuit Nodes {} are not connected".format(not_connected_nodes))

    ##############################################

    def __str__(self):

        """Return the formatted subcircuit definition."""

        nodes = join_list(self._external_nodes)
        parameters = join_list(['{}={}'.format(key, value)
                                for key, value in self._parameters.items()])
        netlist = '.subckt ' + join_list((self.name, nodes, parameters)) + os.linesep
        netlist += super().__str__()
        netlist += '.ends ' + self.name + os.linesep
        return netlist

####################################################################################################

class SubCircuitFactory(SubCircuit):

    # Fixme : versus SubCircuit

    __name__ = None
    __nodes__ = None

    ##############################################

    def __init__(self, **kwargs):

        super().__init__(self.__name__, *self.__nodes__, **kwargs)

####################################################################################################

class Circuit(Netlist):

    """This class implements a cicuit netlist.

    To get the corresponding Spice netlist use::

       circuit = Circuit()
       ...
       str(circuit)

    """

    # .lib
    # .func
    # .csparam

    ##############################################

    def __init__(self, title,
                 ground=0,
                 global_nodes=(),
             ):

        super().__init__()

        self.title = str(title)
        self._ground = ground
        self._global_nodes = set(global_nodes) # .global
        self._includes = [] # .include
        self._parameters = {} # .param
        self._subcircuits = {}

        # Fixme: not implemented
        #  .func
        #  .csparam
        #  .if

    ##############################################

    @property
    def gnd(self):
        return self._ground

    ##############################################

    def include(self, path):

        """Include a file."""

        if path not in self._includes:
            self._includes.append(path)
        else:
            self._logger.warn("Duplicated include")

    ##############################################

    def parameter(self, name, expression):

        """Set a parameter."""

        self._parameters[str(name)] = str(expression)

    ##############################################

    def subcircuit(self, subcircuit):

        """Add a sub-circuit."""

        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def subcircuit_iterator(self):

        """Return a sub-circuit iterator."""

        return iter(self._subcircuits.values())

    ##############################################

    def __str__(self):

        """Return the formatted desk."""

        netlist = '.title {}'.format(self.title) + os.linesep
        if self._includes:
            # ngspice don't like // in path, thus ensure we write real paths
            real_paths = [os.path.realpath(str(path)) for path in self._includes]
            netlist += join_lines(real_paths, prefix='.include ') + os.linesep
        if self._global_nodes:
            netlist += '.global ' + join_list(self._global_nodes) + os.linesep
        if self._parameters:
            netlist += join_lines(self._parameters, prefix='.param ') + os.linesep
        if self._subcircuits:
            netlist += join_lines(self.subcircuit_iterator())
        netlist += super().__str__()
        return netlist

    ##############################################

    def str_end(self):

        return str(self) + '.end' + os.linesep

    ##############################################

    def simulator(self, *args, **kwargs):

        """Return a :obj:`PySpice.Spice.Simulation.SubprocessCircuitSimulator` or
        :obj:`PySpice.Spice.Simulation.NgSpiceSharedCircuitSimulator` instance depending of the
        value of the *simulator* parameter: ``subprocess`` or ``shared``, respectively. If this
        parameter is not specified then a subprocess simulator is returned.

        """

        simulator = kwargs.get('simulator', 'subprocess')
        if 'simulator' in kwargs:
            simulator = kwargs['simulator']
            del kwargs['simulator']
        else:
            simulator = CircuitSimulator.DEFAULT_SIMULATOR_MODE
        if simulator == 'subprocess':
            return SubprocessCircuitSimulator(self, *args, **kwargs)
        elif simulator == 'shared':
            return NgSpiceSharedCircuitSimulator(self, *args, **kwargs)
        else:
            return ValueError('Unknown simulator type')
