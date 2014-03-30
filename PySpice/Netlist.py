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

####################################################################################################

def join_lines(items, prefix=''):
    return '\n'.join([prefix + str(item) for item in items])

####################################################################################################

def join_list(items):
    return ' '.join([str(item) for item in items])

####################################################################################################

def join_dict(d):
    return ' '.join(["{}={}".format(key, value) for key, value in d.iteritems()])

####################################################################################################

class DeviceModel(object):

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

        node = self.node
        self.node = '_'.join((self.element.name, self.name))
        circuit.V(self.node, node, self.node, '0')

####################################################################################################

class Element(object):

    prefix = None

    ##############################################

    def __init__(self, name, pins, *args, **kwargs):

        self._name = str(name)
        self._pins = list(pins)
        self._parameters = list(args)
        self._dict_parameters = dict(kwargs)

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

    def __repr__(self):

        return self.__class__.__name__ + ' ' + self.name

    ##############################################

    def __str__(self):

        return "{} {} {} {}".format(self.name,
                                    join_list(self.nodes),
                                    join_list(self._parameters),
                                    join_dict(self._dict_parameters),
                                   )

####################################################################################################

class SubCircuitElement(Element):

    prefix = 'X'

    ##############################################

    def __init__(self, name, subcircuit_name, *nodes):

        pins = [Pin(self, None, node) for node in nodes]

        super(SubCircuitElement, self).__init__(name, pins, subcircuit_name)

####################################################################################################

class TwoPortElement(Element):

    ##############################################

    def __init__(self, name, node_plus, node_minus, *args, **kwargs):

        pins = (Pin(self, 'plus', node_plus), Pin(self, 'minus', node_minus))

        super(TwoPortElement, self).__init__(name, pins, *args, **kwargs)

    ##############################################

    @property
    def plus(self):
        return self.pins[0]

    ##############################################

    @property
    def minus(self):
        return self.pins[1]

####################################################################################################

class Node(object):

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

    ##############################################

    def __init__(self, name, *nodes):

        super(SubCircuit, self).__init__()

        self.name = str(name)
        self._external_nodes = set(nodes)

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

        self._includes.add(path)

    ##############################################

    def parameter(self, name, expression):

        self._parameters[str(name)] = str(expression)

    ##############################################

    def subcircuit(self, subcircuit):

        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def subcircuit_iterator(self):

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

    def simulation(self, *args, **kwargs):
        return CircuitSimulation(self, *args, **kwargs)

####################################################################################################

class CircuitSimulation(object):

    ##############################################

    def __init__(self, circuit,
                 temperature=27,
                 nominal_temperature=27,
                 pipe=False
                ):

        self._circuit = circuit

        self._options = {} # .options
        self._saved_nodes = ()
        self._analysis_parameters = {}

        self.temperature = temperature
        self.nominal_temperature = nominal_temperature

        if pipe:
            self.options('NOINIT')
            self.options(filetype='binary')

    ##############################################

    def options(self, *args, **kwargs):

        for item in args:
            self._options[str(item)] = None
        for key, value in kwargs.iteritems():
            self._options[str(key)] = str(value)

    ##############################################

    @property
    def temperature(self):
        return self._options['TEMP']

    @temperature.setter
    def temperature(self, value):
        self._options['TEMP'] = value

    ##############################################

    @property
    def nominal_temperature(self):
        return self._options['TNOM']

    @nominal_temperature.setter
    def nominal_temperature(self, value):
        self._options['TNOM'] = value

    ##############################################

    def save(self, *args):

        self._saved_nodes = list(args)

    ##############################################

    def tran(self, *args):

        self._analysis_parameters['tran'] = list(args)

    ##############################################

    def __str__(self):

        netlist = str(self._circuit)
        if self.options:
            for key, value in self._options.iteritems():
                if value is not None:
                    netlist += '.options {} = {}\n'.format(key, value)
                else:
                    netlist += '.options {}\n'.format(key)
        if self._saved_nodes:
            netlist += '.save ' + join_list(self._saved_nodes) + '\n'
        for analysis, analysis_parameters in self._analysis_parameters.iteritems():
            netlist += '.' + analysis + ' ' + join_list(analysis_parameters) + '\n'
        return netlist

####################################################################################################
# 
# End
# 
####################################################################################################
