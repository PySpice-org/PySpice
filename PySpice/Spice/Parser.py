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

class Token(object):

    """ This class implements a token, in fact a line in a Spice netlist. """

    ##############################################

    def __init__(self, line):

        self._line = line

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

        super(SubCircuit, self).__init__(line)

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

        super(Title, self).__init__(line)

        parameters, dict_parameters = self.split_line('.title')
        self._title = parameters[0]

    ##############################################

    def __repr__(self):

        return "Title {}".format(self._title)

####################################################################################################

class Element(Token):

    """ This class implements an element definition. """

    ##############################################

    def __init__(self, line):

        super(Element, self).__init__(line)

        parameters, dict_parameters = self.split_line('R')
        self._element_type = str(line)[0]
        self._name, self._nodes = parameters[0], parameters[1:]
        self._parameters = parameters[2:]
        self._dict_parameters = dict_parameters

    ##############################################

    @property
    def name(self):
        """ Name of the element """
        return self._name

    ##############################################

    def __repr__(self):

        return "Element {} {} {} {}".format(self._element_type, self._name, self._nodes, self._parameters)

####################################################################################################

class Model(Token):

    """ This class implements a model definition. """

    ##############################################

    def __init__(self, line):

        super(Model, self).__init__(line)

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

class Line(object):

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

class SpiceParser(object):

    """ This class parse a Spice netlist file and build a syntax tree.

    Public Attributes:

      :attr:`circuit`

      :attr:`models`

      :attr:`subcircuits`

    """

    ##############################################

    def __init__(self, path):

        with open(str(path), 'r') as f:
            raw_lines = f.readlines()
            
        lines = self._merge_lines(raw_lines)
        self._tokens = self._parse(lines)
        self._find_sections()

    ##############################################

    def _merge_lines(self, raw_lines):

        """ Merge broken lines and return a new list of lines. """

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
            lower_case_text = text.lower()
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
                    pass
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
