####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 jmgc / Fabrice Salvaire
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

####################################################################################################

"""This module implements a partial SPICE netlist parser.

See the :command:`cir2py` tool for an example of usage of the parser.

It would be difficult to implement a full parser for Ngspice since the syntax is mainly contextual.

SPICE is case insensitive.

"""

####################################################################################################

from collections import OrderedDict
import logging
import os
import regex

####################################################################################################

from .ElementParameter import FlagParameter
from .Netlist import ElementParameterMetaClass, Circuit, SubCircuit

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ParseError(NameError):
    pass

####################################################################################################

class PrefixData:

    """This class represents a device prefix."""

    ##############################################

    def __init__(self, prefix, classes):

        self.prefix = prefix
        self.classes = classes

        number_of_positionals_min = 1000
        number_of_positionals_max = 0
        has_optionals = False
        for element_class in classes:
            number_of_positionals = element_class.number_of_positional_parameters
            number_of_positionals_min = min(number_of_positionals_min, number_of_positionals)
            number_of_positionals_max = max(number_of_positionals_max, number_of_positionals)
            has_optionals = max(has_optionals, bool(element_class.optional_parameters))

        self.number_of_positionals_min = number_of_positionals_min
        self.number_of_positionals_max = number_of_positionals_max
        self.has_optionals = has_optionals

        self.multi_devices = len(classes) > 1
        self.has_variable_number_of_pins = prefix in ('Q', 'X')  # NPinElement, Q has 3 to 4 pins
        if self.has_variable_number_of_pins:
            self.number_of_pins = None
        else:
            # Q and X are single
            self.number_of_pins = classes[0].number_of_pins

        self.has_flag = False
        for element_class in classes:
            for parameter in element_class.optional_parameters.values():
                if isinstance(parameter, FlagParameter):
                    self.has_flag = True

    ##############################################

    def __len__(self):
        return len(self.classes)

    ##############################################

    def __iter__(self):
        return iter(self.classes)

    ##############################################

    @property
    def single(self):
        if not self.multi_devices:
            return self.classes[0]
        else:
            raise NameError()

####################################################################################################

_prefix_cache = {}
for prefix, classes in ElementParameterMetaClass._classes.items():
    prefix_data = PrefixData(prefix, classes)
    _prefix_cache[prefix] = prefix_data
    _prefix_cache[prefix.lower()] = prefix_data

# for prefix_data in sorted(_prefix_cache.values(), key=lambda x: len(x)):
#     print(prefix_data.prefix,
#           len(prefix_data),
#           prefix_data.number_of_positionals_min, prefix_data.number_of_positionals_max,
#           prefix_data.has_optionals)

# Single:
# B 0 True
# D 1 True
# F 2 False
# G 1 False
# H 2 False
# I 1 False
# J 1 True
# K 3 False
# M 1 True
# S 2 False
# V 1 False
# W 3 False
# Z 1 True

# Two:
# E 0 1 False
# L 1 2 True

# Three:
# C 1 2 True
# R 1 2 True

# NPinElement:
# Q 1 1 True
# X 1 1 False

####################################################################################################

class Statement:

    """This base class implements a statement, in fact a line in a Spice netlist."""

    ##############################################

    def __init__(self, line, statement=None):
        self._line = line
        if statement is not None:
            self._line.lower_case_statement(statement)

    ##############################################

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, repr(self._line))

    ##############################################

    def value_to_python(self, x):
        if x:
            if str(x)[0].isdigit():
                return str(x)
            else:
                return "'{}'".format(x)
        else:
            return ''

    ##############################################

    def values_to_python(self, values):
        return [self.value_to_python(x) for x in values]

    ##############################################

    def kwargs_to_python(self, kwargs):
        return ['{}={}'.format(key, self.value_to_python(value))
                for key, value in kwargs.items()]

    ##############################################

    def join_args(self, args):
        return ', '.join(args)

####################################################################################################

class Comment(Statement):
    pass

####################################################################################################

class Title(Statement):

    """This class implements a title definition."""

    ##############################################

    def __init__(self, line):
        super().__init__(line, statement='title')
        self._title = self._line.right_of('.title')

    ##############################################

    def __str__(self):
        return self._title

    ##############################################

    def __repr__(self):
        return 'Title {}'.format(self._title)

####################################################################################################

class Include(Statement):

    """This class implements a include definition."""

    ##############################################

    def __init__(self, line):
        super().__init__(line, statement='include')
        self._include = self._line.right_of('.include')

    ##############################################

    def __str__(self):
        return self._include

    ##############################################

    def __repr__(self):
        return 'Include {}'.format(self._include)

    ##############################################

    def to_python(self, netlist_name):
        return '{}.include({})'.format(netlist_name, self._include) + os.linesep

####################################################################################################

class Model(Statement):

    """This class implements a model definition.

    Spice syntax::

        .model mname type(pname1=pval1 pname2=pval2 ... )

    """

    ##############################################

    def __init__(self, line):
        super().__init__(line, statement='model')

        base, self._parameters = line.split_keyword('.model')
        self._name, self._model_type = base
        self._name = self._name.lower()

    ##############################################

    @property
    def name(self):
        """Name of the model"""
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

class Parameter(Statement):

    """This class implements a parameter definition.

    Spice syntax::

        .param name=expr

    """

    ##############################################

    def __init__(self, line):
        super().__init__(line, statement='param')

        text = line.right_of('.param').strip().lower()  # Fixme: lower ???
        idx = text.find('=')
        self._name = text[:idx].strip()
        self._value = text[idx + 1:].strip()

    ##############################################

    @property
    def name(self):
        """Name of the model"""
        return self._name

    ##############################################

    def __repr__(self):
        return 'Param {}={}'.format(self._name, self._value)

    ##############################################

    def to_python(self, netlist_name):
        args = self.values_to_python((self._name, self._value))
        # Fixme: linesep here ???
        return '{}.param({})'.format(netlist_name, self.join_args(args)) + os.linesep

    ##############################################

    def build(self, circuit):
        circuit.parameter(self._name, self._value)

####################################################################################################

# Review: HERE

class CircuitStatement(Statement):

    # Review: jmgc

    """This class implements a circuit definition.

    Spice syntax::

        Title ...

    """

    ##############################################

    def __init__(self, title):

        super().__init__(title, statement='title')

        # Review: Title
        title_statement = '.title '
        self._title = str(title)
        if self._title.startswith(title_statement):
            self._title = self._title[len(title_statement):]

        self._statements = []
        self._subcircuits = []
        self._models = []
        self._required_subcircuits = set()
        self._required_models = set()
        self._params = []

    ##############################################

    @property
    def title(self):
        """Title of the circuit."""
        return self._title

    @property
    def name(self):
        """Name of the circuit."""
        return self._title

    @property
    def models(self):
        """Models of the circuit."""
        return self._models

    @property
    def subcircuits(self):
        """Subcircuits of the circuit."""
        return self._subcircuits

    @property
    def params(self):
        """Parameters of the circuit."""
        return self._params

    ##############################################

    def __repr__(self):
        text = 'Circuit {}'.format(self._title) + os.linesep
        text += os.linesep.join([repr(model) for model in self._models]) + os.linesep
        text += os.linesep.join([repr(subcircuit) for subcircuit in self._subcircuits]) + os.linesep
        text += os.linesep.join(['  ' + repr(statement) for statement in self._statements])
        return text

    ##############################################

    def __iter__(self):
        """Return an iterator on the statements."""
        return iter(self._models + self._subcircuits + self._statements)

    ##############################################

    def append(self, statement):
        """Append a statement to the statement's list."""
        self._statements.append(statement)

    ##############################################

    def append_model(self, statement):
        """Append a model to the statement's list."""
        self._models.append(statement)

    ##############################################

    def append_param(self, statement):
        """Append a param to the statement's list."""
        self._params.append(statement)

    ##############################################

    def append_subcircuit(self, statement):
        """Append a subcircuit to the statement's list."""
        self._subcircuits.append(statement)

    ##############################################

    def to_python(self, ground=0):
        subcircuit_name = 'subcircuit_' + self._name
        args = self.values_to_python([subcircuit_name] + self._nodes)
        source_code = ''
        source_code += '{} = SubCircuit({})'.format(subcircuit_name, self.join_args(args)) + os.linesep
        source_code += SpiceParser.netlist_to_python(subcircuit_name, self, ground)
        return source_code

    ##############################################

    def build(self, ground=0):
        circuit = Circuit(self._title)
        for statement in self._params:
            statement.build(circuit)
        for statement in self._models:
            model = statement.build(circuit)
        for statement in self._subcircuits:
            subckt = statement.build(ground)  # Fixme: ok ???
            circuit.subcircuit(subckt)
        for statement in self._statements:
            if isinstance(statement, Element):
                statement.build(circuit, ground)
        return circuit

####################################################################################################

class SubCircuitStatement(Statement):

    """This class implements a sub-circuit definition.

    Spice syntax::

        .SUBCKT name node1 ... param1=value1 ...

    """

    ##############################################

    def __init__(self, line):

        super().__init__(line, statement='subckt')

        # Fixme
        parameters, dict_parameters = self._line.split_keyword('.subckt')
        # Review: syntax ???
        if parameters[-1].lower() == 'params:':
            parameters = parameters[:-1]
        self._name, self._nodes = parameters[0], parameters[1:]
        self._name = self._name.lower()
        self._parameters = dict_parameters

        self._statements = []
        self._subcircuits = []
        self._models = []
        self._required_subcircuits = set()
        self._required_models = set()
        self._params = []

    ##############################################

    @property
    def name(self):
        """Name of the sub-circuit."""
        return self._name

    @property
    def nodes(self):
        """Nodes of the sub-circuit."""
        return self._nodes

    @property
    def models(self):
        """Models of the sub-circuit."""
        return self._models

    @property
    def params(self):
        """Params of the sub-circuit."""
        return self._params

    @property
    def subcircuits(self):
        """Subcircuits of the sub-circuit."""
        return self._subcircuits

    ##############################################

    def __repr__(self):
        if self._parameters:
            text = 'SubCircuit {} {} Parameters: {}'.format(self._name, self._nodes, self._parameters) + os.linesep
        else:
            text = 'SubCircuit {} {}'.format(self._name, self._nodes) + os.linesep
        text += os.linesep.join([repr(model) for model in self._models]) + os.linesep
        text += os.linesep.join([repr(subcircuit) for subcircuit in self._subcircuits]) + os.linesep
        text += os.linesep.join(['  ' + repr(statement) for statement in self._statements])
        return text

    ##############################################

    def __iter__(self):
        """Return an iterator on the statements."""
        return iter(self._models + self._subcircuits + self._statements)

    ##############################################

    def append(self, statement):
        """Append a statement to the statement's list."""
        self._statements.append(statement)

    ##############################################

    def append_model(self, statement):
        """Append a model to the statement's list."""
        self._models.append(statement)

    ##############################################

    def append_param(self, statement):
        """Append a param to the statement's list."""
        self._params.append(statement)

    ##############################################

    def append_subcircuit(self, statement):
        """Append a model to the statement's list."""
        self._subcircuits.append(statement)

    ##############################################

    def to_python(self, ground=0):
        subcircuit_name = 'subcircuit_' + self._name
        args = self.values_to_python([subcircuit_name] + self._nodes)
        source_code = ''
        source_code += '{} = SubCircuit({})'.format(subcircuit_name, self.join_args(args)) + os.linesep
        source_code += SpiceParser.netlist_to_python(subcircuit_name, self, ground)
        return source_code

    ##############################################

    def build(self, ground=0, parent=None):
        subcircuit = SubCircuit(self._name, *self._nodes, **self._parameters)
        subcircuit.parent = parent
        for statement in self._params:
            statement.build(subcircuit)
        for statement in self._models:
            model = statement.build(subcircuit)
        for statement in self._subcircuits:
            subckt = statement.build(ground, parent=subcircuit)  # Fixme: ok ???
            subcircuit.subcircuit(subckt)
        for statement in self._statements:
            if isinstance(statement, Element):
                statement.build(subcircuit, ground)
        return subcircuit

####################################################################################################

class Element(Statement):

    """This class implements an element definition.

    "{ expression }" are allowed in device line.

    """

    _logger = _module_logger.getChild('Element')

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        line_str = str(line)
        # self._logger.debug(os.linesep + line_str)

        # Retrieve device prefix
        prefix = line_str[0]
        if prefix.isalpha():
            self._prefix = prefix
        else:
            raise ParseError("Not an element prefix: " + prefix)
        prefix_data = _prefix_cache[self._prefix]

        # Retrieve device name
        args, kwargs = line.split_element(prefix)
        self._name = args.pop(0)

        self._nodes = []
        self._parameters = []
        self._dict_parameters = {}

        # Read nodes
        if not prefix_data.has_variable_number_of_pins:
            number_of_pins = prefix_data.number_of_pins
            if number_of_pins:
                self._nodes = args[:number_of_pins]
                args = args[number_of_pins:]
        else:  # Q or X
            if prefix_data.prefix == 'Q':
                self._nodes = args[:3]
                args = args[3:]
                # Fixme: optional node
            else:  # X
                if args[-1].lower() == 'params:':
                    args.pop()
                self._parameters.append(args.pop())
                self._nodes = args
                args = []

        # Read positionals
        number_of_positionals = prefix_data.number_of_positionals_min
        if number_of_positionals and (len(args) > 0) and (prefix_data.prefix != 'X'):  # model is optional
            self._parameters = args[:number_of_positionals]
            args = args[number_of_positionals:]
        if prefix_data.multi_devices and (len(args) > 0):
            remaining = args
            args = []
            self._parameters.extend(remaining)

        if prefix_data.prefix in ('V', 'I') and (len(args) > 0):
            # merge remaining
            self._parameters[-1] += " " + " ".join(args)
            self._dict_parameters = kwargs

        # Read optionals
        if (prefix_data.has_optionals or (prefix_data.prefix == 'X')) and (len(kwargs) > 0):
            for key in kwargs:
                self._dict_parameters[key] = kwargs[key]

        if prefix_data.multi_devices:
            for element_class in prefix_data:
                if len(self._parameters) == element_class.number_of_positional_parameters:
                    break
        else:
            element_class = prefix_data.single
        self.factory = element_class

        # Move positionals passed as kwarg
        to_delete = []
        for parameter in element_class.positional_parameters.values():
            if parameter.key_parameter:
                idx = parameter.position
                if idx < len(self._parameters):
                    self._dict_parameters[parameter.attribute_name] = self._parameters[idx]
                    to_delete.append(idx - len(to_delete))
        for idx in to_delete:
            self._parameters.pop(idx)

        # self._logger.debug(os.linesep + self.__repr__())

    ##############################################

    @property
    def name(self):
        """Name of the element"""
        return self._name

    ##############################################

    def __repr__(self):
        return 'Element {0._prefix} {0._name} {0._nodes} {0._parameters} {0._dict_parameters}'.format(self)

    ##############################################

    def translate_ground_node(self, ground):
        nodes = []
        for node in self._nodes:
            if str(node) == str(ground):
                node = 0
            nodes.append(node)
        return nodes

    ##############################################

    def to_python(self, netlist_name, ground=0):

        nodes = self.translate_ground_node(ground)
        args = [self._name]
        if self._prefix != 'X':
            args += nodes + self._parameters
        else:  # != Spice
            args += self._parameters + nodes
        args = self.values_to_python(args)
        kwargs = self.kwargs_to_python(self._dict_parameters)
        return '{}.{}({})'.format(netlist_name, self._prefix, self.join_args(args + kwargs)) + os.linesep

    ##############################################

    def _check_params(self, elements=1):
        params = []
        for param in self._parameters:
            values = param.replace(',', ' ')
            if values[0] == '(' and values[-1] == ')':
                values = values[1: -1].split()
                if len(values) > elements:
                    raise IndexError('Incorrect number of elements for (%r): %s' % (self, param))
                params.extend(values)
            else:
                params.extend(values.split())
        self._parameters = params

    ##############################################

    def _voltage_controlled_nodes(self, poly_arg):
        result = ['v(%s,%s)' % nodes
                  for nodes in zip(self._parameters[:(2 * poly_arg):2],
                                   self._parameters[1:(2 * poly_arg):2])]
        result += self._parameters[2 * poly_arg:]
        return ' '.join(result)

    ##############################################

    def _current_controlled_nodes(self, poly_arg):
        result = ['i(%s)' % node
                  for node in self._parameters[:poly_arg]]
        result += self._parameters[poly_arg:]
        return ' '.join(result)

    ##############################################

    def _manage_controlled_sources(self, nodes):
        try:
            idx = self._nodes.index('POLY')
            if idx == 2:
                poly_arg = self._nodes[3]
                if poly_arg[0] == '(' and poly_arg[-1] == ')':
                    poly_arg = poly_arg[1:-1]
                try:
                    poly_arg = int(poly_arg)
                except TypeError as te:
                    raise TypeError('Not valid poly argument: %s' % poly_arg, te)
                self._nodes = self._nodes[:2]
                nodes = nodes[:2]
                if self._prefix in 'EG':
                    self._check_params(2)
                    values = self._voltage_controlled_nodes(poly_arg)
                    if self._prefix == 'E':
                        key = 'v'
                    else:
                        key = 'i'
                else:
                    self._check_params(1)
                    values = self._current_controlled_nodes(poly_arg)
                    if self._prefix == 'F':
                        key = 'v'
                    else:
                        key = 'i'
                poly_str = '{ POLY (%d) %s }' % (poly_arg, values)

                self._dict_parameters[key] = poly_str
                self._parameters.clear()
                self._name = self._prefix + self._name
                self._prefix = 'B'
                prefix_data = _prefix_cache[self._prefix]
                self.factory = prefix_data.single
                return nodes
            raise IndexError('Incorrect position of POLY: %r' % self)
        except ValueError:
            pass
        _correction = []
        correction = []
        for _node, node in zip(self._nodes, nodes):
            _values = _node.replace(',', ' ')
            try:
                values = node.replace(',', ' ')
            except AttributeError:
                values = str(node)
            if _values[0] == '(' and _values[-1] == ')':
                _values = _values[1: -1]
            if values[0] == '(' and values[-1] == ')':
                values = values[1: -1]
            _correction.extend(_values.split())
            correction.extend(values.split())
        self._parameters = correction[len(self._nodes):] + self._parameters
        self._nodes = _correction[:len(self._nodes)]
        parameters = self._parameters
        correction = correction[:len(self._nodes)]
        if self._prefix in 'EG':
            if len(correction) + len(parameters) == 5:
                parameters = correction[2:] + parameters
                self._nodes = _correction[:2]
                value = '{v(%s, %s) * %s}' % tuple(parameters)
                if self._prefix == 'E':
                    key = 'v'
                else:
                    key = 'i'
                self._dict_parameters[key] = value
                self._parameters.clear()
                self._name = self._prefix + self._name
                self._prefix = 'B'
                prefix_data = _prefix_cache[self._prefix]
                self.factory = prefix_data.single
        else:
            if len(correction) + len(parameters) == 4:
                parameters = correction[2:] + parameters
                self._nodes = _correction[:2]
                value = '{i(%s) * %s}' % tuple(parameters)
                if self._prefix == 'F':
                    key = 'v'
                else:
                    key = 'i'
                self._dict_parameters[key] = value
                self._parameters.clear()
                self._name = self._prefix + self._name
                self._prefix = 'B'
                prefix_data = _prefix_cache[self._prefix]
                self.factory = prefix_data.single
        return correction[:len(self._nodes)]

    ##############################################

    def build(self, circuit, ground=0):

        nodes = self.translate_ground_node(ground)
        if self._prefix != 'X':
            if self._prefix in ('EFGH'):
                nodes = self._manage_controlled_sources(nodes)
            args = nodes + self._parameters
        else:  # != Spice
            args = self._parameters + nodes
        factory = getattr(circuit, self.factory.__alias__)
        kwargs = self._dict_parameters
        message = ' '.join([str(x) for x in (self._prefix, self._name, args,
                                             self._dict_parameters)])
        self._logger.debug(message)
        return factory(self._name, *args, **kwargs)


####################################################################################################

class Line:

    """This class implements a line in the netlist."""

    _logger = _module_logger.getChild('Line')

    ##############################################

    def __init__(self, line, line_range, end_of_line_comment):

        self._end_of_line_comment = end_of_line_comment

        text, comment, self._is_comment = self._split_comment(line)

        self._text = text
        self._comment = comment
        self._line_range = line_range

    ##############################################

    def __repr__(self):
        return '{0._line_range}: {0._text} // {0._comment}'.format(self)

    ##############################################

    def __str__(self):
        return self._text

    ##############################################

    @property
    def comment(self):
        return self._comment

    @property
    def is_comment(self):
        return self._is_comment

    ##############################################

    def _split_comment(self, line):

        line = str(line)

        if line.startswith('*'):
            is_comment = True
            text = ''
            comment = line[1:].strip()
        else:
            is_comment = False
            # remove end of line comment
            location = -1
            for marker in self._end_of_line_comment:
                _location = line.find(marker)
                if _location != -1:
                    if location == -1:
                        location = _location
                    else:
                        location = min(_location, location)
            if location != -1:
                text = line[:location].strip()
                comment = line[location:].strip()
            else:
                text = line
                comment = ''

        return text, comment, is_comment

    ##############################################

    def append(self, line):

        text, comment, is_comment = self._split_comment(line)

        if text:
            if not self._text.endswith(' ') or text.startswith(' '):
                self._text += ' '
            self._text += text
        if comment:
            self._comment += ' // ' + comment

        _slice = self._line_range
        self._line_range = slice(_slice.start, _slice.stop + 1)

    ##############################################

    def lower_case_statement(self, statement):

        """Lower case the statement"""

        # statement without . prefix

        if self._text:
            lower_statement = statement.lower()
            _slice = slice(1, len(statement) + 1)
            _statement = self._text[_slice]
            if _statement.lower() == lower_statement:
                self._text = '.' + lower_statement + self._text[_slice.stop:]

    ##############################################

    def right_of(self, text):
        return self._text[len(text):].strip()

    ##############################################

    def read_words(self, start_location, number_of_words):

        """Read a fixed number of words separated by space."""

        words = []
        stop_location = None

        line_str = self._text
        number_of_words_read = 0
        while number_of_words_read < number_of_words:  # and start_location < len(line_str)
            if line_str[start_location] == '{':
                stop_location = line_str.find('}', start_location)
                if stop_location > start_location:
                    stop_location += 1
            else:
                stop_location = line_str.find(' ', start_location)
            if stop_location == -1:
                stop_location = None  # read until end
            word = line_str[start_location:stop_location].strip()
            if word:
                number_of_words_read += 1
                words.append(word)
            if stop_location is None:  # we should stop
                if number_of_words_read != number_of_words:
                    template = 'Bad element line, looking for word {}/{}:' + os.linesep
                    message = (template.format(number_of_words_read, number_of_words) +
                               line_str + os.linesep +
                               ' ' * start_location + '^')
                    self._logger.warning(message)
                    raise ParseError(message)
            else:
                if start_location < stop_location:
                    start_location = stop_location
                else:  # we have read a space
                    start_location += 1

        return words, stop_location

    ##############################################

    def split_words(self, start_location, until=None):

        stop_location = None

        line_str = self._text
        if until is not None:
            location = line_str.find(until, start_location)
            if location != -1:
                stop_location = location
                location = line_str.rfind(' ', start_location, stop_location)
                if location != -1:
                    stop_location = location
                else:
                    raise NameError('Bad element line, missing key? ' + line_str)

        line_str = line_str[start_location:stop_location]
        words = [x for x in line_str.split(' ') if x]
        result = []
        expression = 0
        begin_idx = 0
        for idx, word in enumerate(words):
            if expression == 0:
                begin_idx = idx
            expression += word.count('{') - word.count('}')
            if expression == 0:
                if begin_idx < idx:
                    result.append(' '.join(words[begin_idx:idx + 1]))
                else:
                    result.append(word)
        return result, stop_location

    ##############################################

    @staticmethod
    def get_kwarg(text):

        dict_parameters = {}

        parts = []
        for part in text.split():
            if '=' in part and part != '=':
                left, right = [x for x in part.split('=')]
                parts.append(left)
                parts.append('=')
                if right:
                    parts.append(right)
            else:
                parts.append(part)

        i = 0
        i_stop = len(parts)
        while i < i_stop:
            if i + 1 < i_stop and parts[i + 1] == '=':
                key, value = parts[i], parts[i + 2]
                dict_parameters[key] = value
                i += 3
            else:
                raise ParseError("Bad kwarg: {}".format(text))

        return dict_parameters

    ##############################################

    @staticmethod
    def _partition(text):
        parts = []
        values = text.replace(',', ' ')
        for part in values.split():
            if '=' in part and part != '=':
                left, right = [x for x in part.split('=')]
                parts.append(left)
                parts.append('=')
                if right:
                    parts.append(right)
            else:
                parts.append(part)
        return parts

    ##############################################

    @staticmethod
    def _partition_parentheses(text):
        p = regex.compile(r'\(([^\(\)]|(?R))*?\)')
        parts = []
        previous_start = 0
        for m in regex.finditer(p, text):
            parts.extend(Line._partition(text[previous_start:m.start()]))
            parts.append(m.group())
            previous_start = m.end()
        parts.extend(Line._partition(text[previous_start:]))
        return parts

    ##############################################

    @staticmethod
    def _partition_braces(text):
        p = regex.compile(r'\{([^\{\}]|(?R))*?\}')
        parts = []
        previous_start = 0
        for m in regex.finditer(p, text):
            parts.extend(Line._partition_parentheses(text[previous_start:m.start()]))
            parts.append(m.group())
            previous_start = m.end()
        parts.extend(Line._partition_parentheses(text[previous_start:]))
        return parts

    ##############################################

    @staticmethod
    def _check_parameters(parts):
        parameters = []
        dict_parameters = {}

        i = 0
        i_stop = len(parts)
        while i < i_stop:
            if i + 1 < i_stop and parts[i + 1] == '=':
                key, value = parts[i], parts[i + 2]
                dict_parameters[key] = value
                i += 3
            else:
                parameters.append(parts[i])
                i += 1

        return parameters, dict_parameters

    ##############################################

    def split_keyword(self, keyword):

        """Split the line according to the following pattern::

            keyword parameter1 parameter2 ( key1=value1 key2=value2 )

        Return the list of parameters and the dictionary.
        The parenthesis can be omitted.

        """

        text = self.right_of(keyword)

        p = regex.compile(r'\(([^\(\)]|(?R))*?\)')
        b = regex.compile(r'\{([^\{\}]|(?R))*?\}')
        parts = []

        mp = regex.search(p, text)
        mb = regex.search(b, text)
        if mb is not None:
            if mp is not None:
                if (mb.start() > mp.start()) and (mb.end() < mp.end()):
                    parts.extend(Line._partition(text[:mp.start()]))
                    parts.extend(Line._partition_braces(mp.group()[1:-1]))
                elif (mb.start() < mp.start()) and (mb.end() > mp.end()):
                    parts.extend(Line._partition_braces(text))
                else:
                    raise ValueError("Incorrect format {}".format(text))
            else:
                parts.extend(Line._partition_braces(text))
        else:
            if mp is not None:
                parts.extend(Line._partition(text[:mp.start()]))
                parts.extend(Line._partition(mp.group()[1:-1]))
            else:
                parts.extend(Line._partition(text))
        return Line._check_parameters(parts)

    ##############################################

    def split_element(self, prefix):

        """Split the line according to the following pattern::

            keyword parameter1 parameter2 ... key1=value1 key2=value2 ...

        Return the list of parameters and the dictionary.

        """

        # Fixme: cf. get_kwarg

        parameters = []
        dict_parameters = {}

        text = self.right_of(prefix)

        parts = Line._partition_braces(text)

        return Line._check_parameters(parts)

####################################################################################################

class SpiceParser:

    """This class parse a Spice netlist file and build a syntax tree.

    Public Attributes:

      :attr:`circuit`

      :attr:`models`

      :attr:`subcircuits`

    """

    _logger = _module_logger.getChild('SpiceParser')

    ##############################################

    def __init__(self, path=None, source=None, end_of_line_comment=('$', '//', ';')):

        # Fixme: empty source

        if path is not None:
            with open(str(path), 'r') as fh:
                raw_lines = fh.readlines()  # Fixme: cf. jmgc
        elif source is not None:
            raw_lines = source.split(os.linesep)
        else:
            raise ValueError

        self._end_of_line_comment = end_of_line_comment

        lines = self._merge_lines(raw_lines)
        self._title = None
        self._statements = self._parse(lines)

    ##############################################

    def _merge_lines(self, raw_lines):

        """Merge broken lines and return a new list of lines.

        A line starting with "+" continues the preceding line.

        """

        lines = []
        current_line = None
        for line_index, line_string in enumerate(raw_lines):
            if line_string.startswith('+'):
                current_line.append(line_string[1:].strip('\r\n'))
            else:
                line_string = line_string.strip(' \t\r\n')
                if line_string:
                    _slice = slice(line_index, line_index + 1)
                    line = Line(line_string, _slice, self._end_of_line_comment)
                    lines.append(line)
                    # handle case with comment before line continuation
                    if not line_string.startswith('*'):
                        current_line = line

        return lines

    ##############################################

    @staticmethod
    def _check_models(circuit, available_models=set()):
        p_available_models = available_models.copy()
        p_available_models.update([model.name for model in circuit._models])
        for subcircuit in circuit._subcircuits:
            SpiceParser._check_models(subcircuit, p_available_models)
        for model in circuit._required_models:
            if model not in p_available_models:
                raise ValueError("model (%s) not available in (%s)" % (model, circuit.name))

    ##############################################

    @staticmethod
    def _sort_subcircuits(circuit, available_subcircuits=set()):
        p_available_subcircuits = available_subcircuits.copy()
        names = [subcircuit.name for subcircuit in circuit._subcircuits]
        p_available_subcircuits.update(names)
        dependencies = dict()
        for subcircuit in circuit._subcircuits:
            required = SpiceParser._sort_subcircuits(subcircuit, p_available_subcircuits)
            dependencies[subcircuit] = required
        for subcircuit in circuit._required_subcircuits:
            if subcircuit not in p_available_subcircuits:
                raise ValueError("subcircuit (%s) not available in (%s)" % (subcircuit, circuit.name))
        items = sorted(dependencies.items(), key=lambda item: len(item[1]))
        result = list()
        result_names = list()
        previous = len(items) + 1
        while 0 < len(items) < previous:
            previous = len(items)
            remove = list()
            for item in items:
                subckt, depends = item
                for name in depends:
                    if name not in result_names:
                        break
                else:
                    result.append(subckt)
                    result_names.append(subckt.name)
                    remove.append(item)
            for item in remove:
                items.remove(item)
        if len(items) > 0:
            raise ValueError("Crossed dependencies (%s)" % [(key.name, value) for key, value in items])
        circuit._subcircuits = result
        return circuit._required_subcircuits - set(names)

    ##############################################

    def _parse(self, lines):

        """Parse the lines and return a list of statements."""

        # The first line in the input file must be the title, which is the only comment line that does
        # not need any special character in the first place.
        #
        # The last line must be .end

        if len(lines) <= 1:
            raise NameError('Netlist is empty')
        # if lines[-1] != '.end':
        #     raise NameError('".end" is expected at the end of the netlist')

        circuit = CircuitStatement(lines[0])
        stack = []
        scope = circuit
        for line in lines[1:]:
            # print('>', repr(line))
            text = str(line)
            lower_case_text = text.lower()  # !
            if line.is_comment:
                scope.append(Comment(line))
            elif lower_case_text.startswith('.'):
                lower_case_text = lower_case_text[1:]
                if lower_case_text.startswith('subckt'):
                    stack.append(scope)
                    scope = SubCircuitStatement(line)
                elif lower_case_text.startswith('ends'):
                    parent = stack.pop()
                    parent.append_subcircuit(scope)
                    scope = parent
                elif lower_case_text.startswith('title'):
                    # override fist line
                    self._title = Title(line)
                    scope.append(self._title)
                elif lower_case_text.startswith('end'):
                    pass
                elif lower_case_text.startswith('model'):
                    model = Model(line)
                    scope.append_model(model)
                elif lower_case_text.startswith('include'):
                    include = Include(line)
                    scope.append(include)
                elif lower_case_text.startswith('param'):
                    param = Parameter(line)
                    scope.append_param(param)
                else:
                    # options param ...
                    # .global
                    # .lib filename libname
                    # .func .csparam .temp .if
                    # { expr } are allowed in .model lines and in device lines.
                    self._logger.warn('Parser ignored: {}'.format(line))
            else:
                try:
                    element = Element(line)
                    scope.append(element)
                    if hasattr(element, '_prefix') and (element._prefix == "X"):
                        name = element._parameters[0].lower()
                        scope._required_subcircuits.add(name)
                    elif hasattr(element, '_dict_parameters') and 'model' in element._dict_parameters:
                        name = element._dict_parameters['model'].lower()
                        scope._required_models.add(name)
                except ParseError:
                    pass
        SpiceParser._check_models(circuit)
        SpiceParser._sort_subcircuits(circuit)
        return circuit

    ##############################################

    @property
    def circuit(self):
        """Circuit statements."""
        return self._statements

    @property
    def models(self):
        """Models of the sub-circuit."""
        return self._statements.models

    @property
    def subcircuits(self):
        """Subcircuits of the sub-circuit."""
        return self._statements.subcircuits

    ##############################################

    def is_only_subcircuit(self):
        return bool(not self.circuit and self.subcircuits)

    ##############################################

    def is_only_model(self):
        return bool(not self.circuit and not self.subcircuits and self.models)

    ##############################################

    @staticmethod
    def _build_circuit(circuit, statements, ground):

        for statement in statements:
            if isinstance(statement, Include):
                circuit.include(str(statement))

        for statement in statements:
            if isinstance(statement, Element):
                statement.build(circuit, ground)
            elif isinstance(statement, Model):
                statement.build(circuit)
            elif isinstance(statement, SubCircuit):
                subcircuit = statement.build(ground)  # Fixme: ok ???
                circuit.subcircuit(subcircuit)

    ##############################################

    def build_circuit(self, ground=0):
        """Build a :class:`Circuit` instance.

        Use the *ground* parameter to specify the node which must be translated to 0 (SPICE ground node).

        """
        # circuit = Circuit(str(self._title))
        circuit = self.circuit.build(str(ground))
        return circuit

    ##############################################

    @staticmethod
    def netlist_to_python(netlist_name, statements, ground=0):

        source_code = ''
        for statement in statements:
            if isinstance(statement, Element):
                source_code += statement.to_python(netlist_name, ground)
            elif isinstance(statement, Include):
                pass
            elif isinstance(statement, Model):
                source_code += statement.to_python(netlist_name)
            elif isinstance(statement, SubCircuitStatement):
                source_code += statement.to_python(netlist_name)
            elif isinstance(statement, Include):
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
