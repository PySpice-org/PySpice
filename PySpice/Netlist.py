####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

def tera(x):
    """ T Tera 1e12 """
    return x*1e12

def giga(x):
    """ G Giga 1e9 """
    return x*1e9

def mega(x):
    """ Meg Mega 1e6 """
    return x*1e6

def kilo(x):
    """ K Kilo 1e3 """
    return x*1e3

def mil(x):
    """ mil Mil 25.4e-6 """
    return x*25.4e-6

def milli(x):
    """ m milli 1e-3 """
    return x*1e-3

def micro(x):
    """ u micro 1e-6 """
    return x*1e-6

def nano(x):
    """ n nano 1e-9 """
    return x*1e-9

def pico(x):
    """ p pico 1e-12 """
    return x*1e-12

def femto(x):
    """ f femto 1e-15 """
    return x*1e-15

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
        self.nodes = set(nodes)
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

        self._elements = {}
        self._models = {}

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

    ##############################################

    def _prefix_element(self, prefix, name, nodes, *args, **kwargs):
        self.element(prefix+name, nodes, *args, **kwargs)

    ##############################################

    def model(self, name, modele_type, **parameters):

        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model

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
        self.nodes = set(nodes)

    ##############################################

    def check_nodes(self):

        connected_nodes = set()
        for element in self.element_iterator():
            connected_nodes.add(self.nodes & element.nodes)
        not_connected_nodes = self.nodes - connected_nodes
        if not_connected_nodes:
            raise NameError("SubCircuit Nodes {} are not connected".format(not_connected_nodes))

    ##############################################

    def __str__(self):

        netlist = '.subckt {} {}\n'.format(self.name, join_list(self.nodes))
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
                 global_nodes=(),
             ):

        super(Circuit, self).__init__()

        self.title = str(title)
        self._global_nodes = set(global_nodes) # .global
        self._includes = set() # .include
        self._parameters = {} # .param
        self._options = {} # .options
        self._subcircuits = {}
        self._saved_nodes = ()
        self._analysis_parameters = {}

    ##############################################

    def parameter(self, name, expression):

        self._parameters[str(name)] = str(expression)

    ##############################################

    def options(self, *args, **kwargs):

        for item in args:
            self._options[str(item)] = None
        for key, value in kwargs.iteritems():
            self._options[str(key)] = str(value)

    ##############################################

    def subcircuit(self, subcircuit):

        self._subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def subcircuit_iterator(self):

        return self._subcircuits.itervalues()

    ##############################################

    def save(self, *args):

        self._saved_nodes = list(args)

    ##############################################

    def tran(self, *args):

        self._analysis_parameters['tran'] = list(args)

    ##############################################

    def __str__(self):

        netlist = '.title {}\n'.format(self.title)
        if self._includes:
            netlist += join_lines(self._includes, prefix='.include ')  + '\n'
        if self.options:
            for key, value in self._options.iteritems():
                if value is not None:
                    netlist += '.options {} = {}\n'.format(key, value)
                else:
                    netlist += '.options {}\n'.format(key)
        if self._global_nodes:
            netlist += '.global ' + join_list(self._global_nodes) + '\n'
        if self._parameters:
            netlist += join_lines(self._parameters, prefix='.param ') + '\n'
        if self._subcircuits:
            netlist += join_lines(self.subcircuit_iterator())
        netlist += super(Circuit, self).__str__()
        if self._saved_nodes:
            netlist += '.save ' + join_list(self._saved_nodes) + '\n'
        for analysis, analysis_parameters in self._analysis_parameters.iteritems():
            netlist += '.' + analysis + ' ' + join_list(analysis_parameters) + '\n'
        netlist += '.end\n'
        return netlist

####################################################################################################
# 
# End
# 
####################################################################################################
