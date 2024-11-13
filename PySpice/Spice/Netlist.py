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

from ..Tools.StringTools import join_lines, join_list, join_dict, str_spice
from .ElementParameter import (
    ParameterDescriptor,
    PositionalElementParameter,
    FlagParameter, KeyValueParameter,
)
from .Simulation import CircuitSimulator
from .Expressions import Expression

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class DeviceModel:
    """This class implements a device model.

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

    def __init__(self, name, model_type, **parameters):

        self._name = str(name).lower()
        self._model_type = str(model_type)

        self._parameters = {}
        for key, value in parameters.items():
            # For parameters like is that are also python keywords
            if key.endswith('_'):
                key = key[:-1]
            self._parameters[key] = value

    ##############################################

    def clone(self):
        # Fixme: clone parameters ???
        return self.__class__(self._name, self._model_type, self._parameters)

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def model_type(self):
        return self._model_type

    @property
    def parameters(self):
        return self._parameters.keys()

    @property
    def include(self):
        """Include file"""
        return self._include

    @property
    def is_included(self):
        """is_included"""
        return self._include is None

    ##############################################

    def __getitem__(self, name):
        if name in self._parameters:
            return self._parameters[name]
        elif name.endswith('_'):
            return self._parameters[name[:-1]]
        else:
            raise IndexError(name)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(name)

    ##############################################

    def __repr__(self):
        return str(self.__class__) + ' ' + self.name

    ##############################################

    def __str__(self):
        return ".model {0._name} {0._model_type} ({1})".format(self, join_dict(self._parameters))

####################################################################################################

class PinDefinition:
    """This class defines a pin of an element."""

    ##############################################

    def __init__(self, position, name=None, alias=None, optional=False):
        self._position = position
        self._name = name
        self._alias = alias
        self._optional = optional

    ##############################################

    def clone(self):
        # Fixme: self.__class__ ???
        return PinDefinition(self._position, self._name, self._alias, self._optional)

    ##############################################

    @property
    def position(self):
        return self._position

    @property
    def name(self):
        return self._name

    @property
    def alias(self):
        return self._alias

    @property
    def optional(self):
        return self._optional

####################################################################################################

class OptionalPin:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

####################################################################################################

class Pin(PinDefinition):
    """This class implements a pin of an element. It stores a reference to the element, the name of the
    pin and the node.

    """

    _logger = _module_logger.getChild('Pin')

    ##############################################

    def __init__(self, element, pin_definition, node):
        super().__init__(pin_definition.position, pin_definition.name, pin_definition.alias)

        self._element = element
        self._node = node

        node.connect(self)

    ##############################################

    @property
    def element(self):
        return self._element

    @property
    def node(self):
        return self._node

    ##############################################

    def __repr__(self):
        return "Pin {} of {} on node {}".format(self._name, self._element.name, self._node)

    ##############################################

    def disconnect(self):
        self._node.disconnect(self)
        self._node = None

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
    # Metaclass to implements the element node and parameter machinery.

    """Metaclass to customise the element classes when they are created and to register SPICE prefix.

    Element classes are of type :class:`ElementParameterMetaClass` instead of :class:`type`

    .. code-block:: none

        class Resistor(metaclass=ElementParameterMetaClass):

        <=>

        Resistor = ElementParameterMetaClass('Foo', ...)

    """

    #: Dictionary for SPICE prefix -> [cls,]
    _classes = {}

    _logger = _module_logger.getChild('ElementParameterMetaClass')

    ##############################################

    def __new__(meta_cls, class_name, base_classes, namespace):

        # __new__ is called for the creation of a class depending of this metaclass, i.e. at module loading
        # It customises the namespace of the new class

        # Collect positional and optional parameters from class attribute dict
        positional_parameters = {}
        parameters = {}
        for attribute_name, obj in namespace.items():
            if isinstance(obj, ParameterDescriptor):
                obj.attribute_name = attribute_name
                if isinstance(obj, PositionalElementParameter):
                    d = positional_parameters
                elif isinstance(obj, (FlagParameter, KeyValueParameter)):
                    d = parameters
                # else:
                #     raise NotImplementedError
                d[attribute_name] = obj

        # Dictionary for positional parameters : attribute_name -> parameter
        namespace['_positional_parameters'] = OrderedDict(
            sorted(list(positional_parameters.items()), key=lambda t: t[1]))

        # Dictionary for optional parameters
        #   order is not required for SPICE, but for unit test
        namespace['_optional_parameters'] = OrderedDict(
            sorted(list(parameters.items()), key=lambda t: t[0]))

        # Positional parameter array
        namespace['_parameters_from_args'] = [
            parameter
            for parameter in sorted(positional_parameters.values())
            if not parameter.key_parameter]

        # Implement alias for parameters: spice name -> parameter
        namespace['_spice_to_parameters'] = {
            parameter.spice_name:parameter
            for parameter in namespace['_optional_parameters'].values()}
        for parameter in namespace['_spice_to_parameters'].values():
            if (parameter.spice_name in namespace
                and parameter.spice_name != parameter.attribute_name):
                _module_logger.error("Spice parameter '{}' clash with namespace, attribute name: '{}'".format(parameter.spice_name, parameter.attribute_name))

        # Initialise pins

        def make_pin_getter(position):
            def getter(self):
                return self._pins[position]
            return getter

        def make_optional_pin_getter(position):
            def getter(self):
                return self._pins[position] if position < len(self._pins) else None
            return getter

        if 'PINS' in namespace and namespace['PINS'] is not None:
            number_of_optional_pins = 0
            pins = []
            for position, pin_definition in enumerate(namespace['PINS']):
                # ensure pin_definition is a tuple
                if isinstance(pin_definition, OptionalPin):
                    optional = True
                    number_of_optional_pins += 1
                    pin_definition = (pin_definition.name,)
                    pin_getter = make_optional_pin_getter(position)
                else:
                    optional = False
                    pin_getter = make_pin_getter(position)
                if not isinstance(pin_definition, tuple):
                    pin_definition = (pin_definition,)
                for name in pin_definition:
                    # Check for name clash
                    if name in namespace:
                        raise NameError("Pin {} of element {} clashes with another attribute".format(name, class_name))
                    # Add a pin getter in element class
                    namespace[name] = property(pin_getter)
                # Add pin
                pin = PinDefinition(position, *pin_definition, optional=optional)
                pins.append(pin)
            namespace['PINS'] = pins
            namespace['_number_of_optional_pins_'] = number_of_optional_pins
        else:
            _module_logger.debug("{} don't define a PINS attribute".format(class_name))

        return type.__new__(meta_cls, class_name, base_classes, namespace)

    ##############################################

    def __init__(meta_cls, class_name, base_classes, namespace):

        # __init__ is called after the class is created (__new__)

        type.__init__(meta_cls, class_name, base_classes, namespace)

        # Collect basic element classes
        if 'PREFIX' in namespace:
            prefix = namespace['PREFIX']
            if prefix is not None:
                classes = ElementParameterMetaClass._classes
                if prefix in classes:
                    classes[prefix].append(meta_cls)
                else:
                    classes[prefix] = [meta_cls]

    ##############################################

    # Note: These properties are only available from the class object
    #       e.g. Resistor.number_of_pins or Resistor.__class__.number_of_pins

    @property
    def number_of_pins(cls):
        #! Fixme: many pins ???
        number_of_pins = len(cls.PINS)
        if cls._number_of_optional_pins_:
            return slice(number_of_pins - cls._number_of_optional_pins_, number_of_pins +1)
        else:
            return number_of_pins

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
    """This class implements a base class for an element.

    It use a metaclass machinery for the declaration of the parameters.

    """

    # These class attributes are defined in subclasses or via the metaclass.
    PINS = None
    _positional_parameters = None
    _optional_parameters = None
    _parameters_from_args = None
    _spice_to_parameters = None

    #: SPICE element prefix
    PREFIX = None

    ##############################################

    def __init__(self, netlist, name, *args, **kwargs):

        self._netlist = netlist
        self._name = str(name).lower()
        self.raw_spice = ''
        self.enabled = True
        parent = netlist
        self._parameters = kwargs
        # self._pins = kwargs.pop('pins',())

        # Process remaining args
        if len(self._parameters_from_args) + self._number_of_optional_pins_ + len(self._positional_parameters) < len(args):
            raise NameError("Number of args mismatch for device: {}".format(self.name))
        # TODO: Modify the selection of arguments to take into account the RLC model cases.
        if len(args) > 0:
            optional_pins = 0
            if len(self._positional_parameters) < len(args):
                optional_pins = len(args) - len(self._positional_parameters)
            for parameter in self._positional_parameters.values():
                if parameter.attribute_name in kwargs:
                    optional_pins += 1
                    continue
            if optional_pins <= self._number_of_optional_pins_ and len(args) >= optional_pins:
                self._pins += [Pin(self, pin_definition, netlist.get_node(node, True))
                      for pin_definition, node in zip(self.PINS[len(self._pins):], args[:optional_pins])]
                args = args[optional_pins:]
            else:
                raise IndexError("Incongruent number of optional pins on device: {}{}".format(self.PREFIX, self._name))
            if len(args) > 0:
                read = [False] * len(args)
                for parameter in self._positional_parameters.values():
                    if parameter.position < len(read) and not read[parameter.position]:
                        setattr(self, parameter.attribute_name, args[parameter.position])
                        read[parameter.position] = True
        # Process kwargs
        for key, value in kwargs.items():
            if key == 'raw_spice':
                self.raw_spice = value
            else:
                if (key in self._positional_parameters or
                        key in self._optional_parameters or
                        key in self._spice_to_parameters):
                    setattr(self, key, value)
                else:
                    for parameter in self._optional_parameters:
                        if key.lower() == self._optional_parameters[parameter].spice_name.lower():
                            setattr(self, parameter, value)
                            break
                    else:
                        raise ValueError('Unknown argument for {}: {}={}'.format(self.name, key, value))

        netlist._add_element(self)

    ##############################################

    def has_parameter(self, name):
        return hasattr(self, '_' + name)

    ##############################################

    def copy_to(self, element):

        for parameter_dict in self._positional_parameters, self._optional_parameters:
            for parameter in parameter_dict.values():
                if hasattr(self, parameter.attribute_name):
                    value = getattr(self, parameter.attribute_name)
                    setattr(element, parameter.attribute_name, value)

        if hasattr(self, 'raw_spice'):
            element.raw_spice = self.raw_spice

    ##############################################

    @property
    def netlist(self):
        return self._netlist

    @property
    def name(self):
        return self.PREFIX + self._name

    @property
    def pins(self):
        return self._pins

    ##############################################

    def detach(self):
        for pin in self._pins:
            pin.disconnect()
        self._netlist._remove_element(self)
        self._netlist = None
        return self

    ##############################################

    @property
    def nodes(self):
        return [pin.node for pin in self._pins]

    @property
    def node_names(self):
        return [str(x) for x in self.nodes]

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
        positional_parameters = OrderedDict()
        # Fixme: .parameters ???
        if len(self._positional_parameters) > 0:
            read = [False] * len(self._positional_parameters)
            for parameter in self._positional_parameters.values():
                if parameter.position < len(read) and read[parameter.position] is False:
                    if parameter.nonzero(self):
                        read[parameter.position] = parameter
        for parameter in read:
            if not (parameter is False):
                positional_parameters[parameter.attribute_name] = parameter

        for parameter_dict in positional_parameters, self._optional_parameters:
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
        return join_list((self.format_node_names(), self.format_spice_parameters(), self.raw_spice))

####################################################################################################

class AnyPinElement(Element):

    PINS = ()

    ##############################################

    def copy_to(self, netlist):
        element = self.__class__(netlist, self._name)
        super().copy_to(element)
        return element

####################################################################################################

class FixedPinElement(Element):

    ##############################################

    def __init__(self, netlist, name, *args, **kwargs):

        # Get nodes
        # Usage: if pins are passed using keywords then args must be empty
        #        optional pins are passed as keyword
        pin_definition_nodes = []
        number_of_args = len(args)
        if number_of_args:
            expected_number_of_pins = self.__class__.number_of_pins   # Fixme:
            if isinstance(expected_number_of_pins, slice):
                expected_number_of_pins = expected_number_of_pins.start
            if number_of_args < expected_number_of_pins:
                raise NameError("Incomplete node list for element {}".format(self.name))
            else:
                nodes = args[:expected_number_of_pins]
                args = args[expected_number_of_pins:]
                pin_definition_nodes = zip(self.PINS, nodes)
        else:
            for pin_definition in self.PINS:
                if pin_definition.name in kwargs:
                    node = kwargs[pin_definition.name]
                    del kwargs[pin_definition.name]
                elif pin_definition.alias is not None and pin_definition.alias in kwargs:
                    node = kwargs[pin_definition.alias]
                    del kwargs[pin_definition.alias]
                elif pin_definition.optional:
                    continue
                else:
                    raise NameError("Node '{}' is missing for element {}".format(pin_definition.name, self.name))
                pin_definition_nodes.append((pin_definition, node))

        self._pins = [Pin(self, pin_definition, netlist.get_node(node, True))
                      for pin_definition, node in pin_definition_nodes]

        super().__init__(netlist, name, *args, **kwargs)

    ##############################################

    def copy_to(self, netlist):
        element = self.__class__(netlist, self._name, *self.nodes)
        super().copy_to(element)
        return element

####################################################################################################

class NPinElement(Element):

    PINS = '*'

    ##############################################

    def __init__(self, netlist, name, *args, **kwargs):
        nodes = []
        positional = len(self._positional_parameters)
        for key, parameter in self._positional_parameters.items():
            if parameter.key_parameter:
                if key in kwargs:
                    positional -= 1
        if positional > 0:
            if positional < len(args):
                nodes = args[:-positional]
                args = args[-positional:]
        else:
            nodes = args
            args = []

        if len(nodes) > 0:
            self._pins = [Pin(self, self.PINS[0], netlist.get_node(node, True))
                          for node in nodes]
        super().__init__(netlist, name, *args, **kwargs)

    ##############################################

    def copy_to(self, netlist):
        nodes = [str(x) for x in self.nodes]
        element = self.__class__(netlist, self._name, nodes)
        super().copy_to(element)
        return element

####################################################################################################

class Node:
    """This class implements a node in the circuit. It stores a reference to the pins connected to
    the node.

    """

    _logger = _module_logger.getChild('Node')

    ##############################################

    def __init__(self, netlist, name):

        if keyword.iskeyword(name):
            self._logger.warning("Node name '{}' is a Python keyword".format(name))

        self._netlist = netlist
        self._name = str(name).lower()

        self._pins = set()

    ##############################################

    def __repr__(self):
        return 'Node {}'.format(self._name)

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
            raise ValueError("Pin {} is already connected to node {}".format(pin, self))

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

        self._subcircuits = OrderedDict()  # to keep the declaration order
        self._elements = OrderedDict()  # to keep the declaration order
        self._models = OrderedDict()
        self._includes = []  # .include
        self._used_models = {}
        self._used_subcircuits = {}
        self._parameters = OrderedDict()

        self.raw_spice = ''

        self._spice_sim = ''

        self._parent = None

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

    def _get_spice_sim(self):
        return self._spice_sim

    def _set_spice_sim(self, spice_sim):
        for subcircuit in self._subcircuits:
            self._subcircuits[subcircuit].spice_sim = spice_sim
        self._spice_sim = spice_sim

    spice_sim = property(_get_spice_sim, _set_spice_sim)

    ##############################################

    def __getitem__(self, attribute_name):
        attr = str(attribute_name).lower()
        if attr in self._elements:
            return self.element(attr)
        elif attr in self._models:
            return self.model(attr)
        # Fixme: subcircuits
        elif attr in self._nodes:
            return self.node(attr)
        else:
            raise IndexError(attribute_name)   # KeyError

    def __getattr__(self, attribute_name):
        try:
            return self.__getitem__(attribute_name)
        except IndexError:
            raise AttributeError(attribute_name)

    ##############################################

    def _find_subcircuit(self, name):
        name_low = name.lower()
        if name_low not in self._subcircuits:
            if hasattr(self, 'parent') and self.parent is not None:
                return self.parent._find_subcircuit(name_low)
            else:
                return None
        else:
            return self._subcircuits[name_low]

    def _add_node(self, node_name):
        node_name = str(node_name).lower()
        if node_name not in self._nodes:
            node = Node(self, node_name)
            self._nodes[node_name] = node
            return node
        else:
            raise ValueError("Node {} is already defined".format(node_name))

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
            str_node = str(node).lower()
            if str_node in self._nodes:
                return self._nodes[str_node]
            elif create:
                return self._add_node(str_node)
            else:
                raise KeyError("Node {} doesn't exists".format(node))

    ##############################################

    def has_ground_node(self):
        return bool(self._ground_node)

    ##############################################

    # def _update_used_models_subcircuits(self, subcircuit):
    #     for mod in subcircuit._used_models:
    #         if mod not in subcircuit._models:
    #             self._used_models.add(mod)
    #     for sub in subcircuit._used_subcircuits:
    #         if sub in subcircuit._subcircuits:
    #             if sub in self._subcircuits:
    #                 raise ValueError("Repeated subcircuit label: {}".format(sub))
    #             self._update_used_models_subcircuits(subcircuit._subcircuits[sub])
    #             if sub not in self._subcircuits:
    #                 self._subcircuits[sub] = subcircuit._subcircuits[sub]
    #     self._used_subcircuits.add(subcircuit.name)

    def _revise_required_models_subcircuits(self, subcircuits):
        # Check the subcircuits required in the present object
        # and confirm there are no duplicated subcircuit object with the same name
        for subcircuit_name, subid in self._used_subcircuits.items():
            if subcircuit_name in self._subcircuits:
                subcktid = id(self._subcircuits[subcircuit_name])
                if subid is None:
                    self._used_subcircuits[subcircuit_name] = subcktid
                elif subid != subcktid:
                    raise ValueError("Differing subcircuits: {}".format(subcircuit_name))

        # Check the subcircuits required in the present object with respect to parent
        # and confirm there are no duplicated subcircuit object with the same name
        for subcircuit_name in self._used_subcircuits:
            if subcircuit_name in subcircuits:
                subcktid = id(subcircuits[subcircuit_name])
                if self._used_subcircuits[subcircuit_name] is not None and self._used_subcircuits[subcircuit_name] != subcktid:
                    raise ValueError("Differing subcircuits: {}".format(subcircuit_name))
                else:
                    self._used_subcircuits[subcircuit_name] = subcktid

        # Check the subcircuits in the present object with respect to parent
        # and confirm there are no duplicated subcircuit object with the same name
        for subcircuit_name in self._subcircuits:
            if subcircuit_name in subcircuits:
                if id(self._subcircuits[subcircuit_name]) != id(subcircuits[subcircuit_name]):
                    raise ValueError("Differing subcircuits: {}".format(subcircuit_name))
            else:
                _, subcircuits[subcircuit_name] = self._subcircuits.popitem(subcircuit_name)

        # Check the subcircuits in the child objects
        for subcircuit_name in self._subcircuits:
            required_subs, required_mods = self._subcircuits[subcircuit_name]._revise_required_models_subcircuits(subcircuits)
            for subckt, subid in required_subs.items():
                if subckt in self._used_subcircuits:
                    if self._used_subcircuits[subckt] is None:
                        self._used_subcircuits[subckt] = subid
                    elif subid is not None and subid != self._used_subcircuits[subckt]:
                        raise ValueError("Differing subcircuits: {}".format(subckt))
                else:
                    self._used_subcircuits[subckt] = subid
            for mod_name, modid in required_mods.items():
                if mod_name in self._used_models:
                    if self._used_models[mod_name] is None:
                        self._used_models[mod_name] = modid
                    elif modid is not None and modid != self._used_models[mod_name]:
                        raise ValueError("Differing subcircuits: {}".format(mod_name))
                else:
                    self._used_models[mod_name] = modid
        return self._used_subcircuits, self._used_models

    def _add_element(self, element):
        from .BasicElement import SubCircuitElement
        """Add an element."""
        element_name = str(element.name).lower()
        if element_name not in self._elements:
            self._elements[element_name] = element
            if hasattr(element, 'model'):
                model = str(element.model).lower()
                if model is not None:
                    self._used_models[model] = None

            if isinstance(element, SubCircuitElement):
                subcircuit_name = str(element.subcircuit_name).lower()
                if subcircuit_name is not None:
                    self._used_subcircuits[subcircuit_name] = None
                else:
                    ValueError("Subcircuit not provided for element: {}".format(element_name))
        else:
            raise NameError("Element name {} is already defined".format(element_name))

    ##############################################

    def _remove_element(self, element):
        try:
            del self._elements[str(element.name).lower()]
        except KeyError:
            raise NameError("Cannot remove undefined element {}".format(element))

    ##############################################

    def parameter(self, name, expression):
        """Set a parameter."""
        self._parameters[str(name).lower()] = expression

    ##############################################

    def model(self, name, model_type, **parameters):

        """Add a model."""

        model = DeviceModel(str(name).lower(), model_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model
        else:
            raise NameError("Model name {} is already defined".format(name))

        return model

    ##############################################

    def subcircuit(self, subcircuit):
        """Add a sub-circuit."""
        # Fixme: subcircuit is a class
        assert isinstance(subcircuit, SubCircuit)
        self._subcircuits[str(subcircuit.name).lower()] = subcircuit
        subcircuit._parent = self
        self._revise_required_models_subcircuits(self._subcircuits)

    ##############################################

    def __str__(self):
        """ Return the formatted list of element and model definitions. """
        # Fixme: order ???
        netlist = self._str_raw_spice()
        if self._parameters:
            parameters = self._str_parameters()
            netlist += parameters
            netlist += os.linesep
        if self._models:
            models = self._str_models()
            netlist += models
            netlist += os.linesep
        if self._subcircuits:
            subcircuits = self._str_subcircuits()
            netlist += subcircuits  # before elements
            netlist += os.linesep
        netlist += self._str_elements() + os.linesep
        return netlist

    ##############################################

    def _str_parameters(self):
        parameters = [".param {}={}".format(key, ('{%s}' % str_spice(value)) if isinstance(value, Expression) else str_spice(value))
                      for key, value in self._parameters.items()]
        return join_lines(parameters)

    ##############################################

    def _str_elements(self):
        elements = [element for element in self.elements if element.enabled]
        return join_lines(elements)

    ##############################################

    def _str_models(self):
        if self._used_models:
            models = [self._models[model]
                      for model in self._models
                      if model in self._used_models]
            return join_lines(models)
        else:
            return ''

    ##############################################

    def _str_subcircuits(self):
        if self._used_subcircuits:
            subcircuits = [self._subcircuits[subcircuit]
                           for subcircuit in self._subcircuits
                           if subcircuit in self._used_subcircuits]
            return join_lines(subcircuits)
        else:
            return ''

    ##############################################

    def _str_raw_spice(self):
        netlist = self.raw_spice
        if netlist and not netlist.endswith(os.linesep):
            netlist += os.linesep
        return netlist

    def include(self, library):
        from .Library import SpiceLibrary

        """Include a file."""
        if isinstance(library, SpiceLibrary):
            spice_library = library
        else:
            spice_library = SpiceLibrary(library)
        models = spice_library.models
        for model_name in models:
            self.model(model_name,
                       spice_library[model_name]._model_type,
                       **spice_library[model_name]._parameters)
        subcircuits = spice_library.subcircuits
        for subcircuit_name in subcircuits:
            if self._search_subcircuit(subcircuit_name) is not None:
                continue
            subcircuit = spice_library[subcircuit_name]
            assert subcircuit is not None
            subcircuit_def = subcircuit.build(parent=self)
            self.subcircuit(subcircuit_def)

    def _search_subcircuit(self, name):
        if name in self._subcircuits:
            return self._subcircuits[name]
        if self._parent is not None:
            return self._parent._search_subcircuit(name)
        return None
####################################################################################################

class SubCircuit(Netlist):

    """This class implements a sub-cicuit netlist."""

    ##############################################

    def __init__(self, name, *nodes, **kwargs):
        self._included = None

        nodes_set = set(nodes)
        if len(nodes_set) != len(nodes):
            raise ValueError("Duplicated nodes in {}".format(nodes))

        super().__init__()

        self._name = str(name).lower()
        self._external_nodes = tuple([Node(self, str(node)) for node in nodes])
        self.PINS = [PinDefinition(position, pin_definition)
                     for position, pin_definition in enumerate(nodes)]
        # Fixme: ok ?
        ground = 'ground'
        self._ground = kwargs.get(ground, 0)
        if ground in kwargs:
            kwargs.pop(ground)

        self._params = kwargs

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

    def parameter(self, name, expression):

        """Set a parameter."""

        self._parameters[str(name)] = expression

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

    @property
    def included(self):
        """Include file"""
        return self._included

    @property
    def is_included(self):
        """is_included"""
        return self._included is None

    ##############################################

    def check_nodes(self):

        """Check for dangling nodes in the subcircuit."""

        nodes = self._external_nodes
        connected_nodes = dict()
        connected_nodes.update([(node.name, False) for node in nodes])
        for element in self.elements:
            for node in element.nodes:
                node_name = node.name
                if node_name in connected_nodes:
                    connected_nodes[node_name] = True
                else:
                    connected_nodes[node_name] = False
        not_connected_nodes = [node for node in connected_nodes
                               if not connected_nodes[node]]
        if not_connected_nodes:
            raise NameError("SubCircuit Nodes {} are not connected".format(not_connected_nodes))

    ##############################################

    def __str__(self):
        netlist = self._str_raw_spice()

        """Return the formatted subcircuit definition."""
        nodes = join_list(self._external_nodes)

        netlist += '.subckt ' + join_list((self._name, nodes))
        if self._params:
            parameters = {key: ('{%s}' % str_spice(value)) if isinstance(value, Expression) else str_spice(value)
                          for key, value in self._params.items()}
            netlist += ' params: ' + join_dict(parameters)
        netlist += os.linesep
        if self._parameters:
            parameters = self._str_parameters()
            netlist += parameters
            netlist += os.linesep
        if self._models:
            models = self._str_models()
            netlist += models
            netlist += os.linesep
        if self._subcircuits:
            subcircuits = self._str_subcircuits()
            netlist += subcircuits  # before elements
            netlist += os.linesep
        netlist += self._str_elements() + os.linesep
        netlist += '.ends ' + self._name + os.linesep
        return netlist

####################################################################################################

class Library(Netlist):
    """This class implements a library netlist."""

    ##############################################

    def __init__(self, entry):
        self._entry = entry

    ##############################################

    def clone(self, entry=None):
        if entry is None:
            entry = self._entry

        library = self.__class__(entry)
        self.copy_to(library)

    ##############################################

    @property
    def entry(self):
        return self._entry

    ##############################################

    def __str__(self):
        """Return the formatted library definition."""

        netlist = '.lib ' + self._entry + os.linesep
        netlist += super().__str__()
        netlist += '.endl ' + self._entry + os.linesep
        return netlist


####################################################################################################

class SubCircuitFactory(SubCircuit):

    NAME = None
    NODES = None
    PINS = None

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

        if title is None:
            title = ""
        self.title = str(title)
        self._ground = ground
        self._global_nodes = set(global_nodes)  # .global
        self._data = {}  # .data

        # Fixme: not implemented
        #  .csparam
        #  .func
        #  .if
        #  .lib

    ##############################################

    @property
    def name(self):
        return self.title

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

    ##############################################

    def data(self, table, **kwargs):
        self._data.update[table] = kwargs

    ##############################################

    def str(self, spice_sim=None):
        if spice_sim is not None:
            self.spice_sim = spice_sim
        """Return the formatted desk."""
        # if not self.has_ground_node():
        #     raise NameError("Circuit don't have ground node")
        netlist = self._str_title()
        netlist += os.linesep
        # netlist += self._str_includes(simulator)
        for sub_circuit in self._subcircuits:
            self._subcircuits[sub_circuit].spice_sim = self.spice_sim

        if self._global_nodes:
            netlist += self._str_globals() + os.linesep
        netlist += super().__str__()
        return netlist

    ##############################################

    def _str_title(self):
        if self.title:
            lines = self.title.splitlines()
            title = '.title {}'.format(lines[0]) + os.linesep
            if len(lines) > 1:
                for line in lines[1:]:
                    title += '* {}'.format(line) + os.linesep
            return title
        else:
            return '.title' + os.linesep

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

    def _str_globals(self):

        if self._global_nodes:
            return join_lines(['.global {}'.format(str_spice(node))
                               for node in self._global_nodes])
        else:
            return ''

    ##############################################

    def __str__(self):
        return self.str(spice_sim=None)

    ##############################################

    def str_end(self):
        return str(self) + '.end' + os.linesep

    ##############################################

    def simulator(self, *args, **kwargs):
        return CircuitSimulator.factory(self, *args, **kwargs)


####################################################################################################

class Comment:

    def __init__(self, txt=''):
        self._txt = txt

    def __str__(self):
        return self._txt

    def __repr__(self):
        return "Comment({})".format(repr(self._txt))
