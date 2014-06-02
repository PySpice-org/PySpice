####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

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

# import networkx

####################################################################################################

from ..Tools.StringTools import join_lines, join_list, join_dict
from ..Unit.Units import Unit
from .Simulation import CircuitSimulator

####################################################################################################

class DeviceModel(object):

    """ This class implements a device model. """

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

class Pin(object):

    """ This class implements a pin of an element. """

    ##############################################

    def __init__(self, element, name, node):

        self.element = element
        self.name = name
        self.node = node

    ##############################################

    def __repr__(self):

        return "Pin {} of {} on node {}".format(self.name, self.element.name, self.node)

    ##############################################

    def add_current_probe(self, circuit):

        # Fixme: require a reference to circuit

        node = self.node
        self.node = '_'.join((self.element.name, self.name))
        circuit.V(self.node, node, self.node, '0')

####################################################################################################

class ElementParameter(object):

    ##############################################

    def __init__(self, spice_name, default=None):

        self.spice_name = spice_name
        self.value = default

        self.attribute_name = None

    ##############################################

    def __get__(self, obj, object_type):
        return self.value

    ##############################################

    def validate(self, value):
        return value
        
    ##############################################

    def __set__(self, obj, value):
        self.value = self.validate(value)

    ##############################################

    def __nonzero__(self):
        return self.value is not None

    ##############################################

    def __str__(self):
        raise NotImplementedError

####################################################################################################

class KeyValueParameter(ElementParameter):

    ##############################################

    def str_value(self):
        return str(self.value)

    ##############################################

    def __str__(self):

        if bool(self):
            return '{}={}'.format(self.spice_name, self.str_value())
        else:
            return ''

####################################################################################################

class IntKeyParameter(KeyValueParameter):

    ##############################################

    def validate(self, value):
        return int(value)

####################################################################################################

class FloatKeyParameter(KeyValueParameter):

    ##############################################

    def validate(self, value):
        return float(value)

####################################################################################################

class FloatPairKeyParameter(KeyValueParameter):

    ##############################################

    def str_value(self):
        return ','.join([str(value) for value in self.value])

    ##############################################

    def validate(self, pair):

        if len(pair) == 2:
            return (float(pair[0]), float(pair[1]))
        else:
            raise ValueError()

####################################################################################################

class FlagKeyParameter(ElementParameter):

    def __init__(self, spice_name, default=False):

        super(FlagKeyParameter, self).__init__(spice_name, default)

    ##############################################

    def __nonzero__(self):
        return bool(self.value)

    ##############################################

    def __str__(self):

        if bool(self):
            return 'off'
        else:
            return ''

####################################################################################################

class BoolKeyParameter(ElementParameter):

    def __init__(self, spice_name, default=False):

        super(BoolKeyParameter, self).__init__(spice_name, default)

    ##############################################

    def __nonzero__(self):
        return bool(self.value)

    ##############################################

    def __str__(self):

        if bool(self):
            return '0'
        else:
            return '1'

####################################################################################################

class ExpressionKeyParameter(KeyValueParameter):

    ##############################################

    def validate(self, value):
        return str(value)

####################################################################################################

class ElementParameterMetaClass(type):

    ##############################################

    def __new__(cls, name, bases, attributes):

        parameters = {}
        for attribute_name, obj in attributes.iteritems():
            if isinstance(obj, ElementParameter):
                obj.attribute_name = attribute_name
                parameters[attribute_name] = obj
        attributes['optional_parameters'] = parameters

        return super(ElementParameterMetaClass, cls).__new__(cls, name, bases, attributes)

####################################################################################################

class Element(object):

    """ This class implements a base class for an element. """

    __metaclass__ = ElementParameterMetaClass

    prefix = None

    ##############################################

    def __init__(self, name, pins, *args, **kwargs):

        self._name = str(name)
        self._pins = list(pins) # Fixme: pins is not a ordered dict, cf. property
        self._parameters = list(args)

        for key, value in kwargs.iteritems():
            if key in self.optional_parameters:
                setattr(self, key, value)

    ##############################################

    @property
    def name(self):
        return self.prefix + self._name

    ##############################################

    @property
    def pins(self):
        return self._pins

    ##############################################

    @property
    def nodes(self):
        return [pin.node for pin in self._pins]

    ##############################################

    @property
    def parameters(self):
        return self._parameters

    ##############################################

    def __repr__(self):

        return self.__class__.__name__ + ' ' + self.name

    ##############################################

    def format_node_names(self):

        return join_list((self.name, join_list(self.nodes)))

    ##############################################

    def format_spice_parameters(self):

        return join_list(str(parameter)
                         for parameter in self.optional_parameters.itervalues()
                         if bool(parameter))

    ##############################################

    def __str__(self):

        return join_list((self.format_node_names(),
                          join_list(self.parameters),
                          self.format_spice_parameters()))

####################################################################################################

class SubCircuitElement(Element):

    """ This class implements a sub-circuit. """

    prefix = 'X'

    ##############################################

    def __init__(self, name, subcircuit_name, *nodes):

        pins = [Pin(self, None, node) for node in nodes]

        super(SubCircuitElement, self).__init__(name, pins, subcircuit_name)

####################################################################################################

class TwoPinElement(Element):

    """ This class implements a base class for a two-pin element. """

    ##############################################

    def __init__(self, name, node_plus, node_minus, *args, **kwargs):

        pins = (Pin(self, 'plus', node_plus), Pin(self, 'minus', node_minus))

        super(TwoPinElement, self).__init__(name, pins, *args, **kwargs)

    ##############################################

    @property
    def plus(self):
        return self.pins[0]

    ##############################################

    @property
    def minus(self):
        return self.pins[1]

####################################################################################################

class TwoPortElement(Element):

    """ This class implements a base class for a two-port element.

    Input nodes comes before to output nodes contrary to Spice.
    """

    ##############################################

    def __init__(self, name,
                 input_node_plus, input_node_minus,
                 output_node_plus, output_node_minus,
                 *args, **kwargs):

        pins = (Pin(self, 'output_plus', output_node_plus),
                Pin(self, 'output_minus', output_node_minus),
                Pin(self, 'input_plus', input_node_plus),
                Pin(self, 'input_minus', input_node_minus))

        super(TwoPortElement, self).__init__(name, pins, *args, **kwargs)

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

class ElementWithValue(Element):

    """ This class implements a base class for an element with a mandatory parameter value. """

    ##############################################

    @property
    def value(self):

        value = self._parameters[0]
        if isinstance(value, Unit):
            return value
        else:
            return Unit(value)

    ##############################################

    @property
    def float_value(self):
        return float(self._parameters[0]) # self.value

####################################################################################################

class TwoPinElementWithValue(TwoPinElement, ElementWithValue):
    """ This class implements a base class for a two-pin element with a mandatory parameter value. """

####################################################################################################

class TwoPortElementWithValue(TwoPortElement, ElementWithValue):
    """ This class implements a base class for a two-port element with a mandatory parameter value. """

####################################################################################################

class Node(object):

    """ This class implements a node in the circuit. """

    ##############################################

    def __init__(self, name):

        self._name = name
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

class Netlist(object):

    """ This class implements a base class for a netlist. """

    ##############################################

    def __init__(self):

        self._ground = None
        self._elements = {}
        self._models = {}
        self._dirty = True
        # self._nodes = set()
        self._nodes = {}

        # self._graph = networkx.Graph()

    ##############################################

    def element_iterator(self):

        return self._elements.itervalues()

    ##############################################

    def model_iterator(self):

        return self._models.itervalues()

    ##############################################

    def __str__(self):

        netlist = join_lines(self.element_iterator()) + '\n'
        if self._models:
            netlist += join_lines(self.model_iterator()) + '\n'
        return netlist

    ##############################################

    def _add_element(self, element):

        if element.name not in self._elements:
            self._elements[element.name] = element
            self._dirty = True
        else:
            raise NameError("Element name {} is already defined".format(element.name))

    ##############################################

    def model(self, name, modele_type, **parameters):

        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model

    ##############################################

    @property
    def nodes(self):

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
        return self._nodes.values()

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

    ##############################################

    def X(self, *args):
        self._add_element(SubCircuitElement(*args))

####################################################################################################

class SubCircuit(Netlist):

    """ This class implements a sub-cicuit netlist. """

    ##############################################

    def __init__(self, name, *nodes, **kwargs):

        super(SubCircuit, self).__init__()

        self.name = str(name)
        self._external_nodes = list(nodes)
        self._ground = kwargs.get('ground', 0)
        
    ##############################################

    @property
    def gnd(self):
        """ Local ground """
        return self._ground

    ##############################################

    def check_nodes(self):

        nodes = set(self._external_nodes)
        connected_nodes = set()
        for element in self.element_iterator():
            connected_nodes.add(nodes & element.nodes)
        not_connected_nodes = nodes - connected_nodes
        if not_connected_nodes:
            raise NameError("SubCircuit Nodes {} are not connected".format(not_connected_nodes))

    ##############################################

    def __str__(self):

        netlist = '.subckt {} {}\n'.format(self.name, join_list(self._external_nodes))
        netlist += super(SubCircuit, self).__str__()
        netlist += '.ends\n'
        return netlist

####################################################################################################

class Circuit(Netlist):

    """ This class implements a cicuit netlist.

    To get the corresponding Spice source use::

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

        super(Circuit, self).__init__()

        self.title = str(title)
        self._ground = ground
        self._global_nodes = set(global_nodes) # .global
        self._includes = set() # .include
        self._parameters = {} # .param
        self._subcircuits = {}

    ##############################################

    @property
    def gnd(self):
        return self._ground

    ##############################################

    def include(self, path):

        """ Include a file. """

        self._includes.add(path)

    ##############################################

    def parameter(self, name, expression):

        """ Set a parameter. """
        
        self._parameters[str(name)] = str(expression)

    ##############################################

    def subcircuit(self, subcircuit):

        """ Add a sub-circuit. """

        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def subcircuit_iterator(self):

        """ Return a sub-circuit iterator. """

        return self._subcircuits.itervalues()

    ##############################################

    def __str__(self):

        netlist = '.title {}\n'.format(self.title)
        if self._includes:
            netlist += join_lines(self._includes, prefix='.include ')  + '\n'
        if self._global_nodes:
            netlist += '.global ' + join_list(self._global_nodes) + '\n'
        if self._parameters:
            netlist += join_lines(self._parameters, prefix='.param ') + '\n'
        if self._subcircuits:
            netlist += join_lines(self.subcircuit_iterator())
        netlist += super(Circuit, self).__str__()
        netlist += '.end\n'
        return netlist

    ##############################################

    def simulator(self, *args, **kwargs):
        return CircuitSimulator(self, *args, **kwargs)

####################################################################################################
# 
# End
# 
####################################################################################################
