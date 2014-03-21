####################################################################################################
# 
# @Project@ - @ProjectDescription@.
# Copyright (C) 2014 Fabrice Salvaire
# 
####################################################################################################

####################################################################################################

def join_lines(items, prefix=''):
    return '\n'.join([prefix + str(item) for item in items])

####################################################################################################

def join_list(items):
    return ' '.join([str(item) for item in items])

####################################################################################################

def join_dict(d):
    return ' '.join(["{} = {}".format(key, value) for key, value in d.iteritems()])

####################################################################################################

class Element(object):

    ##############################################

    def __init__(self, name, nodes, parameters):

        self.name = str(name)
        self.nodes = set(nodes)
        self.parameters = str(parameters)

    ##############################################

    def __str__(self):

        return "{} {} {}".format(self.name, join_list(self.nodes), self.parameters)

####################################################################################################

class DeviceModel(object):

    ##############################################

    def __init__(self, name, modele_type, **parameters):

        self.name = str(name)
        self.model = str(modele_type)
        self.parameters = dict(**parameters)

    ##############################################

    def __str__(self):

        return "{} {} {}".format(self.name, self.model, join_dict(self.parameters))

####################################################################################################

class Netlist(object):

    ##############################################

    def __init__(self):

        self._elements = {}
        self._models = {}

    ##############################################

    def add_element(self, name, nodes, parameters):

        element = Element(name, nodes, parameters)
        if element.name not in self._elements:
            self._elements[element.name] = element

    ##############################################

    def add_model(self, name, modele_type, **parameters):

        model = DeviceModel(name, modele_type, **parameters)
        if model.name not in self._models:
            self._models[model.name] = model

    ##############################################

    def element_iterator(self):

        return self._elements.itervalues()

    ##############################################

    def model_iterator(self):

        return self._models.itervalues()

    ##############################################

    def __str__(self):

        netlist = join_lines(self.element_iterator())
        if self._models:
            netlist += '\n'
            netlist += join_lines(self.model_iterator()) + '\n'
        return netlist

####################################################################################################

class SubCircuit(Netlist):

    ##############################################

    def __init__(self, name, nodes):

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

        netlist = '.SUBCKT {} {}\n'.format(self.name, join_list(self.nodes))
        netlist += super(SubCircuit, self).__str__()
        netlist += '.ENDS\n'
        return netlist

####################################################################################################

class Circuit(Netlist):

    # .LIB

    ##############################################

    def __init__(self, title,
                 global_nodes=(),
             ):

        super(Circuit, self).__init__()

        self.title = str(title)
        self.global_nodes = set(global_nodes) # .GLOBAL
        self.includes = set() # .INCLUDE
        self.parameters = {} # .PARAM
        self.options = {} # .OPTIONS
        self.subcircuits = {}
        self.saved_nodes = ()
        self.analysis_parameters = {}

    ##############################################

    def add_parameter(self, name, expression):

        self.parameters[str(name)] = str(expression)

    ##############################################

    def add_options(self, *args, **kwargs):

        for item in args:
            self.options[str(item)] = None
        for key, value in kwargs.iteritems():
            self.options[str(key)] = str(value)

    ##############################################

    def add_subcircuit(self, subcircuit):

        self.subcircuits[str(subcircuit.name)] = subcircuit

    ##############################################

    def subcircuit_iterator(self):

        return self.subcircuits.itervalues()

    ##############################################

    def save(self, *args):

        self.saved_nodes = list(args)

    ##############################################

    def tran(self, *args):

        self.analysis_parameters['tran'] = list(args)

    ##############################################

    def __str__(self):

        netlist = '.TITLE {}\n'.format(self.title)
        if self.includes:
            netlist += join_lines(self.includes, prefix='.INCLUDE ')  + '\n'
        if self.options:
            for key, value in self.options.iteritems():
                if value is not None:
                    netlist += '.OPTIONS {} = {}\n'.format(key, value)
                else:
                    netlist += '.OPTIONS {}\n'.format(key)
        if self.global_nodes:
            netlist += '.GLOBAL ' + join_list(self.global_nodes) + '\n'
        if self.parameters:
            netlist += join_lines(self.parameters, prefix='.PARAM ') + '\n'
        if self.subcircuits:
            netlist += join_lines(self.subcircuit_iterator())
        netlist += super(Circuit, self).__str__()
        if self.saved_nodes:
            netlist += '.SAVE ' + join_list(self.saved_nodes) + '\n'
        for analysis, analysis_parameters in self.analysis_parameters.iteritems():
            netlist += '.' + analysis + join_list(analysis_parameters) + '\n'
        netlist += '.END\n'
        return netlist

####################################################################################################
# 
# End
# 
####################################################################################################
