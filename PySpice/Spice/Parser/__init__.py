####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = ["SpiceParser"]

####################################################################################################

from pathlib import Path
from enum import IntEnum   # , auto
import os

from .SpiceSyntax import ElementLetters

####################################################################################################

def n_iterator(items, strip):
    number_of_pairs = len(items) // strip
    if number_of_pairs * strip != len(items):
        raise ValueError("List is odd")
    for i in range(number_of_pairs):
        yield items[strip*i], items[strip*(i+1)-1]

def pair_iterator(items):
    return n_iterator(items, 2)

def tri_iterator(items):
    return n_iterator(items, 3)

####################################################################################################

class ParserError(NameError):
    pass

####################################################################################################

class ParserState(IntEnum):
    HEADER = 0
    COMMAND = 1

####################################################################################################

class SpiceLine:

    ##############################################

    def __init__(self, start: int, stop: int, command: str, comment: str):
        self._start = start
        self._stop = stop
        self._command = command
        self._comment = comment

    ##############################################

    @property
    def location(self) -> slice:
        return slice(self._start, self._stop)

    @property
    def str_location(self) -> str:
        return f"[{self._start}:{self._stop}]"

    @property
    def command(self):
        return self._command

    @property
    def comment(self):
        return self._comment

    ##############################################

    @property
    def is_comment(self) -> str:
        return self._comment and not self._command

    @property
    def is_command(self) -> str:
        return self._command

    @property
    def is_dot_command(self) -> bool:
        return self._command and self._command.startswith('.')

    @property
    def is_element(self) -> bool:
        return self.is_command and not self.is_dot_command

    ##############################################

    @property
    def dot_command(self) -> str:
        if not self.is_dot_command:
            raise ValueError
        i = self._command.find(' ')
        if i == -1:
            _ = self._command[1:]
        else:
            _ = self._command[1:i]
        return _.upper()

    @property
    def element_letter(self) -> str:
        if self.is_element:
            return self._command[0].upper()
        else:
            raise ValueError

    ##############################################

    def append(self, line_number, command, comment):
        self._stop = line_number
        if command:
            self._command += ' ' + command
        if comment:
            self._comment += os.linesep + comment

    ##############################################

    def cleanup(self):
        command = self._command
        self._command = ''
        last_c = None
        for c in command:
            if c == ' ' and last_c == ' ':
                continue
            self._command += c
            last_c = c

    ##############################################

    def __repr__(self) -> str:
        line_number = self.str_location
        if self.is_comment:
            return f"{line_number} COMMENT{os.linesep}{self._comment}"
        else:
            if self.is_dot_command:
                label = "DOT COMMAND"
            else:
                label = "ELEMENT"
            return f"{line_number} {label}{os.linesep}{self._command} ; {self._comment}"

    ##############################################

    def right_of(self, prefix: str) -> str:
        return self._command[len(prefix):].strip()

    ##############################################

    def slipt_right_of(self, prefix: str) -> list[str]:
        return self.right_of(prefix).split(' ')

    ##############################################

    def tokenize(self, prefix: str=None, exclude: str=None) -> list[str]:
        if prefix:
            command = self.right_of(prefix)
        else:
            command = self.command
        tokens = []
        append = False
        for c in command:
            match c:
                case '=' | '{' | '}' | "'":
                    tokens.append(c)
                    append = False
                case ' ':
                    append = False
                # case '=' | '{' | '}' | "'" | ' ':
                #     append = False
                case _:
                    if append:
                        tokens[-1] += c
                    else:
                        tokens.append(c)
                        append = True
        if exclude:
            tokens = [_ for _ in tokens if _ not in exclude]
        return tokens

####################################################################################################

class Statement:

    ##############################################

    def __init__(self, line: SpiceLine):
        self._line = line

    ##############################################

    @property
    def line(self) -> SpiceLine:
        return self._line

####################################################################################################

class Element(Statement):

    """ This class implements an element definition.

    Spice syntax::

        [A-Z][name] ...

    """

    ##############################################

    def __init__(self, line: SpiceLine):
        super().__init__(line)
        command = line.command
        self._letter = command[0].upper()
        if not getattr(ElementLetters, self._letter):
            raise ParserError(f"Invalid element letter in element command @{line.str_location} {command}")
        i = command.find(' ')
        if i >= 2:
            self._name = command[1:i]
        elif i == 1:
            self._name = ''
        else:
            raise ParserError(f"Error in element command @{line.str_location} {command}")
        self._right_part = command[i:].strip()

    ##############################################

    @property
    def letter(self) -> str:
        return self._letter

    @property
    def name(self) -> str:
        return self._name

    @property
    def right_part(self) -> str:
        return self._right_part

    ##############################################

    def __repr__(self) -> str:
        return f"Element {self._letter}[{self._name}] {self._right_part}"

####################################################################################################

class Csparam(Statement):

    """This class implements a csparam statement.

    Create a constant vector from a parameter in plot const.

    Spice syntax::

        .CSPARAM <ident> = { <expr > }

    Examples::

        .PARAM pippo=5
        .PARAM pp=6
        .CSPARAM pippp={pippo + pp}
        .PARAM p={pp}
        .CSPARAM pap='pp+p'
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        # Fixme: !!!

    ##############################################

    def __repr__(self) -> str:
        return f"Csparam"

####################################################################################################

class Func(Statement):

    """This class implements a func statement.

    This command defines a function. The syntax of the expression is the same as for a *.PARAM*.

    Spice syntax::

        .FUNC <ident> { <expr > }
        .FUNC <ident> = { <expr > }

    Examples::

        .FUNC icos(x) {cos(x) - 1}
        .FUNC f(x,y) {x*y}
        .FUNC foo(a,b) = {a + b}
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)

        command = line.command
        # Fixme: ok ???
        # Fixme: -> func
        # remove space around =
        command = command.replace(' =', '=')
        command = command.replace('= ', '=')
        left, right = command.split('{')
        self._expression = right.rstrip('}')
        self._name, variables = left.split('(')
        self._variables = variables.strip(')=').split(',')

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def variables(self) -> list[str]:
        return self._variables

    @property
    def expression(self) -> str:
        return self._expression

    ##############################################

    def __repr__(self) -> str:
        return f"Func {self._name} {self._variables} {self._expression}"

####################################################################################################

class Global(Statement):

    """This class implements a global command.

    Spice syntax::

        .GLOBAL nodename
        .GLOBAL nodename1 nodename2 ...

    Examples::

        .GLOBAL gnd vcc
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        self._nodes = line.split_right_of('.global')

    ##############################################

    @property
    def nodes(self):   # ->
        return iter(self._nodes)

    ##############################################

    def __repr__(self) -> str:
        return f'Global {self._nodes}'

####################################################################################################

class Include(Statement):

    """This class implements a include command.

    Spice syntax::

        .INCLUDE filename

    Examples::

        .INCLUDE /users/spice/common/bsim3-param.mod
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        self._path = line.right_of('.include').strip('"')

    ##############################################

    @property
    def path(self) -> str:
        return self._path

    ##############################################

    def __repr__(self) -> str:
        return f'Include {self._path}'

####################################################################################################

class Lib(Statement):

    """This class implements a library command.

    Spice syntax::

        .LIB filename libname

    Examples::

        .LIB /users/spice/common/mosfets.lib mos1
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        self._path, self._libname = line.slipt_right_of('.lib')

    ##############################################

    @property
    def path(self) -> str:
        return self._path

    @property
    def libname(self) -> str:
        return self._libname

    ##############################################

    def __repr__(self) -> str:
        return f'Lib {self._path} {self._libname}'

####################################################################################################

class Model(Statement):

    """This class implements a model command.

    Spice syntax::

        .MODEL mname type (pname1=pval1 pname2=pval2)

    Examples::

        .MODEL MOD1 npn (bf=50 is=1e-13 vbf=50)
    """

    ##############################################

    def __init__(self, line: SpiceLine):
        super().__init__(line)
        command = line.command
        # remove space around =
        command = command.replace(' =', '=')
        command = command.replace('= ', '=')
        # use space as splitter
        # () is optional
        items = command.split(' ')
        self._name = items[1]
        self._type = items[2]
        self._parameters = {}
        for _ in items[3:]:
            # cleanup for ()
            _ = _.strip('()')
            if _:
                key, value = _.split('=')
                self._parameters[key] = value

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def parameters(self) -> dict:
        return self._parameters

    ##############################################

    def __repr__(self) -> str:
        return f"Model {self._name} type={self._type} {self._parameters}"

####################################################################################################

class Param(Statement):

    """This class implements a param command.

    Spice syntax::

        .PARAM <ident> = <expr> <ident> = <expr> ...

    Examples::

        .PARAM pippo=5
        .PARAM po=6 pp=7.8 pap={AGAUSS(pippo, 1, 1.67)}
        .PARAM pippp={pippo + pp}
        .PARAM p={pp}
        .PARAM pop='pp+p'
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)

        self._parameters = {}
        tokens = self.line.tokenize(prefix='.param', exclude="={}'")
        for key, value in pair_iterator(tokens):
            self._parameters[key] = value

    ##############################################

    @property
    def parameters(self) -> dict:
        return self._parameters

    ##############################################

    def __repr__(self) -> str:
        return f"Param {self._parameters}"

####################################################################################################

class Subcircuit(Statement):

    """This class implements a subcircuit command.

    Spice syntax::

        .SUBCKT name N1 <N2 ...>
        .SUBCKT name N1 <N2 ...>  <ident>=<value> <ident>=<value> ...

    Examples::

        .SUBCKT vdivide 1 2 3
        R1 1 2 10K
        R2 2 3 5
        .ENDS

       .SUBCKT myfilter in out rval=100k cval=100nF

    Each :code:`<value>` is either a SPICE number or a brace expression :code:`{<expr>}`.
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        tokens = self.line.tokenize(prefix='.subckt', exclude="{}'")
        self._name = tokens[0]
        found = False
        for i, _ in enumerate(tokens):
            if _ == '=':
                found = True
                break
        self._parameters = {}
        if found:
            self._nodes = tokens[1:i-1]
            for key, value in tri_iterator(tokens[i-1:]):
                self._parameters[key] = value
        else:
            self._nodes = tokens[1:]

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def nodes(self) -> list[str]:
        return self._nodes

    @property
    def parameters(self) -> dict:
        return self._parameters

    ##############################################

    def __repr__(self) -> str:
        return f"Subckt {self._name} {self._nodes} {self._parameters}"

####################################################################################################

class Temp(Statement):

    """This class implements a temp command.

    Sets the circuit temperature in degrees Celsius.

    Spice syntax::

        .TEMP value

    Examples::

        .TEMP 27
    """

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        self._temperature = float(line.right_of('.temp'))

    ##############################################

    @property
    def temperature(self) -> float:
        return self._temperature

    ##############################################

    def __repr__(self) -> str:
        return f'Temp {self._temperature}'

####################################################################################################

class Title(Statement):

    """This class implements a title command."""

    ##############################################

    def __init__(self, line):
        super().__init__(line)
        self._title = line.right_of('.title')

    ##############################################

    def __str__(self) -> str:
        return self._title

    ##############################################

    def __repr__(self) -> str:
        return f'Title {self._title}'

####################################################################################################

class DotCommandHandlers:
    AC = None
    CONTROL = None
    CSPARAM = Csparam
    DC = None
    DISTO = None
    ELSE = None   # to be implemented
    ELSEIF = None   # to be implemented
    END = None
    ENDC = None
    ENDIF = None   # to be implemented
    ENDS = None    # cf. subcircuit
    FOUR = None
    FUNC = Func
    GLOBAL = Global
    IC = None
    IF = None   # to be implemented
    INCLUDE = Include
    LIB = Lib
    MEAS = None
    MODEL = Model
    NODESET = None
    NOISE = None
    OP = None
    OPTIONS = None
    PARAM = Param
    PLOT = None
    PRINT = None
    PROBE = None
    PSS = None
    PZ = None
    SAVE = None
    SENS = None
    SUBCKT = Subcircuit
    TEMP = Temp
    TF = None
    TITLE = Title
    TRAN = None
    WIDTH = None

####################################################################################################

class SpiceParser:

    ##############################################

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._parse()

    ##############################################

    @classmethod
    def _split_command_comment(cls, line):
        # Handle end-of-line comments
        command = ''
        comment = ''
        if '$' in line:
            command, comment = line.split('$')
        elif ';' in line:
            command, comment = line.split(';')
        else:
            command = line
        return command.strip(), comment.strip()

    ##############################################

    def _parse(self):
        with open(self._path, 'r') as fh:
            state = ParserState.HEADER
            self._lines = []
            last_line = None
            last_command = None
            for line_number, line in enumerate(fh.readlines()):
                # print(f'>>>{line_number}///{line.rstrip()}')
                # Skip empty line
                if not line.strip():
                    continue
                command = ''
                comment = ''
                # Handle continuation line
                if line.startswith('+'):
                    _ = line[1:].strip()
                    command, comment = self._split_command_comment(_)
                    if last_command:
                        last_command.append(line_number, command, comment)
                        continue
                    else:
                        raise ParserError(f"Continuation line in {self._path} at {line_number} doesn't follow a command line")
                # Handle comment line
                elif line.startswith('*'):
                    comment = line[1:].strip()
                else:
                    command, comment = self._split_command_comment(line)
                # print(f'>>>{line_number}///{command}///{comment}///')
                # Is continuing comment ?
                if not command and last_line and last_line.is_comment:
                    last_line.append(line_number, '', comment)
                else:
                    last_line = SpiceLine(line_number, line_number, command, comment)
                    self._lines.append(last_line)
                    if command:
                        last_command = last_line

        # print(self.header)
        for line in self._lines:
            line.cleanup()
            if line.is_element:
                element = Element(line)
                print(element)
            elif line.is_dot_command:
                handler = getattr(DotCommandHandlers, line.dot_command)
                if handler is not None:
                    dot_command = handler(line)
                    print(dot_command)
            # print(line)

    ##############################################

    @property
    def header(self) -> str:
        top = self._lines[0]
        if top.is_comment:
            return top.comment
        return ''
