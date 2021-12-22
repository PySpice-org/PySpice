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

"""This module implements a Spice parser.

"""

####################################################################################################

__all__ = [
    'Ac',
    'Command',
    'Control',
    'Csparam',
    'Dc',
    'Distorsion',
    'DotCommand',
    'Element',
    'Else',
    'ElseIf',
    'EndControl',
    'End',
    'EndIf',
    'EndSubcircuit',
    'Fourier',
    'Function',
    'Global',
    'If',
    'Include',
    'InitialCondition',
    'Library',
    'Measure',
    'Model',
    'Netlist',
    'NodeSet',
    'Noise',
    'Op',
    'Options',
    'Param',
    'ParseError',
    'PeriodicSteadyState',
    'Plot',
    'PoleZero',
    'Print',
    'Probe',
    'Save',
    'Sensitivity',
    'SpiceSource',
    'SpiceFile',
    'SpiceLine',
    'SpiceStates',
    'Subcircuit',
    'Temperature',
    'Title',
    'Transient',
    'Width',
]

####################################################################################################

from enum import IntEnum
from pathlib import Path
from typing import Generator, Iterator, Optional
import logging
import os

from PySpice.Spice.Netlist import Node
from PySpice.Tools.StringTools import remove_multi_space
from . import Ast
from . import ElementData
from .Ast import AstNode
from .Parser import SpiceParser
from .SpiceSyntax import ElementLetters

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ParseError(NameError):
    pass

####################################################################################################

class SpiceLine:

    _logger = _module_logger.getChild('SpiceLine')

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
    def start(self) -> int:
        return self._start

    @property
    def location(self) -> slice:
        return slice(self._start, self._stop)

    @property
    def str_location(self) -> str:
        return f'[{self._start}:{self._stop}]'

    @property
    def command(self) -> str:
        return self._command

    @property
    def comment(self) -> str:
        return self._comment

    ##############################################

    @property
    def is_comment(self) -> bool:
        return not self._command

    @property
    def is_command(self) -> bool:
        return bool(self._command)

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
    def dot_command(self) -> Optional[str]:
        if not self.is_dot_command:
            return None
        if self._dot_command is None:
            i = self._command.find(' ')
            if i == -1:
                _ = self._command
            else:
                _ = self._command[:i]
            self._dot_command = _.lower()
        return self._dot_command

    # @property
    # def element_letter(self) -> str:
    #     if self.is_element:
    #         return self._command[0].upper()
    #     else:
    #         raise ValueError

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
        self._command = remove_multi_space(self._command)

    ##############################################

    def __repr__(self) -> str:
        line_number = self.str_location
        if self.is_comment:
            return f'{line_number} COMMENT{os.linesep}    {self._comment}'
        else:
            if self.is_dot_command:
                label = 'DOT COMMAND'
            else:
                label = 'ELEMENT / CONTROL COMMAND'
            return f'{line_number} {label}{os.linesep}    {self._command} ; {self._comment}'

    ##############################################

    # def right_of(self, prefix: str) -> str:
    #     return self._command[len(prefix):].strip()

####################################################################################################

class Command:

    DOT_COMMAND = None
    _dot_command_maps = {}

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.DOT_COMMAND is not None:
            cls._dot_command_maps[cls.DOT_COMMAND] = cls

    ##############################################

    @classmethod
    def get_cls(cls, line: SpiceLine, in_control: bool) -> 'Command':
        # Fixme: use AST instead ?
        if not in_control and line.is_element:
            return Element
        elif in_control or line.is_dot_command:
            try:
                return cls._dot_command_maps[line.dot_command]
            except KeyError:
                return cls
        return None

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        self._line = line
        self._ast = ast

    ##############################################

    @property
    def line(self) -> SpiceLine:
        return self._line

    @property
    def ast(self) -> AstNode:
        return self._ast

    ##############################################

    @staticmethod
    def format_parameters(parameters: dict) -> dict[str, str]:
        return {key: str(value) for key, value in parameters.items()}

    ##############################################

    @staticmethod
    def child_to_python(child: AstNode) -> str | int:
        match child:
            case Ast.Id():
                return str(child)
            case Ast.Integer():
                return int(child)
            case Ast.Number():
                if child.has_str:
                    return str(child)
                else:
                    return float(child)
            case _:
                # Fixme:
                return str(child)

    @classmethod
    def childs_to_python(cls, childs: list[AstNode]) -> list:
        return [cls.child_to_python(_) for _ in childs]

####################################################################################################

class Element(Command):

    """ This class implements an element definition.

    Spice syntax::

        [A-Z][name] ...

    """

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)

        self._letter = ast.first_letter
        if not getattr(ElementLetters, self._letter):
            raise ParseError(f"Invalid element letter in element command @{line.str_location} {self._ast.name}")
        self._name = ast.after_first_letter

        first_set_position = ast.childs.find_first_set()

        # Read nodes
        self._nodes = []
        number_of_pins = 0
        data = ElementData.elements[self._letter]
        if not data.has_variable_number_of_pins:
            number_of_pins = data.number_of_pins
        else:   # Q or X
            if first_set_position == -1:
                number_of_pins = len(ast)
            else:
                number_of_pins = first_set_position
            number_of_pins -= 1   # last is model / subcircuit name
            if self._letter == 'Q':
                last_node = ast[number_of_pins -1]
                if isinstance(last_node, Ast.Id) and str(last_node) == 'off':
                    number_of_pins -= 1
                if not (3 <= number_of_pins <= 5):
                    raise ValueError("Invalid number of nodes for {ast}")
            self._model_name = str(ast[number_of_pins])
        if number_of_pins:
            self._nodes = self.childs_to_python(ast[:number_of_pins])

        self._parameters = []
        self._dict_parameters = {}
        for child in ast[number_of_pins:]:
            match child:
                case Ast.Id():
                    self._parameters.append(str(child))
                case Ast.Integer():
                    self._parameters.append(int(child))
                # case Ast.Number():
                #     self._parameters.append(child)
                case Ast.Set():
                    self._dict_parameters[child.left_id] = child
                case _:
                    self._parameters.append(child)
                    # raise ValueError(f"Invalid item {child} in {ast}")

        # Fixme: ok ???
        if data.multi_devices:
            for element_class in data:
                if len(self._parameters) == element_class.number_of_positional_parameters:
                    break
        else:
            element_class = data.single
        self._factory = element_class

    ##############################################

    @property
    def factory(self):
        return self._factory

    @property
    def letter(self) -> str:
        return self._letter

    @property
    def name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        if hasattr(self, 'model_name'):
            return self._model_name
        else:
            return None

    subcircuit_name = model_name

    @property
    def parameters(self):
        return self._parameters

    @property
    def dict_parameters(self):
        return self._dict_parameters

    ##############################################

    def __repr__(self) -> str:
        parameters = [str(_) for _ in self._parameters]
        dict_parameters = self.format_parameters(self._dict_parameters)
        return f'Element {self._letter}[{self._name}] {self._nodes} {parameters} {dict_parameters}'

    ##############################################

    def translate_ground_node(self, ground: int) -> list[str|int]:
        nodes = []
        for node in self._nodes:
            if str(node) == str(ground):
                node = Node.SPICE_GROUND_NUMBER
            nodes.append(node)
        return nodes

####################################################################################################

class DotCommand(Command):
    pass

####################################################################################################

class Ac(DotCommand):
    DOT_COMMAND = '.ac'

####################################################################################################

class Control(DotCommand):
    DOT_COMMAND = '.control'

####################################################################################################

class Csparam(DotCommand):

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

    DOT_COMMAND = '.param'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        # Fixme:

    ##############################################

    def __repr__(self) -> str:
        return f'Csparam'

####################################################################################################

class Dc(DotCommand):
    DOT_COMMAND = '.dc'

class Distorsion(DotCommand):
    DOT_COMMAND = '.disto'

class Else(DotCommand):
    DOT_COMMAND = '.else'

class ElseIf(DotCommand):
    DOT_COMMAND = '.elseif'

####################################################################################################

class End(DotCommand):
    DOT_COMMAND = '.end'

class EndControl(DotCommand):
    DOT_COMMAND = '.endc'

class EndIf(DotCommand):
    DOT_COMMAND = '.endif'

class EndSubcircuit(DotCommand):
    DOT_COMMAND = '.ends'

####################################################################################################

class Fourier(DotCommand):
    DOT_COMMAND = '.fourier'

####################################################################################################

class Function(DotCommand):

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

    DOT_COMMAND = '.func'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        # Fixme:
        self._name = ''
        self._variables = ''
        self._expression = ''

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
        return f'Func {self._name} {self._variables} {self._expression}'

####################################################################################################

class Global(DotCommand):

    """This class implements a global command.

    Spice syntax::

        .GLOBAL nodename
        .GLOBAL nodename1 nodename2 ...

    Examples::

        .GLOBAL gnd vcc
    """

    DOT_COMMAND = '.global'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        # Fixme
        self._nodes = ()

    ##############################################

    @property
    def nodes(self):   # ->
        return iter(self._nodes)

    ##############################################

    def __repr__(self) -> str:
        return f'Global {self._nodes}'

####################################################################################################

class InitialCondition(DotCommand):
    DOT_COMMAND = '.ic'

####################################################################################################

class If(DotCommand):
    DOT_COMMAND = '.if'

####################################################################################################

class Include(DotCommand):

    """This class implements a include command.

    Spice syntax::

        .INCLUDE filename

    Examples::

        .INCLUDE /users/spice/common/bsim3-param.mod
    """

    DOT_COMMAND = '.include'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        self._path = Path(str(ast.child))

    ##############################################

    @property
    def path(self) -> Path:
        return self._path

    ##############################################

    def __repr__(self) -> str:
        return f'Include "{self._path}"'

####################################################################################################

class Library(DotCommand):

    """This class implements a library command.

    Spice syntax::

        .LIB filename libname

    Examples::

        .LIB /users/spice/common/mosfets.lib mos1
    """

    DOT_COMMAND = '.lib'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        self._path, self._libname = [str(_) for _ in ast]
        self._path = Path(self._path)

    ##############################################

    @property
    def path(self) -> Path:
        return self._path

    @property
    def libname(self) -> str:
        return self._libname

    ##############################################

    def __repr__(self) -> str:
        return f'Lib "{self._path}" {self._libname}'

####################################################################################################

class Measure(DotCommand):
    DOT_COMMAND = '.meas'

####################################################################################################

class Model(DotCommand):

    """This class implements a model command.

    Spice syntax::

        .MODEL mname type (pname1=pval1 pname2=pval2)

    Examples::

        .MODEL MOD1 npn (bf=50 is=1e-13 vbf=50)
    """

    DOT_COMMAND = '.model'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        self._name = str(ast.first_child)
        child2 = ast[1]
        if isinstance(child2, Ast.Function):
            self._type = child2.name
            parameters = child2   # .childs
        else:
            self._type = str(child2)
            parameters = ast[2:]
        self._dict_parameters = {}
        # Fixme: duplicated code
        for child in parameters:
            if isinstance(child, Ast.Set):
                self._dict_parameters[child.left_id] = child.right
            else:
                raise ParseError(f"Invalid item '{child}' in {ast}")

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def parameters(self) -> dict:
        return self._dict_parameters

    @property
    def py_parameters(self) -> dict:
        return {name:self.child_to_python(ast) for name, ast in self._dict_parameters.items()}

    ##############################################

    def __repr__(self) -> str:
        parameters = self.format_parameters(self._dict_parameters)
        return f'Model {self._name} type={self._type} {parameters}'

####################################################################################################

class NodeSet(DotCommand):
    DOT_COMMAND = '.nodeset'

class Noise(DotCommand):
    DOT_COMMAND = '.noise'

class Op(DotCommand):
    DOT_COMMAND = '.op'

class Options(DotCommand):
    DOT_COMMAND = '.options'

####################################################################################################

class Param(DotCommand):

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

    DOT_COMMAND = '.param'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        # Fixme:
        self._parameters = {}

    ##############################################

    @property
    def parameters(self) -> dict:
        return self._parameters

    ##############################################

    def __repr__(self) -> str:
        return f'Param {self._parameters}'

####################################################################################################

class Plot(DotCommand):
    DOT_COMMAND = '.plot'

class Print(DotCommand):
    DOT_COMMAND = '.print'

class Probe(DotCommand):
    DOT_COMMAND = '.probe'

class PeriodicSteadyState(DotCommand):
    DOT_COMMAND = '.pss'

class PoleZero(DotCommand):
    DOT_COMMAND = '.pz'

class Save(DotCommand):
    DOT_COMMAND = '.save'

class Sensitivity(DotCommand):
    DOT_COMMAND = '.sens'

####################################################################################################

class Netlist:

    ##############################################

    def __init__(self) -> None:
        self._items = []

    ##############################################

    def add(self, item: Command) -> None:
        self._items.append(item)

    append = add

    ##############################################

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> Iterator[Command]:
        return iter(self._items)

####################################################################################################

class Subcircuit(Netlist, DotCommand):

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

    DOT_COMMAND = '.subckt'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        DotCommand.__init__(self, line, ast)
        Netlist.__init__(self)
        # self._name = str(ast.first_child)
        self._name, *self._nodes = self.childs_to_python(ast.childs.iter_on_leaf())
        self._dict_parameters = {}
        for child in ast[len(self._nodes)+1:]:
            if isinstance(child, Ast.Set):
                self._dict_parameters[child.left_id] = child.right
            else:
                raise ParseError(f"Invalid item {child} in {ast}")

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def nodes(self) -> list[str]:
        return self._nodes

    @property
    def parameters(self) -> dict:
        return self._dict_parameters

    ##############################################

    def __repr__(self) -> str:
        parameters = self.format_parameters(self._dict_parameters)
        return f'Subckt {self._name} {self._nodes} {parameters}'

####################################################################################################

class Temperature(DotCommand):

    """This class implements a temp command.

    Sets the circuit temperature in degrees Celsius.

    Spice syntax::

        .TEMP value

    Examples::

        .TEMP 27
    """

    COMMAND = '.temp'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        self._temperature = ast.child

    ##############################################

    @property
    def float_temperature(self) -> float:
        # Fixme: could fail
        return float(self._temperature)

    ##############################################

    def __repr__(self) -> str:
        return f'Temp {self._temperature}'

####################################################################################################

class Title(DotCommand):

    """This class implements a title command."""

    DOT_COMMAND = '.title'

    ##############################################

    def __init__(self, line: SpiceLine, ast: AstNode) -> None:
        super().__init__(line, ast)
        self._title = str(ast.child)

    ##############################################

    def __str__(self) -> str:
        return self._title

    ##############################################

    def __repr__(self) -> str:
        return f'Title "{self._title}"'

####################################################################################################

class Transient(DotCommand):
    DOT_COMMAND = '.tran'

class Width(DotCommand):
    DOT_COMMAND = '.width'

####################################################################################################

class SpiceStates(IntEnum):
    DESK = 0         # -> .end
    SUBCIRCUIT = 1   # -> .subcircuit -> .ends
    IF = 2           # -> .if -> .endif
    CONTROL = 3      # -> .control -> .endc / or .end

####################################################################################################

class SpiceSource:

    _logger = _module_logger.getChild('SpiceSource')

    ##############################################

    def __init__(self, source: Optional[str]=None, title_line: bool=True) -> None:
        self._parser = SpiceParser()
        self.reset()
        if source is not None:
            self.parse_string(source, title_line)

    ##############################################

    def reset(self) -> None:
        self._lines = []
        self._title_line = None
        self._ast_lines = []
        self._obj_lines = []
        self._titles = []
        self._includes = []
        self._libs = []
        self._models = []
        self._subcircuits = []
        self._circuit = Netlist()
        self._control = []

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

    def read(self, generator: Generator[tuple[int, str], None, None], title_line: bool=True) -> None:
        """Preprocess lines. This method merges continuation lines and split command and comment.

        """
        self.reset()
        last_line = None
        last_command = None
        for line_number, line in generator:
            # print(f'>>>{line_number}///{line.rstrip()}')
            ### line = line.strip()
            # handle first line
            line_is_comment = line.startswith('*')
            if line_number == 0 and not line_is_comment and title_line:
                self._title_line = SpiceLine(line_number, line_number, None, line.strip())
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
                    raise ParseError(f"Continuation line at {line_number} doesn't follow a command line")
            # Handle comment line
            elif line_is_comment:
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

    ##############################################

    def parse(self) -> None:
        for line in self._lines:
            if line.is_comment:
                self._ast_lines.append(None)
            else:
                line.cleanup()
                self._logger.debug(os.linesep + str(line))
                try:
                    ast = self._parser.parse(line.command)
                    self._ast_lines.append(ast)
                    self._logger.debug(os.linesep + str(ast.pretty_print()))
                except NameError as e:
                    raise ParseError(str(e))

    ##############################################

    def analyse(self) -> None:
        state_stack = [SpiceStates.DESK]
        circuit = []
        subcircuit = None
        control = []

        def get_state() -> int:
            return state_stack[-1]

        def not_state(state: int) -> bool:
            return get_state() != state

        def append(obj: Command) -> None:
            match get_state():
                case SpiceStates.SUBCIRCUIT:
                    _ = subcircuit
                case SpiceStates.CONTROL:
                    _ = control
                case _:
                    _ = circuit
            _.append(obj)

        for line, ast in zip(self._lines, self._ast_lines):
            if line.is_comment:
                continue
            cls = Command.get_cls(line, get_state() == SpiceStates.CONTROL)
            obj = cls(line, ast)
            self._obj_lines.append(obj)
            self._logger.debug(os.linesep + repr(obj))
            match obj:
                case If():
                    state_stack.append(SpiceStates.IF)
                    append(obj)
                    raise NotImplementedError
                case Include():
                    self._includes.append(obj)
                case Control():
                    state_stack.append(SpiceStates.CONTROL)
                    control.append(obj)
                case End():
                    # ignore line after
                    break
                case EndControl():
                    if not_state(SpiceStates.CONTROL):
                        raise ParseError(".endc without .control")
                    state_stack.pop()
                case EndIf():
                    if not not_state(SpiceStates.IF):
                        raise ParseError(".endif without .if")
                    state_stack.pop()
                case EndSubcircuit():
                    if not_state(SpiceStates.SUBCIRCUIT):
                        raise ParseError(".ends without .subckt")
                    state_stack.pop()
                    subcircuit = None
                case Library():
                    self._includes.append(obj)
                case Model():
                    self._models.append(obj)
                    append(obj)
                case Subcircuit():
                    state_stack.append(SpiceStates.SUBCIRCUIT)
                    subcircuit = obj
                    self._subcircuits.append(obj)
                    # append(obj)
                case Title():
                    self._titles.append(obj)
                case _:
                    append(obj)
        self._circuit = circuit
        self._control = control

    ##############################################

    def _parse(self) -> None:
        self.parse()
        self.analyse()

    ##############################################

    def parse_string(self, source: str, title_line: bool=True) -> None:
        generator = enumerate(source.splitlines())
        self.read(generator, title_line)
        self._parse()

    ##############################################

    def parse_file(self, path: str | Path) -> None:
        with open(path, 'r', encoding='utf-8') as fh:
            generator = enumerate(fh.readlines())
            self.read(generator, title_line=True)
            self._parse()

    ##############################################

    def to_spice(self, comment: bool=False, line_length_max: int=None) -> str:
        """Retranslate for each line the AST in Spice syntax."""

        def split_line(line: str, prefix: str) -> str:
            if line_length_max is not None and len(line) > line_length_max:
                position = line.rfind(' ', 0, line_length_max)
                # if position == -1:
                #     position = line_length_max
                # avoid infinite loop
                if position > 0:
                    line = line[:position] + os.linesep + prefix + split_line(line[position:].strip(), prefix)
            return line

        text = ''
        for line, ast in zip(self._lines, self._ast_lines):
            if ast is not None:
                ast_str = str(ast)
                if line.comment:
                    ast_str += f' ; {line.comment}'
                if not (isinstance(ast, Ast.DotCommand) and ast.name in ('.title', '.include', '.lib')):
                    ast_str = split_line(ast_str, '+')
            elif line.comment:
                # comment = line.comment.replace(os.linesep, ' ')
                # ast_str = f'* {comment}'
                # ast_str = split_line(ast_str, '* ')
                comment = line.comment.replace(os.linesep, os.linesep + '* ')
                if line.start == 0:
                    ast_str = comment
                else:
                    ast_str = f'* {comment}'
            text += ast_str + os.linesep
        return text

    ##############################################

    @property
    def title(self) -> SpiceLine | None:
        if self._title_line is not None:
            return self._title_line.comment
        else:
            return None

    @property
    def lines(self) -> Iterator[str]:
        return iter(self._lines)

    @property
    def ast_lines(self) -> Iterator[AstNode]:
        return iter(self._ast_lines)

    @property
    def obj_lines(self) -> Iterator[Command]:
        return iter(self._obj_lines)

    @property
    def titles(self) -> Iterator[Title]:
        return iter(self._titles)

    @property
    def includes(self) -> Iterator[Include]:
        return iter(self._includes)

    @property
    def libraries(self) -> Iterator[Library]:
        return iter(self._libs)

    @property
    def models(self) -> Iterator[Model]:
        return iter(self._models)

    @property
    def subcircuits(self) -> Iterator[Subcircuit]:
        return iter(self._subcircuits)

    @property
    def circuit(self) -> Netlist:
        return iter(self._circuit)

    @property
    def control(self) -> Iterator[Command]:
        return iter(self._control)

    ##############################################

    @property
    def is_only_subcircuit(self) -> bool:
        return not self._circuit and self._subcircuits

    ##############################################

    @property
    def is_only_model(self) -> bool:
        return not self._circuit and not self._subcircuits and self._models

####################################################################################################

class SpiceFile(SpiceSource):

    ##############################################

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self.parse_file(path)
