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

from .Netlist import ElementParameterMetaClass, NPinElement
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

    def read_words(self, location_start, number_of_words):

        line_str = str(self._line)
        number_of_words_read = 0
        words = []
        while number_of_words_read < number_of_words: # and location_start < len(line_str)
            location_stop = line_str.find(' ', location_start)
            if location_stop == -1:
                location_stop = None # read until end
            word = line_str[location_start:location_stop].strip()
            if word:
                number_of_words_read += 1
                words.append(word)
            if location_stop is None: # we should stop
                if number_of_words_read != number_of_words:
                    raise NameError("Bad element line, looking for word:\n" +
                                    line_str + '\n' +
                                    ' '*location_start + '^')
            else:
                if location_start < location_stop:
                    location_start = location_stop
                else: # we have read a space
                    location_start += 1
        
        return words, location_stop

    ##############################################

    def split_words(self, location_start, until=None):

        line_str = str(self._line)
        location_stop = None
        if until is not None:
            location = line_str.find(until, location_start)
            if location != -1:
                location_stop = location
                location = line_str.rfind(' ', location_start, location_stop)
                if location != -1:
                    location_stop = location
                else:
                    raise NameError("Bad element line, missing key? " + line_str)
        
        line_str = line_str[location_start:location_stop]
        words = [x for x in line_str.split(' ') if x]
        
        return words, location_stop

    ##############################################

    def split_line(self, keyword):

        """ Split the line according to the following pattern::

            keyword parameter1 parameter2 ... key1=value1 key2=value2 ...

        Return the list of parameters and the dictionnary.
        """

        raw_parameters = str(self._line)[len(keyword):].split()
        parameters = []
        dict_parameters = {}
        for parameter in raw_parameters:
            if '=' in parameter:
                key, value = parameter.split('=')
                dict_parameters[key.strip()] = value.strip()
            else:
                parameters.append(parameter)
        return parameters, dict_parameters

    ##############################################

    def __repr__(self):

        return "{} {}".format(self.__class__.__name__, repr(self._line))

####################################################################################################

class Comment(Token):
    pass

####################################################################################################

class SubCircuit(Token):

    """ This class implements a sub-circuit definition. """

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        parameters, dict_parameters = self.split_line('.subckt')
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

class Title(Token):

    """ This class implements a title definition. """

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        parameters, dict_parameters = self.split_line('.title')
        self._title = parameters[0]

    ##############################################

    def __repr__(self):

        return "Title {}".format(self._title)

####################################################################################################

class Element(Token):

    """ This class implements an element definition. """

    _logger = _module_logger.getChild('Element')

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        line_str = str(line)
        
        self._prefix = line_str[0]
        location_start = 1 # Fixme: start_location ?
        location_stop = line_str.find(' ')
        self._name = line_str[location_start:location_stop]
        
        self._parameters = None
        self._dict_parameters = None
        
        classes = ElementParameterMetaClass.__classes__[self._prefix]
        element_class = classes[0] # Fixme: all compatible ?
        self._logger.debug(str(element_class) + '\n' + line_str)
        if issubclass(element_class, NPinElement):
            if issubclass(element_class, SubCircuitElement):
                args, location_stop = self.split_words(location_stop, until='=')
                self._nodes = args[:-1]
                self._parameters = args[-1]
            elif issubclass(element_class, BipolarJunctionTransistor):
                self._nodes, location_stop = self.read_words(location_stop, 3)
                # Fixme:
            else:
                raise NotImplementedError
        else:
            number_of_pins = element_class.number_of_pins()
            if number_of_pins:
                self._nodes, location_stop = self.read_words(location_stop, number_of_pins)
            else:
                self._nodes = []
        
        if location_stop is not None:
            # args, location_stop = self.split_words(location_stop, until='=')
            # number_of_positional_parameters = element_class.number_of_positional_parameters()
            # if len(args) == number_of_positional_parameters:
            #     self._parameters = args
            # else:
            #     template = "wrong number of positional parameters {} / {}"
            #     raise NameError(template.format(len(args), number_of_positional_parameters))
            number_of_positional_parameters = element_class.number_of_positional_parameters()
            if number_of_positional_parameters:
                self._parameters, location_stop = self.read_words(location_stop, number_of_positional_parameters)
        if location_stop is not None:
            has_optional_parameters = bool(element_class.optional_parameters)
            if has_optional_parameters:
                pass
            else: # merge
                self._parameters[-1] += line_str[location_stop:]

        # parameters, dict_parameters = self.split_line('R') # tokenizer for () ...
        # self._element_type = str(line)[0]
        # self._name, self._nodes = parameters[0], parameters[1:] # Fixme: wrong #number of parameters
        # self._parameters = parameters[2:]
        # self._dict_parameters = dict_parameters

    ##############################################

    @property
    def name(self):
        """ Name of the element """
        return self._name

    ##############################################

    def __repr__(self):

        return "Element {} {} {} {}".format(self._prefix, self._name, self._nodes, self._parameters)

####################################################################################################

class Model(Token):

    """ This class implements a model definition. """

    ##############################################

    def __init__(self, line):

        super().__init__(line)

        parameters, dict_parameters = self.split_line('.model')
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

class Line:

    """ This class implements a line in the netlist. """

    ##############################################

    def __init__(self, text, line_range):

        self._text = str(text)
        self._line_range = line_range

    ##############################################

    def __repr__(self):
        return "{} {}".format(self._line_range, self._text)

    ##############################################

    def __str__(self):
        return self._text

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
        for line in lines:
            # print repr(line)
            text = str(line)
            lower_case_text = text.lower() # !
            if text.startswith('*'):
                tokens.append(Comment(line))
            elif lower_case_text.startswith('.'):
                lower_case_text = lower_case_text[1:]
                if lower_case_text.startswith('subckt'):
                    sub_circuit = SubCircuit(line)
                    tokens.append(sub_circuit)
                elif lower_case_text.startswith('ends'):
                    sub_circuit = None
                elif lower_case_text.startswith('title'):
                    tokens.append(Title(line))
                elif lower_case_text.startswith('end'):
                    pass
                elif lower_case_text.startswith('model'):
                    model = Model(line)
                    if sub_circuit:
                        sub_circuit.append(model)
                    else:
                        tokens.append(model)
                else:
                    # options param ...
                    # .global .include .lib .param
                    # .func .csparam .temp .if
                    # { expr } are allowed in .model lines and in device lines.
                    self._logger.warn(line)
                    # pass
            else:
                element = Element(line)
                if sub_circuit:
                    sub_circuit.append(element)
                else:
                    tokens.append(element)

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

####################################################################################################
#
# End
#
####################################################################################################
