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

####################################################################################################

"""This module implements a partial SPICE netlist parser.

It would be difficult to implement a full parser for Ngspice since the syntax is mainly contextual.

"""

####################################################################################################

import logging

####################################################################################################

from .Netlist import ElementParameterMetaClass, NPinElement, Circuit
from .BasicElement import SubCircuitElement, BipolarJunctionTransistor

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Token:

    """ This class implements a token, in fact a line in a Spice netlist. """

    ##############################################

    def __init__(self, line):

        self._line = line

    ##############################################

    def __repr__(self):

        return "{} {}".format(self.__class__.__name__, repr(self._line))

####################################################################################################

class Comment(Token):
    pass

####################################################################################################

class Title(Token):

    """ This class implements a title definition. """

    ##############################################

    def __init__(self, line):

        super().__init__(line)
        
        self._title = self._line.read_right_of('.title')

    ##############################################

    def __str__(self):
        return self._title

    ##############################################

    def __repr__(self):
        return "Title {}".format(self._title)

####################################################################################################

class Include(Token):

    """ This class implements a include definition. """

    ##############################################

    def __init__(self, line):

        super().__init__(line)
        
        self._include = self._line.read_right_of('.include')

    ##############################################

    def __str__(self):
        return self._include

    ##############################################

    def __repr__(self):
        return "Include {}".format(self._title)

####################################################################################################

class Model(Token):

    """ This class implements a model definition.

    Spice syntax::

        .model mname type (pname1=pval1 pname2=pval2)

    """

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        # Fixme
        parameters, dict_parameters = self._line.split_line('.model')
        self._name, self._model_type = parameters[:2]
        self._parameters = dict_parameters

    ##############################################

    @property
    def name(self):
        """ Name of the model """
        return self._name

    ##############################################

    def __repr__(self):

        return "Model {} {} {}".format(self._name, self._model_type, self._parameters)

####################################################################################################

class SubCircuit(Token):

    """ This class implements a sub-circuit definition.

    Spice syntax::

        .SUBCKT name node1 ... param1=value1 ...

    """

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        # Fixme:
        parameters, dict_parameters = self._line.split_line('.subckt')
        self._name, self._nodes = parameters[0], parameters[1:]

        self._tokens = []

    ##############################################

    @property
    def name(self):
        """ Name of the sub-circuit. """
        return self._name

    ##############################################

    def __repr__(self):

        text = "SubCircuit {} {}\n".format(self._name, self._nodes)
        text += '\n'.join(['  ' + repr(token) for token in self._tokens])
        return text

    ##############################################

    def __iter__(self):

        """ Return an iterator on the tokens. """

        return iter(self._tokens)

    ##############################################

    def append(self, token):

        """ Append a token to the token's list. """

        self._tokens .append(token)

####################################################################################################

class Element(Token):

    """ This class implements an element definition. """

    _logger = _module_logger.getChild('Element')

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        line_str = str(line)
        
        self._prefix = line_str[0]
        start_location = 1
        stop_location = line_str.find(' ')
        self._name = line_str[start_location:stop_location]
        
        self._parameters = []
        self._dict_parameters = {}
        
        classes = ElementParameterMetaClass.__classes__[self._prefix]
        element_class = classes[0] # Fixme: all compatible ?
        # self._logger.debug(str(element_class) + '\n' + line_str)
        if issubclass(element_class, NPinElement):
            if issubclass(element_class, SubCircuitElement):
                args, stop_location = self._line.split_words(stop_location, until='=')
                self._nodes = args[:-1]
                self._parameters.append(args[-1]) # model name
            elif issubclass(element_class, BipolarJunctionTransistor):
                self._nodes, stop_location = self._line.read_words(stop_location, 3)
                # Fixme:
            else:
                raise NotImplementedError
        else:
            number_of_pins = element_class.number_of_pins()
            if number_of_pins:
                self._nodes, stop_location = self._line.read_words(stop_location, number_of_pins)
            else:
                self._nodes = []
        
        if stop_location is not None:
            number_of_positional_parameters = element_class.number_of_positional_parameters()
            if number_of_positional_parameters:
                self._parameters, stop_location = self._line.read_words(stop_location, number_of_positional_parameters)
        if stop_location is not None:
            has_optional_parameters = bool(element_class.optional_parameters)
            if has_optional_parameters:
                # Fixme: will fail is space in value
                kwargs, stop_location = self._line.split_words(stop_location)
                for kwarg in kwargs:
                    try:
                        key, value = kwarg.split('=')
                        self._dict_parameters[key] = value
                    except ValueError:
                        self._logger.warn(line_str)
                        # raise NameError("Bad element line:", line_str)
            else: # merge
                self._parameters[-1] += line_str[stop_location:]

    ##############################################

    @property
    def name(self):
        """ Name of the element """
        return self._name

    ##############################################

    def __repr__(self):

        return "Element {0._prefix} {0._name} {0._nodes} {0._parameters} {0._dict_parameters}".format(self)

####################################################################################################

class Line:

    """ This class implements a line in the netlist. """

    ##############################################

    def __init__(self, text, line_range):

        text = str(text)
        for marker in ('$', ';', '//'):
            location = text.find(marker)
            if location != -1:
                break
        if location != -1:
            text = text[:location]
            comment = text[location:]
        else:
            comment = ''
        
        self._text = text
        self._comment = comment
        self._line_range = line_range

    ##############################################

    def __repr__(self):
        return "{0._line_range} {0._text}".format(self)

    ##############################################

    def __str__(self):
        return self._text

    ##############################################

    def read_right_of(self, text):

        return self._text[len(text):].strip()

    ##############################################

    def read_words(self, start_location, number_of_words):

        line_str = self._text
        number_of_words_read = 0
        words = []
        while number_of_words_read < number_of_words: # and start_location < len(line_str)
            stop_location = line_str.find(' ', start_location)
            if stop_location == -1:
                stop_location = None # read until end
            word = line_str[start_location:stop_location].strip()
            if word:
                number_of_words_read += 1
                words.append(word)
            if stop_location is None: # we should stop
                if number_of_words_read != number_of_words:
                    raise NameError("Bad element line, looking for word:\n" +
                                    line_str + '\n' +
                                    ' '*start_location + '^')
            else:
                if start_location < stop_location:
                    start_location = stop_location
                else: # we have read a space
                    start_location += 1
        
        return words, stop_location

    ##############################################

    def split_words(self, start_location, until=None):

        line_str = self._text
        stop_location = None
        if until is not None:
            location = line_str.find(until, start_location)
            if location != -1:
                stop_location = location
                location = line_str.rfind(' ', start_location, stop_location)
                if location != -1:
                    stop_location = location
                else:
                    raise NameError("Bad element line, missing key? " + line_str)
        
        line_str = line_str[start_location:stop_location]
        words = [x for x in line_str.split(' ') if x]
        
        return words, stop_location

    ##############################################

    def split_line(self, keyword):

        """ Split the line according to the following pattern::

            keyword parameter1 parameter2 ... key1=value1 key2=value2 ...

        Return the list of parameters and the dictionnary.
        """

        raw_parameters = self._text[len(keyword):].split()
        parameters = []
        dict_parameters = {}
        for parameter in raw_parameters:
            if '=' in parameter:
                key, value = parameter.split('=')
                dict_parameters[key.strip()] = value.strip()
            else:
                parameters.append(parameter)
        return parameters, dict_parameters

####################################################################################################

class SpiceParser:

    """ This class parse a Spice netlist file and build a syntax tree.

    Public Attributes:

      :attr:`circuit`

      :attr:`models`

      :attr:`subcircuits`

    """

    _logger = _module_logger.getChild('SpiceParser')

    ##############################################

    def __init__(self, path=None, source=None):

        # Fixme: empty source

        if path is not None:
            with open(str(path), 'r') as f:
                raw_lines = f.readlines()
        elif source is not None:
            raw_lines = source.split('\n') # Fixme: other os
        else:
            raise ValueError
        
        lines = self._merge_lines(raw_lines)
        self._title = None
        self._tokens = self._parse(lines)
        self._find_sections()

    ##############################################

    def _merge_lines(self, raw_lines):

        """Merge broken lines and return a new list of lines.
        
        A line starting with "+" continues the preceding line.
        """

        # Fixme: better using lines[-1] ?
        lines = []
        current_line = ''
        current_line_index = None
        for line_index, line in enumerate(raw_lines):
            if line.startswith('+'):
                current_line += ' ' + line[1:].strip()
            else:
                if current_line:
                    lines.append(Line(current_line, slice(current_line_index, line_index)))
                current_line = line.strip()
                current_line_index = line_index
        if current_line:
            lines.append(Line(current_line, slice(current_line_index, len(raw_lines))))
        return lines

    ##############################################

    def _parse(self, lines):

        """ Parse the lines and return a list of tokens. """

        tokens = []
        sub_circuit = None
        scope = tokens
        for line in lines:
            # print repr(line)
            text = str(line)
            lower_case_text = text.lower() # !
            if text.startswith('*'):
                scope.append(Comment(line))
            elif lower_case_text.startswith('.'):
                lower_case_text = lower_case_text[1:]
                if lower_case_text.startswith('subckt'):
                    sub_circuit = SubCircuit(line)
                    tokens.append(sub_circuit)
                    scope = sub_circuit
                elif lower_case_text.startswith('ends'):
                    sub_circuit = None
                    scope = tokens
                elif lower_case_text.startswith('title'):
                    self._title = Title(line)
                    scope.append(self._title)
                elif lower_case_text.startswith('end'):
                    pass
                elif lower_case_text.startswith('model'):
                    model = Model(line)
                    scope.append(model)
                elif lower_case_text.startswith('include'):
                    scope.append(Include(line))
                else:
                    # options param ...
                    # .global
                    # .lib filename libname
                    # .param
                    # .func .csparam .temp .if
                    # { expr } are allowed in .model lines and in device lines.
                    self._logger.warn(line)
            else:
                element = Element(line)
                scope.append(element)

        return tokens

    ##############################################

    def _find_sections(self):

        """ Look for model, sub-circuit and circuit definitions in the token list. """

        self.circuit = None
        self.subcircuits = []
        self.models = []
        for token in self._tokens:
            if isinstance(token, Title):
                if self.circuit is None:
                    self.circuit = token
                else:
                    raise NameError("More than one title")
            elif isinstance(token, SubCircuit):
                self.subcircuits.append(token)
            elif isinstance(token, Model):
                self.models.append(token)

    ##############################################

    def is_only_subcircuit(self):

        return bool(not self.circuit and self.subcircuits)

    ##############################################

    def is_only_model(self):

        return bool(not self.circuit and not self.subcircuits and self.models)

    ##############################################

    def build_circuit(self):

        circuit = Circuit(str(self._title))
        
        for token in self._tokens:
            if isinstance(token, Include):
                circuit.include(str(token))
        
        for token in self._tokens:
            if isinstance(token, Element):
                factory = getattr(circuit, token._prefix)
                if token._prefix != 'X':
                    args = token._nodes + token._parameters
                else: # != Spice
                    args = token._parameters + token._nodes
                kwargs = token._dict_parameters
                message = ' '.join([str(x) for x in (token._prefix, token._name, token._nodes,
                                                     token._parameters, token._dict_parameters)])
                self._logger.debug(message)
                factory(token._name, *args, **kwargs)
        
        return circuit

####################################################################################################
#
# End
#
####################################################################################################
