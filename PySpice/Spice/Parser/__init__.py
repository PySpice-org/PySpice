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

__all__ = ["SpiceCode", "SpiceFile"]

####################################################################################################

from pathlib import Path
from typing import Generator
import os

from .SpiceSyntax import ElementLetters
from .Parser import SpiceParser

####################################################################################################

class ParserError(NameError):
    pass

####################################################################################################

class SpiceLine:

    ##############################################

    def __init__(self, start: int, stop: int, command: str, comment: str) -> None:
        self._start = start
        self._stop = stop
        self._command = command
        self._comment = comment
        self._is_dot_command = None
        self._is_element = None
        self._dot_command = None

    ##############################################

    @property
    def location(self) -> slice:
        return slice(self._start, self._stop)

    @property
    def str_location(self) -> str:
        return f"[{self._start}:{self._stop}]"

    @property
    def command(self) -> str:
        return self._command

    @property
    def comment(self) -> str:
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
        if self._is_dot_command is None:
            self._is_dot_command = self._command and self._command.startswith('.')
        return self._is_dot_command

    @property
    def is_element(self) -> bool:
        if self._is_element is None:
            self._is_element = self.is_command and not self.is_dot_command
        return self._is_element

    ##############################################

    @property
    def dot_command(self) -> str:
        if not self.is_dot_command:
            return None
        if self._dot_command is None:
            i = self._command.find(' ')
            if i == -1:
                _ = self._command[1:]
            else:
                _ = self._command[1:i]
            self._dot_command = _.lower()
        return self._dot_command

    @property
    def element_letter(self) -> str:
        if self.is_element:
            return self._command[0].upper()
        else:
            raise ValueError

    ##############################################

    def append(self, line_number: int, command: str | None, comment: str | None) -> None:
        self._stop = line_number
        if command:
            self._command += ' ' + command
        if comment:
            self._comment += os.linesep + comment

    ##############################################

    def cleanup(self) -> None:
        """Remove multi-space"""
        # Fixme: tab ???
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

####################################################################################################

class Statement:

    DOT_COMMAND = None

    ##############################################

    def __init__(self, line: SpiceLine, ast: tuple=None) -> None:
        self._line = line
        self._ast = ast

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

    def __init__(self, line: SpiceLine) -> None:
        super().__init__(line)
        command = line.command
        self._letter = command[0].upper()
        if not getattr(ElementLetters, self._letter):
            raise ParserError(f"Invalid element letter in element command @{line.str_location} {command}")

    ##############################################

    @property
    def letter(self) -> str:
        return self._letter

    @property
    def name(self) -> str:
        return self._name

    ##############################################

    def __repr__(self) -> str:
        return f"Element {self._letter}[{self._name}]"

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
        # self._nodes =

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
        # Fixme: space in filename
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

    COMMAND = '.temp'

    ##############################################

    def __init__(self, line):
        super().__init__(line)
         # Fixme:
        self._temperature = None

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

class SpiceCode:

    ##############################################

    def __init__(self) -> None:
        self._parser = SpiceParser()
        self._lines = []
        self._title_line = None

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

    def parse(self, generator: Generator[tuple[int, str], None, None], title_line: bool=True) -> None:
        self._lines = []
        self._title_line = None
        last_line = None
        last_command = None
        for line_number, line in generator:
            # print(f'>>>{line_number}///{line.rstrip()}')
            # handle first line
            if line_number == 0 and title_line:
                self._title_line = SpiceLine(line_number, line_number, None, line)
                self._lines.append(self._title_line)
                continue
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
                    raise ParserError(f"Continuation line at {line_number} doesn't follow a command line")
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
        # Fixme: first line should be the title line
        for line in self._lines:
            line.cleanup()
            if line.is_element or line.is_dot_command:
                print()
                print('='*100)
                print('>>>', line)
                print()
                ast = None
                dot_command = line.dot_command
                if dot_command is not None:
                    match dot_command:
                       # Fixme: use parser ?
                       case 'include':
                           ast = [line.right_of('.include').strip('"')]
                       case 'lib':
                           # Fixme: how ngspice handle space in filename ?
                           _ = line.right_of('.lib')
                           i = _.rfind(' ')
                           ast = [_[:i].rstrip(), _[i+1:]]
                       case 'title':
                           # Not handled by parser by commodity
                           ast = [line.right_of('.title')]
                if ast is None:
                    ast = self._parser.parse(line.command)
                    print(ast)
            # if line.is_element:
            #     element = Element(line)
            #     print(element)
            # elif line.is_dot_command:
            #     handler = getattr(DotCommandHandlers, line.dot_command)
            #     if handler is not None:
            #         dot_command = handler(line)
            #         print(dot_command)
            # print(line)

    ##############################################

    def parse_string(self, code: str, title_line: bool=True) -> None:
        generator = enumerate(code.splitlines())
        self.parse(generator, title_line)

    ##############################################

    def parse_file(self, path: str | Path) -> None:
        with open(path, 'r', encoding='utf-8') as fh:
            generator = enumerate(fh.readlines())
            self.parse(generator, title_line=True)

    ##############################################

    @property
    def title(self) -> str:
        return self._title_line

####################################################################################################

class SpiceFile(SpiceCode):

    ##############################################

    def __init__(self, path: str | Path):
        super().__init__()
        self._path = Path(path)
        self.parse_file(path)
