####################################################################################################
# 
# @Project@ - @ProjectDescription@.
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

def join_lines(items, prefix=''):
    return '\n'.join([prefix + str(item) for item in items])

####################################################################################################

def join_list(items):
    return ' '.join([str(item) for item in items])

####################################################################################################

def join_dict(d):
    return ' '.join(["{}={}".format(key, value) for key, value in d.iteritems()])

####################################################################################################

class Element(object):

    ##############################################

    def __init__(self, name, nodes, *args, **kwargs):

        self.name = str(name)
        self.nodes = list(nodes)
        self.parameters = list(args)
        self.dict_parameters = dict(kwargs)

    ##############################################

    def __str__(self):

        return "{} {} {} {}".format(self.name,
                                    join_list(self.nodes),
                                    join_list(self.parameters),
                                    join_dict(self.dict_parameters),
                                   )

####################################################################################################

class DeviceModel(object):

    ##############################################

    def __init__(self, name, modele_type, **parameters):

        self.name = str(name)
        self.model = str(modele_type)
        self.parameters = dict(**parameters)

    ##############################################

    def __str__(self):

        return ".model {} {} ({})".format(self.name, self.model, join_dict(self.parameters))

####################################################################################################

class Netlist(object):

    ##############################################

    def __init__(self):

        self._ground = None
        self._elements = {}
        self._models = {}
        self._dirty = True
        self._nodes = set()

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

    def element(self, name, nodes, *args, **kwargs):

        element = Element(name, nodes, *args, **kwargs)
        if element.name not in self._elements:
            self._elements[element.name] = element
        self._dirty = True

    ##############################################

    def _prefix_element(self, prefix, name, nodes, *args, **kwargs):
        self.element(prefix+name, nodes, *args, **kwargs)

    ##############################################

    def model(self, name, modele_type, **parameters):

        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model

    ##############################################

    @property
    def nodes(self):

        if self._dirty:
            nodes = set()
            for element in self.element_iterator():
                nodes |= set(element.nodes)
            if self._ground is not None:
                nodes -= set((self._ground,))
            self._nodes = nodes
        return self._nodes

    ##############################################

    def __getitem__(self, attribute_name):

        if attribute_name in self._elements:
            return self._elements[attribute_name]
        elif attribute_name in self._models:
            return self._models[attribute_name]
        elif attribute_name in self.nodes:
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

    def X(self, name, subcircuit_name, *nodes):
        self._prefix_element('x', name, nodes, subcircuit_name)

    ##############################################

    def R(self, name, node_plus, node_minus, *args, **kwargs):

        """
        Resistors
        RXXXXXXX n+ n- value <ac=val> <m=val> <scale=val> <temp=val> <dtemp=val> <noisy=0|1>

        Semiconductor Resistors
        RXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <temp=val> <dtemp=val> m=<val> <ac=val> <scale=val> <noisy=0|1>

        Resistors, dependent on expressions (behavioral resistor)
        RXXXXXXX n+ n- R='expression' <tc1=value> <tc2=value>
        RXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        """

        self._prefix_element('R', name, (node_plus, node_minus), *args, **kwargs)

    ##############################################

    def C(self, name, node_plus, node_minus, *args, **kwargs):

        """
        Capacitors
        CXXXXXXX n+ n- <value> <mname> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
        
        Semiconductor Capacitors
        CXXXXXXX n+ n- <value> <mname> <l=length> <w=width> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>
        
        Capacitors, dependent on expressions (behavioral capacitor)
        CXXXXXXX n+ n- C='expression' <tc1=value> <tc2=value>
        CXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        """

        self._prefix_element('C', name, (node_plus, node_minus), *args, **kwargs)

    ##############################################

    def L(self, name, node_plus, node_minus, *args, **kwargs):

        """
        Inductors
        LYYYYYYY n+ n- <value> <mname> <nt=val> <m=val> <scale=val> <temp=val> <dtemp=val> <ic=init_condition>

        Inductors, dependent on expressions (behavioral inductor)
        LXXXXXXX n+ n- L='expression' <tc1=value> <tc2=value>
        LXXXXXXX n+ n- 'expression' <tc1=value> <tc2=value>
        """

        self._prefix_element('L', name, (node_plus, node_minus), *args, **kwargs)

    ##############################################

    def D(self, name, node_plus, node_minus, *args, **kwargs):

        """
        Junction Diodes
        DXXXXXXX n+ n- mname <area=val> <m=val> <pj=val> <off> <ic=vd> <temp=val> <dtemp=val>
        """

        self._prefix_element('D', name, (node_plus, node_minus), *args, **kwargs)

    ##############################################

    def V(self, name, node_plus, node_minus, *args, **kwargs):

        """
        Independent Sources for Voltage or Current
        VXXXXXXX N+ N- <<DC> DC/TRAN VALUE> <AC <ACMAG <ACPHASE>>> <DISTOF1 <F1MAG <F1PHASE>>> <DISTOF2 <F2MAG <F2PHASE>>>
        """

        self._prefix_element('V', name, (node_plus, node_minus), *args, **kwargs)

    ##############################################

    # def (self, name, node_plus, node_minus, *args, **kwargs):

    #     """
    #     """

    #     self._prefix_element('', name, (node_plus, node_minus), *args, **kwargs)

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
