import logging
import os
import csv
import sys

from unicodedata import normalize
from collections import OrderedDict
from .EBNFExpressionParser import ExpressionModelWalker
from ..Unit.Unit import UnitValue, ZeroPower, PrefixedUnit
from ..Tools.StringTools import join_lines
from .Expressions import *
from .Netlist import (Circuit,
                      SubCircuit)
from .BasicElement import (BehavioralSource,
                           BipolarJunctionTransistor,
                           Capacitor,
                           CoupledInductor,
                           CurrentSource,
                           Diode,
                           Inductor,
                           JunctionFieldEffectTransistor,
                           Mosfet,
                           Resistor,
                           SubCircuitElement,
                           VoltageControlledSwitch,
                           VoltageSource)
from .HighLevelElement import (ExponentialCurrentSource,
                               ExponentialMixin,
                               ExponentialVoltageSource,
                               PatternCurrentSource,
                               PatternMixin,
                               PatternVoltageSource,
                               PieceWiseLinearCurrentSource,
                               PieceWiseLinearMixin,
                               PieceWiseLinearVoltageSource,
                               PulseCurrentSource,
                               PulseMixin,
                               PulseVoltageSource,
                               SinusoidalCurrentSource,
                               SinusoidalMixin,
                               SinusoidalVoltageSource,
                               SingleFrequencyFMCurrentSource,
                               SingleFrequencyFMMixin,
                               SingleFrequencyFMVoltageSource)

from .SpiceGrammar import SpiceParser as parser
from .SpiceModel import SpiceModelBuilderSemantics
from tatsu import to_python_sourcecode, to_python_model, compile
from tatsu.model import NodeWalker

_module_logger = logging.getLogger(__name__)


class ParseError(NameError):
    pass


class Statement:
    """ This class implements a statement, in fact a line in a Spice netlist. """

    @staticmethod
    def arg_to_python(x):

        if x:
            if str(x)[0].isdigit():
                return str(x)
            else:
                return "'{}'".format(x)
        else:
            return ''

    @staticmethod
    def args_to_python(*args):

        return [Statement.arg_to_python(x) for x in args]

    @staticmethod
    def kwargs_to_python(self, **kwargs):
        return Statement.join_args(*['{}={}'.format(key, self.value_to_python(value))
                                     for key, value in kwargs.items()])

    @staticmethod
    def join_args(self, *args):
        return ', '.join(args)


class DataStatement(Statement):
    """ This class implements a data definition.

    Spice syntax::

        .data name, name, ..., value, value, value, value...

    """

    ##############################################

    def __init__(self, table, **parameters):
        self._table = table
        self._parameters = parameters

    @property
    def table(self):
        """ Name of the model """
        return self._table

    ##############################################

    @property
    def names(self):
        """ Name of the model """
        return self._parameters.keys()

    ##############################################

    def __repr__(self):
        return 'Data {}'.format(Statement.kwargs_to_python(**self._parameters))

    ##############################################

    def to_python(self, netlist_name):
        kwargs = "{{{}}}".format(", ".join(["{} = ({})".format(param, ", ".join(values))
                                            for param, values in self._parameters.items]))
        return '{}.data({}, {})'.format(netlist_name, self._table, kwargs) + os.linesep

    ##############################################

    def build(self, circuit):
        circuit.data(self._table, self._parameters)


class IncludeStatement(Statement):
    """ This class implements a include definition. """

    ##############################################

    def __init__(self, parent, filename):
        self._include = filename
        root, _ = os.path.split(parent.path)
        file_name = os.path.abspath(os.path.join(root,
                                                 self._include.replace('"', '')))
        if not (os.path.exists(file_name) and os.path.isfile(file_name)):
            raise ParseError("{}: File not found: {}".format(parent.path, file_name))
        try:
            self._contents = SpiceParser.parse(path=file_name)
        except Exception as e:
            raise ParseError("{}: {:s}".format(parent.path, e))

    ##############################################

    def __str__(self):
        return self._include

    ##############################################

    def __repr__(self):
        return 'Include {}'.format(self._include)

    ##############################################

    def to_python(self, netlist_name):
        return '{}.include({})'.format(netlist_name, self._include) + os.linesep

    def contents(self):
        return self._contents


class ModelStatement(Statement):
    """ This class implements a model definition.

    Spice syntax::

        .model mname type (pname1=pval1 pname2=pval2)

    """

    def __eq__(self, other):
        return isinstance(other, ModelStatement) and self._name == other._name

    def __hash__(self):
        return hash(self._name)

    ##############################################

    def __init__(self, name, device, **parameters):
        self._name = str(name).lower()
        self._model_type = device
        self._parameters = parameters

    ##############################################

    @property
    def name(self):
        """ Name of the model """
        return self._name

    ##############################################

    def __repr__(self):
        return 'Model {} {} {}'.format(self._name, self._model_type, self._parameters)

    ##############################################

    def to_python(self, netlist_name):
        args = self.values_to_python((self._name, self._model_type))
        kwargs = self.kwargs_to_python(self._parameters)
        return '{}.model({})'.format(netlist_name, self.join_args(args + kwargs)) + os.linesep

    ##############################################

    def build(self, circuit):
        return circuit.model(self._name, self._model_type, **self._parameters)


####################################################################################################

class ParamStatement(Statement):
    """ This class implements a param definition.

    Spice syntax::

        .param name=expr

    """

    ##############################################

    def __init__(self, **parameters):
        self._parameters = parameters

    ##############################################

    @property
    def names(self):
        """ Name of the model """
        return self._parameters.keys()

    ##############################################

    def __repr__(self):
        return 'Param {}'.format(Statement.kwargs_to_python(**self._parameters))

    ##############################################

    def to_python(self, netlist_name):
        args = self.values_to_python((self._name, self._value))
        return '{}.param({})'.format(netlist_name, self.join_args(args)) + os.linesep

    ##############################################

    def build(self, circuit):
        for key, value in self._parameters.items():
            circuit.parameter(key, value)


class ElementStatement(Statement):
    """ This class implements an element definition.

    "{ expression }" are allowed in device line.

    """

    _logger = _module_logger.getChild('Element')

    ##############################################

    def __init__(self, statement, name, *nodes, **params):
        self._statement = statement
        self._prefix = name[0]
        self._name = name[1:]
        self._nodes = nodes
        self._params = params

    ##############################################

    @property
    def name(self):
        """ Name of the element """
        return self._name

    ##############################################

    def __repr__(self):
        return 'Element {0._prefix} {0._name} {0._nodes} {0._params}'.format(self)

    ##############################################

    def translate_ground_node(self, ground):

        nodes = []
        for idx, node in enumerate(self._nodes):
            if str(node) == str(ground):
                self._node[idx] = 0

        return nodes

    ##############################################

    def to_python(self, netlist_name, ground=0):

        args = self.translate_ground_node(ground)
        args = self.values_to_python(args)
        kwargs = self.kwargs_to_python(self._dict_parameters)
        return '{}.{}({})'.format(netlist_name,
                                  self._prefix, self.join_args(args + kwargs)) + os.linesep

    def build(self, circuit, ground=0):
        return self._statement(circuit, self._name, *self._nodes, **self._params)


class LibraryStatement(Statement):
    """ This class implements a library definition.

    Spice syntax::

        .LIB entry
        .ENDL [entry]

    """

    ##############################################

    def __init__(self, entry):
        self._entry = entry

        self._statements = []
        self._subcircuits = []
        self._models = []
        self._params = []

    ##############################################

    @property
    def entry(self):
        """ Name of the sub-circuit. """
        return self._entry

    @property
    def models(self):
        """ Models of the sub-circuit. """
        return self._models

    @property
    def params(self):
        """ Params of the sub-circuit. """
        return self._params

    @property
    def subcircuits(self):
        """ Subcircuits of the sub-circuit. """
        return self._subcircuits

    ##############################################

    def __repr__(self):
        text = 'LIB {}'.format(self._entry) + os.linesep
        text += os.linesep.join([repr(model) for model in self._models]) + os.linesep
        text += os.linesep.join([repr(subcircuit) for subcircuit in self._subcircuits]) + os.linesep
        text += os.linesep.join(['  ' + repr(statement) for statement in self._statements])
        return text

    ##############################################

    def __iter__(self):
        """ Return an iterator on the statements. """
        return iter(self._models + self._subcircuits + self._statements)

    ##############################################

    def append(self, statement):
        """ Append a statement to the statement's list. """
        self._statements.append(statement)

    def appendModel(self, statement):

        """ Append a model to the statement's list. """

        self._models.append(statement)

    def appendParam(self, statement):

        """ Append a param to the statement's list. """

        self._params.append(statement)

    def appendSubCircuit(self, statement):

        """ Append a model to the statement's list. """

        self._subcircuits.append(statement)

    ##############################################

    def to_python(self, ground=0):

        lib_name = 'lib_' + self._entry
        source_code = ''
        source_code += '{} = Lib({})'.format(lib_name, self._entry) + os.linesep
        source_code += SpiceParser.netlist_to_python(lib_name, self, ground)
        return source_code


class LibCallStatement(Statement):
    """ This class implements a library call statement.

    Spice syntax::

        .lib library entry

    """

    ##############################################

    def __init__(self, library, entry):
        self._library = library
        self._entry = entry

    ##############################################

    @property
    def name(self):
        """ Name of the library """
        return self._library

    ##############################################

    @property
    def entry(self):
        """ Entry in the library """
        return self._entry

    ##############################################

    def __repr__(self):
        return 'Library {} {}'.format(self._library, self._entry)

    ##############################################

    def to_python(self, netlist_name):
        args = self.values_to_python((self._name, self._model_type))
        kwargs = self.kwargs_to_python(self._parameters)
        return '{}.include({}, {})'.format(netlist_name, self._library, self._entry) + os.linesep

    ##############################################

    def build(self, circuit, libraries):
        library = libraries[self._entry]
        for statement in library._params:
            statement.build(circuit)
        for statement in library._models:
            statement.build(circuit)
        for statement in library._subcircuits:
            statement.build(circuit, parent=circuit)
        return circuit


class SubCircuitStatement(Statement):
    """ This class implements a sub-circuit definition.

    Spice syntax::

        .SUBCKT name node1 ... param1=value1 ...

    """

    ##############################################
    def __eq__(self, other):
        return isinstance(other, SubCircuitStatement) and self._name == other._name

    def __hash__(self):
        return hash(self._name)

    def __init__(self, name, *nodes, **params):

        self._name = str(name).lower()
        self._nodes = nodes
        self._params = params

        self._statements = []
        self._subcircuits = OrderedDict()
        self._models = OrderedDict()
        self._required_subcircuits = OrderedDict()
        self._required_models = set()
        self._parameters = []
        self._parent = None

    ##############################################

    @property
    def name(self):
        """ Name of the sub-circuit. """
        return self._name

    @property
    def nodes(self):
        """ Nodes of the sub-circuit. """
        return self._nodes

    @property
    def models(self):
        """ Models of the sub-circuit. """
        return self._models

    @property
    def params(self):
        """ Params of the sub-circuit. """
        return self._params

    @property
    def subcircuits(self):
        """ Subcircuits of the sub-circuit. """
        return self._subcircuits

    ##############################################

    def __repr__(self):
        if self._params:
            text = 'SubCircuit {} {} Params: {}'.format(self._name, self._nodes, self._params) + os.linesep
        else:
            text = 'SubCircuit {} {}'.format(self._name, self._nodes) + os.linesep
        text += os.linesep.join([repr(model) for model in self._models]) + os.linesep
        text += os.linesep.join([repr(subcircuit) for subcircuit in self._subcircuits]) + os.linesep
        text += os.linesep.join(['  ' + repr(statement) for statement in self._statements])
        return text

    ##############################################

    def __iter__(self):
        """ Return an iterator on the statements. """
        return iter(self._parameters + self._models + self._subcircuits + self._statements)

    ##############################################

    def append(self, statement):
        """ Append a statement to the statement's list. """
        self._statements.append(statement)
        if len(statement.name) > 0 and statement.name[0] in "xX":
            self._required_subcircuits[statement.model] = None

    def appendModel(self, statement):

        """ Append a model to the models list. """

        self._models[statement._name] = statement

    def appendParam(self, statement):

        """ Append a param to the parameters list. """

        self._parameters.append(statement)

    def appendSubCircuit(self, statement):

        """ Append a subcircuit to the subcircuits list. """
        statement._parent = self
        self._subcircuits[statement._name] = statement

    ##############################################

    def to_python(self, ground=0):

        subcircuit_name = 'subcircuit_' + self._name
        args = self.values_to_python([subcircuit_name] + self._nodes)
        source_code = ''
        source_code += '{} = SubCircuit({})'.format(subcircuit_name, self.join_args(args)) + os.linesep
        source_code += SpiceParser.netlist_to_python(subcircuit_name, self, ground)
        return source_code

    ##############################################

    def _build(self, ground, netlist):
        for statement in self._parameters:
            statement.build(netlist)
        for name, statement in self._models.items():
            statement.build(netlist)
        # Check subcircuits
        names = list(self._required_subcircuits.keys())
        for name in names:
            req_subcircuit = self._required_subcircuits[name]
            if req_subcircuit is None:
                # Search for the subcircuit
                valid_subcircuit = self._search_build_subcircuit(name, ground, netlist)
                if valid_subcircuit is not None:
                    self._required_subcircuits[name] = id(valid_subcircuit)
                else:
                    self._required_subcircuits[name] = None
        for name in names:
            if self._required_subcircuits[name] is None:
                raise ValueError("Subcircuit not found: {}", name)
        for statement in self._statements:
            if isinstance(statement, ElementStatement):
                statement.build(netlist, ground)
        return netlist

    def build(self, ground=0, parent=None):
        subcircuit = SubCircuit(str(self._name).lower(), *self._nodes, **self._params)
        subcircuit.parent = parent
        return self._build(ground, subcircuit)

    def _search_build_subcircuit(self, subcircuit_name, ground=0, netlist=None):
        # If the subcircuit is in the netlist, return the subcircuit
        subcircuit = None
        if netlist is not None:
            subcircuit = netlist._search_subcircuit(subcircuit_name)
            if subcircuit is not None:
                return subcircuit
        # If it is not, search for it in subcircuits
        if subcircuit_name in self._subcircuits:
            subcircuit = self._subcircuits[subcircuit_name]
        # Or in a possible library
        elif hasattr(self, '_library'):
            if subcircuit_name in self._library._subcircuits:
                subcircuit = self._library._subcircuits[subcircuit_name]
                self._subcircuits[subcircuit_name] = subcircuit
        # If a netlist has been received and the subcircuit exists
        if netlist is not None and subcircuit is not None:
            # Build the subcircuit
            result = self._subcircuits[subcircuit_name].build(ground, netlist)
            # Add the subcircuit to the netlist
            netlist.subcircuit(result)
            # Return the subcircuit
            return result
        # If no subcircuit has been fount, try the parent
        if self._parent is None or netlist.parent is None:
            return None
        else:
            return self._parent._search_build_subcircuit(subcircuit_name, ground, netlist.parent)


class CircuitStatement(SubCircuitStatement):
    """ This class implements a circuit definition.

    Spice syntax::

        Title ...

    """

    ##############################################

    def __init__(self, title, path):
        super(CircuitStatement, self).__init__("")

        if path is not None:
            self._path = str(path)
        else:
            self._path = os.getcwd()

        self._title = str(title)

        self._library_calls = []
        self._libraries = {}
        self._data = {}
        self._library = None

    ##############################################

    @property
    def path(self):
        """ Path of the circuit. """
        return self._path

    @property
    def title(self):
        """ Title of the circuit. """
        return self._title

    @property
    def name(self):
        """ Name of the circuit. """
        return self._title

    @property
    def libraries(self):
        """ Libraries. """
        return self._libraries

    @property
    def models(self):
        """ Models of the circuit. """
        return self._models

    @property
    def subcircuits(self):
        """ Subcircuits of the circuit. """
        return self._subcircuits

    @property
    def parameters(self):
        """ Parameters of the circuit. """
        return self._parameters

    ##############################################

    def __repr__(self):

        text = 'Circuit {}'.format(self._title) + os.linesep
        text += os.linesep.join([repr(library) for library in self._libraries]) + os.linesep
        text += os.linesep.join([repr(parameter) for parameter in self._parameters]) + os.linesep
        text += os.linesep.join([repr(model) for model in self._models]) + os.linesep
        text += os.linesep.join([repr(subcircuit) for subcircuit in self._subcircuits]) + os.linesep
        text += os.linesep.join(['  ' + repr(statement) for statement in self._statements])
        return text

    ##############################################

    def __iter__(self):

        """ Return an iterator on the statements. """

        return iter(self._libraries, self._parameters + self._models + self._subcircuits + self._statements)

    ##############################################

    def appendData(self, statement):

        """ Append a model to the statement's list. """

        self._data[statement.table] = statement

    def appendLibrary(self, statement):

        """ Append a library to the statement's list. """

        self._libraries[statement.entry] = statement

    def appendLibraryCall(self, statement):

        """ Append a library to the statement's list. """

        self._library_calls.append(statement)

    ##############################################

    def to_python(self, ground=0):

        circuit_title = self._title
        source_code = ''
        source_code += '{} = Circuit({})'.format(circuit_title) + os.linesep
        source_code += SpiceParser.netlist_to_python(circuit_title, self, ground)
        return source_code

    ##############################################

    def build(self, ground=0, library=None):
        circuit = Circuit(self._title)
        if library is not None:
            if self._library is None:
                self._library = library
            else:
                raise ValueError("Library already assigned.")
        if self._library is not None:
            circuit.include(self._library)
        return self._build(ground, circuit)


####################################################################################################

class SpiceModelWalker(ExpressionModelWalker):

    def __init__(self):
        self._functions = {"abs": Abs,
                           "agauss": AGauss,
                           "acos": ACos,
                           "acosh": ACosh,
                           "arctan": ATan,
                           "asin": ASin,
                           "asinh": ASinh,
                           "atan": ATan,
                           "atan2": ATan2,
                           "atanh": ATanh,
                           "aunif": AUnif,
                           "ceil": Ceil,
                           "cos": Cos,
                           "cosh": Cosh,
                           "db": Db,
                           "ddt": Ddt,
                           "ddx": Ddx,
                           "exp": Exp,
                           "ln": Ln,
                           "log": Ln,
                           "log10": Log10,
                           "floor": Floor,
                           "gauss": Gauss,
                           "i": I,
                           "if": If,
                           "img": Img,
                           "int": Int,
                           "limit": Limit,
                           "m": M,
                           "max": Max,
                           "min": Min,
                           "nint": NInt,
                           "ph": Ph,
                           "pow": Pow,
                           "pwr": Pow,
                           "pwrs": Pwrs,
                           "r": Re,
                           "rand": Rand,
                           "re": Re,
                           "sdt": Sdt,
                           "sgn": Sgn,
                           "sign": Sign,
                           "sin": Sin,
                           "sinh": Sinh,
                           "sqrt": Sqrt,
                           "stp": Stp,
                           "tan": Tan,
                           "tanh": Tanh,
                           "unif": Unif,
                           "uramp": URamp,
                           "v": V
                           }
        self._relational = {
            "<": LT,
            "<=": LE,
            "==": EQ,
            "!=": NE,
            ">=": GE,
            ">": GT
        }

    def walk_Circuit(self, node, data):
        if data._root is None:
            title = self.walk(node.title, data)
            title = join_lines(title)
            data._root = CircuitStatement(
                title,
                data._path
            )
            data._present = data._root
        else:
            raise ValueError('Circuit already created: {}'.format(data._path))

        self.walk(node.lines, data)
        if len(data._context) != 0:
            raise ParseError("Not closed hierarchy: {}".format(data._path))
        return data._root

    def walk_BJT(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        collector = self.walk(node.collector, data)
        base = self.walk(node.base, data)
        emitter = self.walk(node.emitter, data)
        nodes = [
            collector,
            base,
            emitter
        ]
        if node.substrate is not None:
            substrate = self.walk(node.substrate, data)
            nodes.append(substrate)
        if node.thermal is not None:
            thermal = node.thermal
            nodes.append(thermal)
        if node.area is not None:
            area = self.walk(node.area, data)
            kwargs["area"] = SpiceModelWalker._to_number(area)

        model_name = self.walk(node.model, data)
        kwargs["model"] = model_name
        data._present._required_models.add(model_name.lower())

        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)

        data._present.append(
            ElementStatement(
                BipolarJunctionTransistor,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_SubstrateNode(self, node, data):
        return node.text[1:-1]

    def walk_Capacitor(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is not None:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        value = None
        if node.value is not None:
            value = self.walk(node.value, data)
            kwargs['capacitance'] = value
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)
        if value is None:
            if 'c' in kwargs:
                value = kwargs.pop('c')
                kwargs['capacitance'] = value
            elif 'C' in kwargs:
                value = kwargs.pop('C')
                kwargs['capacitance'] = value


        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                Capacitor,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_CurrentControlledCurrentSource(self, node, data):
        device = self.walk(node.dev, data)
        if (node.controller is None and node.dev is None and
                node.gain is None):
            raise ValueError("Device {} not properly defined".format(node.dev))
        if node.controller is not None:
            controller = self.walk(node.controller, data)
            kwargs = {"I": controller}
        else:
            value = self.walk(node.gain, data)
            kwargs = {"I": I(self.walk(node.device, data).lower())*value}

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                BehavioralSource,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_CurrentControlledVoltageSource(self, node, data):
        device = self.walk(node.dev, data)
        if (node.controller is None and node.dev is None and
                node.gain is None):
            raise ValueError("Device {} not properly defined".format(node.dev))
        if node.controller is not None:
            controller = self.walk(node.controller, data)
            kwargs = {"V": controller}
        else:
            value = self.walk(node.transresistance, data)
            kwargs = {"V": I(self.walk(node.device, data).lower())*value}

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                BehavioralSource,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_CurrentSource(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        element = CurrentSource
        if node.dc_value is not None:
            kwargs['dc_value'] = self.walk(node.dc_value, data)
        if node.ac_magnitude is not None:
            kwargs['ac_magnitude'] = self.walk(node.ac_magnitude, data)
        if node.ac_phase is not None:
            kwargs['ac_phase'] = self.walk(node.ac_phase, data)
        if node.transient is not None:
            transient = self.walk(node.transient, data)
            if transient[0] == ExponentialMixin:
                element = ExponentialCurrentSource
            elif transient[0] == PatternMixin:
                element = PatternCurrentSource
            elif transient[0] == PieceWiseLinearMixin:
                element = PieceWiseLinearCurrentSource
            elif transient[0] == PulseMixin:
                element = PulseCurrentSource
            elif transient[0] == SingleFrequencyFMMixin:
                element = SingleFrequencyFMCurrentSource
            elif transient[0] == SinusoidalMixin:
                element = SinusoidalCurrentSource
            else:
                raise ParseError("Unknown transient: {}".format(transient[0]))
            kwargs.update(transient[1])

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                element,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_Diode(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is None:
            raise ValueError("The device {} has no model".format(node.dev))
        else:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        if node.area is not None:
            area = self.walk(node.area, data)
            kwargs['area'] = area

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                Diode,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_Inductor(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is not None:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        value = None
        if node.value is not None:
            value = self.walk(node.value, data)
            kwargs['inductance'] = value
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)
        if value is None:
            if 'l' in kwargs:
                value = kwargs.pop('l')
                kwargs['inductance'] = value
            elif 'L' in kwargs:
                value = kwargs.pop('L')
                kwargs['inductance'] = value

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                Inductor,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_JFET(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is None:
            raise ValueError("The device {} has no model".format(node.dev))
        else:
            model_name = self.walk(node.model, data)
            kwargs["model"] = model_name
            data._present._required_models.add(model_name.lower())
        if node.area is not None:
            area = self.walk(node.area, data)
            kwargs["area"] = area
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)

        drain = self.walk(node.drain, data)
        gate = self.walk(node.gate, data)
        source = self.walk(node.source, data)
        nodes = [
            drain,
            gate,
            source
        ]
        data._present.append(
            ElementStatement(
                JunctionFieldEffectTransistor,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_MOSFET(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is None:
            raise ValueError("The device {} has no model".format(node.dev))
        else:
            model_name = self.walk(node.model, data)
            kwargs["model"] = model_name
            data._present._required_models.add(model_name.lower())
        if node.param is not None:
            if isinstance(node.param, list):
                # The separators are not taken into account
                for parameter in node.param:
                    if isinstance(parameter, list):
                        kwargs[parameter[0]] = self.walk(parameter[2][::2], data)
                    else:
                        kwargs.update(self.walk(parameter, data))
            else:
                kwargs.update(self.walk(node.param, data))
        drain = self.walk(node.drain, data)
        gate = self.walk(node.gate, data)
        source = self.walk(node.source, data)
        bulk = self.walk(node.bulk, data)
        nodes = [
            drain,
            gate,
            source,
            bulk
        ]
        data._present.append(
            ElementStatement(
                Mosfet,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_MutualInductor(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is not None:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        inductors = self.walk(node.inductor, data)
        if len(inductors) != 2:
            raise ParseError("Presently, only two inductors are allowed.")
        inductor1 = inductors[0]
        inductor2 = inductors[1]
        coupling_factor = self.walk(node.value, data)
        kwargs["inductor1"] = inductor1
        kwargs["inductor2"] = inductor2
        kwargs["coupling_factor"] = coupling_factor

        data._present.append(
            ElementStatement(
                CoupledInductor,
                device,
                **kwargs
            )
        )

    def walk_NonLinearDependentSource(self, node, data):
        device = self.walk(node.dev, data)
        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        expr = self.walk(node.expr, data)
        kwargs = {}
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)
        if node.magnitude == "V":
            kwargs["voltage_expression"] = expr
        else:
            kwargs["current_expression"] = expr

        data._present.append(
            ElementStatement(
                BehavioralSource,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_Resistor(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is not None:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        value = None
        if node.value is not None:
            value = self.walk(node.value, data)
            kwargs['resistance'] = value
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)
        if value is None:
            if 'r' in kwargs:
                value = kwargs.pop('r')
                kwargs['resistance'] = value
            elif 'R' in kwargs:
                value = kwargs.pop('R')
                kwargs['resistance'] = value

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                Resistor,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_Subcircuit(self, node, data):
        device = self.walk(node.dev, data)
        node_node = self.walk(node.node, data)
        if node.params is not None:
            subcircuit_name = node_node[-2]
            nodes = node_node[:-2]
        else:
            subcircuit_name = node_node[-1]
            nodes = node_node[:-1]
        kwargs = {}
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
            kwargs.update(parameters)
        data._present._required_subcircuits[subcircuit_name.lower()] = None
        data._present.append(
            ElementStatement(
                SubCircuitElement,
                device,
                subcircuit_name,
                *nodes,
                **kwargs
            )
        )

    def walk_Switch(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        if node.model is not None:
            model_name = self.walk(node.model, data)
            kwargs['model'] = model_name
            data._present._required_models.add(model_name.lower())
        if node.initial_state is not None:
            kwargs['initial_state'] = node.initial_state

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        if node.control_p is not None:
            if node.control_n is not None:
                control_p = self.walk(node.control_p, data)
                control_n = self.walk(node.control_n, data)
                nodes = (
                    positive,
                    negative,
                    control_p,
                    control_n
                )
            else:
                raise ValueError("Only one control node defined")
        else:
            if node.control_n is None:
                nodes = (
                    positive,
                    negative
                )
        data._present.append(
            ElementStatement(
                VoltageControlledSwitch,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_VoltageControlledCurrentSource(self, node, data):
        device = self.walk(node.dev, data)
        if node.controller is None and node.nodes is None:
            raise ValueError("Device {} not properly defined".format(node.dev))
        if node.controller is not None:
            controller = self.walk(node.controller, data)
            kwargs = {"I": controller}
        else:
            value = self.walk(node.transconductance, data)
            nodes = self.walk(node.nodes, data)
            if len(nodes) != 2:
                raise ValueError("Device {} not properly defined".format(node.dev))
            ctrl_p = nodes[0]
            ctrl_n = nodes[1]
            kwargs = {"I": V(ctrl_p, ctrl_n) * value}

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                BehavioralSource,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_VoltageControlledVoltageSource(self, node, data):
        device = self.walk(node.dev, data)
        if node.controller is not None:
            controller = self.walk(node.controller, data)
            kwargs = {"V": controller}
        else:
            value = self.walk(node.transconductance, data)
            nodes = self.walk(node.nodes, data)
            if len(nodes) != 2:
                raise ValueError("Device {} not properly defined".format(node.dev))
            ctrl_p = nodes[0]
            ctrl_n = nodes[1]
            kwargs = {"V": V(ctrl_p, ctrl_n) * value}

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                BehavioralSource,
                device,
                *nodes,
                **kwargs
            )
        )

    def walk_VoltageSource(self, node, data):
        device = self.walk(node.dev, data)
        kwargs = {}
        element = VoltageSource
        if node.dc_value is not None:
            kwargs['dc_value'] = self.walk(node.dc_value, data)
        if node.ac_magnitude is not None:
            kwargs['ac_magnitude'] = self.walk(node.ac_magnitude, data)
        if node.ac_phase is not None:
            kwargs['ac_phase'] = self.walk(node.ac_phase, data)
        if node.transient is not None:
            transient = self.walk(node.transient, data)
            if transient[0] == ExponentialMixin:
                element = ExponentialVoltageSource
            elif transient[0] == PatternMixin:
                element = PatternVoltageSource
            elif transient[0] == PieceWiseLinearMixin:
                element = PieceWiseLinearVoltageSource
            elif transient[0] == PulseMixin:
                element = PulseVoltageSource
            elif transient[0] == SingleFrequencyFMMixin:
                element = SingleFrequencyFMVoltageSource
            elif transient[0] == SinusoidalMixin:
                element = SinusoidalVoltageSource
            else:
                raise ParseError("Unknown transient: {}".format(transient[0]))
            kwargs.update(transient[1])

        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        nodes = (
            positive,
            negative
        )
        data._present.append(
            ElementStatement(
                element,
                device,
                *nodes,
                **kwargs
            )
        )


    def walk_ControlVoltagePoly(self, node, data):
        controllers = self.walk(node.value, data)
        positive = self.walk(node.positive, data)
        negative = self.walk(node.negative, data)
        if len(positive) < controllers or len(negative) < controllers:
            raise ValueError(
                "The number of control nodes is smaller than the expected controllers: {}".format(controllers))

        ctrl_pos = positive[:controllers]
        ctrl_neg = negative[:controllers]

        values = []
        if len(positive) > controllers:
            if isinstance(positive, list):
                values_pos = positive[controllers:]
            else:
                values_pos = [positive]
            if isinstance(negative, list):
                values_neg = negative[controllers:]
            else:
                values_neg = [negative]
            values += [SpiceModelWalker._to_number(val)
                       for pair in zip(values_pos, values_neg)
                       for val in pair]
        if node.coefficient:
            coefficients = self.walk(node.coefficient, data)
            if isinstance(coefficients, list):
                values.extend(coefficients)
            else:
                values.append(coefficients)
        controllers = [V(*nodes)
                       for nodes in zip(ctrl_pos,
                                        ctrl_neg)]
        return Poly(controllers, values)

    def walk_ControlCurrentPoly(self, node, data):
        controllers = self.walk(node.value, data)
        if len(node.device) < controllers:
            raise ValueError(
                "The number of control nodes is smaller than the expected controllers: {}".format(controllers))

        ctrl_dev = [self.walk(dev, data)
                    for dev in node.device[:controllers]]

        values = []
        if controllers > len(node.device):
            values = [SpiceModelWalker._to_number(self.walk(value, data))
                      for value in node.device[controllers:]]
        if node.coefficient:
            coefficients = self.walk(node.coefficient, data)
            if isinstance(coefficients, list):
                values.extend(coefficients)
            else:
                values.append(coefficients)
        controllers = [I(dev) for dev in ctrl_dev]
        return Poly(controllers, values)

    def walk_ControlTable(self, node, data):
        return Table(self.walk(node.expr, data),
                     list(zip(self.walk(node.input, data),
                              self.walk(node.output, data))))

    def walk_ControlValue(self, node, data):
        return self.walk(node.expression, data)

    def walk_TransientSpecification(self, node, data):
        return self.walk(node.ast, data)

    def walk_TransientPulse(self, node, data):
        parameters = dict([(key, value)
                           for value, key in zip(self.walk(node.ast, data),
                                                 ("initial_value",
                                                  "pulse_value",
                                                  "delay_time",
                                                  "rise_time",
                                                  "fall_time",
                                                  "pulse_width",
                                                  "period",
                                                  "phase"))])
        return PulseMixin, parameters

    def walk_PulseArguments(self, node, data):
        v1 = self.walk(node.v1, data)
        value = []
        if node.value is not None:
            value = self.walk(node.value, data)
        if isinstance(value, list):
            return [v1] + value
        else:
            return [v1, value]

    def walk_TransientPWL(self, node, data):
        data, parameters = self.walk(node.ast, data)
        keys = list(parameters.keys())
        low_keys = [key.lower() for key in keys]
        if 'r' in low_keys:
            idx = low_keys.index('r')
            key = keys[idx]
            repeat_time = parameters.pop(key)
            parameters['repeat_time'] = repeat_time
        if 'td' in low_keys:
            idx = low_keys.index('td')
            key = keys[idx]
            time_delay = parameters.pop(key)
            parameters['time_delay'] = time_delay
        if isinstance(data, list):
            parameters.update({"values": data})
        else:
            curdir = os.path.abspath(os.curdir)
            datapath, filename = os.path.split(data)
            if curdir.endswith(datapath):
                curdir += os.sep + filename
            else:
                curdir = os.path.abspath(data)

            with open(curdir) as ifile:
                ext = os.path.splitext(curdir)[1]
                reader = csv.reader(ifile, delimiter=',' if ext.lower() == ".csv" else ' ')
                data = [(SpiceModelWalker._to_number(t),
                         SpiceModelWalker._to_number(value))
                        for t, value in reader]
            parameters.update({"values": data})
        return PieceWiseLinearMixin, parameters

    def walk_PWLArguments(self, node, data):
        t = self.walk(node.t, data)
        value = self.walk(node.value, data)
        parameters = {}
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
        return list(zip(t, value)), parameters

    def walk_PWLFileArguments(self, node, data):
        filename = self.walk(node.filename, data)
        parameters = {}
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
        return filename, parameters

    def walk_TransientSin(self, node, data):
        parameters = dict([(key, value)
                           for value, key in zip(self.walk(node.ast, data),
                                                 ("offset",
                                                  "amplitude",
                                                  "frequency",
                                                  "delay",
                                                  "damping_factor"))])
        return SinusoidalMixin, parameters

    def walk_SinArguments(self, node, data):
        v0 = self.walk(node.v0, data)
        va = self.walk(node.va, data)
        freq = self.walk(node.freq, data)
        value = []
        if node.value is not None:
            value = self.walk(node.value, data)
        if isinstance(value, list):
            return [v0, va, freq] + value
        else:
            return [v0, va, freq, value]

    def walk_TransientPat(self, node, data):
        parameters = dict([(key, value)
                           for value, key in zip(self.walk(node.ast, data),
                                                 ("high_value",
                                                  "low_value",
                                                  "delay_time",
                                                  "rise_time",
                                                  "fall_time",
                                                  "bit_period",
                                                  "bit_pattern",
                                                  "repeat"))])
        return PatternMixin, parameters

    def walk_PatArguments(self, node, data):
        vhi = self.walk(node.vhi, data)
        vlo = self.walk(node.vlo, data)
        td = self.walk(node.td, data)
        tr = self.walk(node.tr, data)
        tf = self.walk(node.tf, data)
        tsample = self.walk(node.tsample, data)
        data = self.walk(node.data, data)
        repeat = False
        if node.repeat is not None:
            repeat = (node.repeat == '1')
        return [vhi, vlo, td, tr, tf, tsample, data, repeat]

    def walk_TransientExp(self, node, data):
        parameters = dict([(key, value)
                           for value, key in zip(self.walk(node.ast, data),
                                                 ("initial_amplitude",
                                                  "amplitude",
                                                  "rise_delay_time",
                                                  "rise_time_constant",
                                                  "delay_fall_time",
                                                  "fall_time_constant"))])
        return ExponentialMixin, parameters

    def walk_ExpArguments(self, node, data):
        v1 = self.walk(node.v1, data)
        v2 = self.walk(node.v2, data)
        if node.value is not None:
            value = self.walk(node.value, data)
        if isinstance(value, list):
            return [v1, v2] + value
        else:
            return [v1, v2, value]

    def walk_TransientSFFM(self, node, data):
        parameters = dict([(key, value)
                           for value, key in zip(self.walk(node.ast, data),
                                                 ("offset",
                                                  "amplitude",
                                                  "carrier_frequency",
                                                  "modulation_index",
                                                  "signal_frequency"))])
        return SingleFrequencyFMMixin, parameters

    def walk_SFFMArguments(self, node, data):
        v0 = self.walk(node.v0, data)
        va = self.walk(node.va, data)
        if node.value is not None:
            value = self.walk(node.value, data)
        if isinstance(value, list):
            return [v0, va] + value
        else:
            return [v0, va, value]

    def walk_ACCmd(self, node, data):
        return node.text

    def walk_DataCmd(self, node, data):
        table = node.table
        names = node.name
        values = self.walk(node.value, data)
        if len(values) % len(names) != 0:
            raise ValueError("The number of elements per parameter do not match (line: {})".format(node.line))
        parameters = dict([(name, [value for value in values[idx::len(names)]])
                           for idx, name in enumerate(names)])
        data._root.appendData(
            DataStatement(
                table,
                **parameters
            )
        )

    def walk_DCCmd(self, node, data):
        return node.text

    def walk_IncludeCmd(self, node, data):
        filename = self.walk(node.filename, data)
        include = IncludeStatement(
            data._root,
            filename
        )
        # The include statement makes available all the parameters, models and
        # subcircuits in the file.
        for inc_parameters in include._contents._parameters:
            for parameters in data._present._parameters:
                for name in inc_parameters.names:
                    if name in parameters.names:
                        raise ValueError("Duplicated parameter name {} in include file: {}".format(name, filename))
            data._present._parameters.append(inc_parameters)

        for model in include._contents._models:
            if model not in data._present._models:
                data._present._models[model] = include._contents._models[model]
            else:
                raise ValueError("Duplicated model name {} in include file: {}".format(model.name, filename))
        for name, subcircuit in include._contents._subcircuits.items():
            if name not in data._present._subcircuits:
                data._present._subcircuits[name] = subcircuit
            else:
                raise ValueError("Duplicated subcircuit name {} in include file: {}".format(subcircuit.name, filename))

    def walk_ICCmd(self, node, data):
        return node.text

    def walk_ModelCmd(self, node, data):
        name = self.walk(node.name, data)
        device = node.type
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
        else:
            parameters = {}

        data._present.appendModel(
            ModelStatement(
                name,
                device,
                **parameters
            )
        )

    def walk_ModelName(self, node, data):
        return node.name.lower()

    def walk_ParamCmd(self, node, data):
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)
        else:
            parameters = {}

        data._present.appendParam(
            ParamStatement(**parameters)
        )

    def walk_LibCmd(self, node, data):
        if node.block is not None:
            self.walk(node.block, data)
        else:
            self.walk(node.call, data)

    def walk_LibBlock(self, node, data):
        entries = node.entry
        if len(entries) == 2:
            if entries[0] != entries[1]:
                raise NameError(
                    'Begin and end library entries differ: {} != {}'.format(*entries))
            entries = entries[0]
        library = LibraryStatement(entries)
        data._context.append(data._present)
        data._present = library
        self.walk(node.lines, data)
        tmp = data._context.pop()
        tmp.appendLibrary(data._present)
        data._present = tmp

    def walk_LibCall(self, node, data):
        entries = node.entry
        if len(entries) == 2:
            if entries[0] != entries[1]:
                raise NameError(
                    'Begin and end library entries differ: {} != {}'.format(*entries))
            entries = entries[0]
        filename = self.walk(node.filename, data)
        data._present.appendLibraryCall(
              LibCallStatement(filename, entries)
        )

    def walk_SimulatorCmd(self, node, data):
        return node.simulator

    def walk_SubcktCmd(self, node, data):
        name = self.walk(node.name, data)
        if isinstance(name, list) and len(name) == 2:
            if name[0] != name[1]:
                raise NameError(
                    'Begin and end library entries differ (file:{}, line:{}): {} != {}'.format(self._path, node.parseinfo.line,
                                                                                 *name))
            name = name[0]
        nodes = self.walk(node.node, data)
        parameters = None
        if node.parameters is not None:
            parameters = self.walk(node.parameters, data)

        if nodes is None:
            if parameters is None:
                subckt = SubCircuitStatement(name)
            else:
                subckt = SubCircuitStatement(name, **parameters)
        else:
            if parameters is None:
                subckt = SubCircuitStatement(name, *nodes)
            else:
                subckt = SubCircuitStatement(name, *nodes, **parameters)
        data._context.append(data._present)
        data._present = subckt
        self.walk(node.lines, data)
        tmp = data._context.pop()
        tmp.appendSubCircuit(data._present)
        data._present = tmp

    def walk_TitleCmd(self, node, data):
        if id(data._root) == id(data._present):
            data._root._title = self.walk(node.title)
        else:
            raise SyntaxError(".Title command can only be used in the root circuit.")
        return data._root

    def walk_Lines(self, node, data):
        return self.walk(node.ast, data)

    def walk_CircuitLine(self, node, data):
        return self.walk(node.ast, data)

    def walk_NetlistLines(self, node, data):
        return self.walk(node.ast, data)

    def walk_NetlistLine(self, node, data):
        return self.walk(node.ast, data)

    def walk_Parameters(self, node, data):
        result = {}
        # The separators are not taken into account
        for parameter in self.walk(node.ast, data):
            result.update(parameter)
        return result

    def walk_Parameter(self, node, data):
        value = self.walk(node.value, data)
        return {node.name.lower(): value}

    def walk_ParenthesisNodes(self, node, data):
        return self.walk(node.ast, data)

    def walk_CircuitNodes(self, node, data):
        return self.walk_list(node.ast, data)
    def walk_Comment(self, node, data):
        # TODO implement comments on devices
        return node.ast

    def walk_Separator(self, node, data):
        if node.comment is not None:
            return self.walk(node.comment, data)

    def walk_Device(self, node, data):
        # Conversion of controlled devices to the B device names
        if node.ast[0] in ("E", "F", "G", "H"):
            return "B" + node.ast
        else:
            return node.ast

    def walk_Command(self, node, data):
        return self.walk(node.ast, data)

    def walk_NetlistCmds(self, node, data):
        return self.walk(node.ast, data)

    def walk_TableFile(self, node, data):
        filename = self.walk(node.filename, data)
        return TableFile(filename)



class ParsingData:
    def __init__(self, filename):
        self._path = filename
        self._root = None
        self._present = None
        self._context = []


class SpiceParser:
    """ This class parse a Spice netlist file and build a syntax tree.

    Public Attributes:

      :attr:`circuit`

      :attr:`models`

      :attr:`subcircuits`

    """

    _logger = _module_logger.getChild('SpiceParser')

    ##############################################

    _parser = parser(whitespace='', semantics=SpiceModelBuilderSemantics())
    _walker = SpiceModelWalker()

    def __init__(self):
        pass

    @staticmethod
    def parse(path=None, source=None, library=None):
        # Fixme: empty source

        if path is not None:
            with open(str(path), 'rb') as f:
                raw_code = f.read().decode('utf-8')
        elif source is not None:
            raw_code = source
        else:
            raise ValueError("No path or source")

        try:
            model = SpiceParser._parser.parse(raw_code)
        except Exception as e:
            if path is not None:
                raise ParseError("{}: ".format(path) + str(e)) from e
            else:
                raise ParseError(str(e)) from e

        if path is None:
            path = os.getcwd()
        data = ParsingData(path)
        circuit = SpiceParser._walker.walk(model, data)
        if library is not None:
            circuit._library = library
        try:
            SpiceParser._check_models(circuit)
        except Exception as e:
            tb = sys.exc_info()[2]
            raise ParseError("{}: ".format(path) + str(e)).with_traceback(tb)

        return circuit

    @staticmethod
    def _regenerate():
        from PySpice.Spice import __file__ as spice_file
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(spice_file)))
        grammar_file = os.path.join(location, "spicegrammar.ebnf")
        with open(grammar_file, "r") as grammar_ifile:
            grammar = grammar_ifile.read()
        with open(grammar_file, "w") as grammar_ofile:
            model = compile(str(grammar))
            grammar_ofile.write(str(model))
        python_file = os.path.join(location, "SpiceGrammar.py")
        python_grammar = to_python_sourcecode(grammar)
        with open(python_file, 'w') as grammar_ofile:
            grammar_ofile.write(python_grammar)
        python_model = to_python_model(grammar)
        model_file = os.path.join(location, "SpiceModel.py")
        with open(model_file, 'w') as model_ofile:
            model_ofile.write(python_model)

    @staticmethod
    def _check_models(circuit, available_models=set()):
        p_available_models = {model.lower() for model in available_models}
        p_available_models.update([model.lower() for model in circuit._models])
        for name, subcircuit in circuit._subcircuits.items():
            SpiceParser._check_models(subcircuit, p_available_models)
        for model in circuit._required_models:
            if model not in p_available_models:
                if hasattr(circuit, "_library"):
                    if model in circuit._library._models:
                        circuit._models[model] = circuit._library._models[model]
                        p_available_models.add(model)
            if model not in p_available_models:
                raise ValueError("Model (%s) not available in (%s)" % (model, circuit.name))

    @property
    def circuit(self):
        """ Circuit statements. """
        return self._circuit

    @property
    def models(self):
        """ Models of the sub-circuit. """
        return self._circuit.models

    @property
    def subcircuits(self):
        """ Subcircuits of the sub-circuit. """
        return self._circuit.subcircuits

    @property
    def parameters(self):
        """ Subcircuits of the sub-circuit. """
        return self._circuit.params

    ##############################################

    def is_only_subcircuit(self):
        return bool(not self._circuit and self.subcircuits)

    ##############################################

    def is_only_model(self):
        return bool(not self.circuit and not self.subcircuits and self.models)

    ##############################################

    @staticmethod
    def _build_circuit(circuit, statements, ground):

        for statement in statements:
            if isinstance(statement, IncludeStatement):
                circuit.include(str(statement))

        for statement in statements:
            if isinstance(statement, ElementStatement):
                statement.build(circuit, ground)
            elif isinstance(statement, ModelStatement):
                statement.build(circuit)
            elif isinstance(statement, SubCircuitStatement):
                subcircuit = statement.build(ground)  # Fixme: ok ???
                circuit.subcircuit(subcircuit)

    ##############################################

    def build_circuit(self, ground=0):

        """Build a :class:`Circuit` instance.

        Use the *ground* parameter to specify the node which must be translated to 0 (SPICE ground node).

        """

        # circuit = Circuit(str(self._title))
        circuit = self._circuit.build(str(ground))
        return circuit

    ##############################################

    @staticmethod
    def netlist_to_python(netlist_name, statements, ground=0):

        source_code = ''
        for statement in statements:
            if isinstance(statement, ElementStatement):
                source_code += statement.to_python(netlist_name, ground)
            elif isinstance(statement, LibraryStatement):
                source_code += statement.to_python(netlist_name)
            elif isinstance(statement, ModelStatement):
                source_code += statement.to_python(netlist_name)
            elif isinstance(statement, SubCircuitStatement):
                source_code += statement.to_python(netlist_name)
            elif isinstance(statement, IncludeStatement):
                source_code += statement.to_python(netlist_name)
        return source_code

    ##############################################

    def to_python_code(self, ground=0):

        ground = str(ground)

        source_code = ''

        if self.circuit:
            source_code += "circuit = Circuit('{}')".format(self._title) + os.linesep
        source_code += self.netlist_to_python('circuit', self._statements, ground)

        return source_code
