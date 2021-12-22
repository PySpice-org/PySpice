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

"""This module implements an AST for Spice syntax.
"""

# Fixme: duplicate code

####################################################################################################

__all__ = [
    'Addition',
    'And',
    'AstNode',
    'BinaryOperator',
    'BraceGroup',
    'BracketGroup',
    'Branch',
    'CommaList',
    'Command',
    'Division',
    'DotCommand',
    'Equal',
    'Function',
    'Greater',
    'GreaterEqual',
    'Group',
    'Id',
    'If',
    'InnerParameter',
    'Integer',
    'IntegerDivision',
    'InvertedInput',
    'Less',
    'LessEqual',
    'List',
    'Modulo',
    'Multiplication',
    'Negation',
    'NotEqual',
    'Not',
    'Number',
    'Operator',
    'Or',
    'Set',
    'ParenthesisGroup',
    'PortModifierFunction',
    'PortModifierVector',
    'PortTypeModifier',
    'Power',
    'QuoteGroup',
    'SpaceList',
    'Subtraction',
    'Text',
    'Tuple',
    'UnaryOperator',
]

####################################################################################################

import os

from typing import Optional, Iterator

####################################################################################################

class AstNode:

    ##############################################

    def indentation(self, level: int=0) -> str:
        return ' '*4*level

    ##############################################

    def pretty_print_class(self, level: int=0, linesep: bool=True) -> str:
        _ = self.indentation(level) + self.__class__.__name__
        if linesep:
            _ += os.linesep
        return _

    ##############################################

    @property
    def is_node(self) -> bool:
        return True

    @property
    def is_leaf(self) -> bool:
        return False

    ##############################################

    def __iter__(self) -> Iterator['AstNode']:
        raise NotImplementedError

####################################################################################################

class AstLeaf(AstNode):

    ##############################################

    @property
    def is_node(self) -> bool:
        return False

    @property
    def is_leaf(self) -> bool:
        return True

####################################################################################################
####################################################################################################

class Integer(AstLeaf):

    ##############################################

    def __init__(self, value: int | float) -> None:
        self._value = value

    ##############################################

    def __int__(self) -> int:
        return self._value

    def __float__(self) -> float:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._value}'

    ##############################################

    def negate(self) -> 'Number':
        return Number(-self._value)

####################################################################################################

class Number(AstLeaf):

    ##############################################

    def __init__(self, value: int | float, unit: Optional[str]=None, extra_unit: Optional[str]=None) -> None:
        self._value = value
        self._unit = unit
        self._extra_unit = extra_unit
        # self._is_interger = isinstance(value, int) and not unit and not extra_unit

    ##############################################

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self._unit

    @property
    def extra_unit(self):
        return self._extra_unit

    ##############################################

    def __float__(self) -> float:
        return float(self._value)

    ##############################################

    def __str__(self) -> str:
        _ = str(self._value)
        if self._unit is not None:
            _ += str(self._unit)
        if self._extra_unit is not None:
            _ += str(self._extra_unit)
        return _

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._value} {self._unit} {self._extra_unit}'

    ##############################################

    def negate(self) -> 'Number':
        self._value = - self._value
        return self

####################################################################################################

class Id(AstLeaf):

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    def __str__(self) -> str:
        return self._name

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._name}'

####################################################################################################

class Text(AstLeaf):

    ##############################################

    def __init__(self, text: str) -> None:
        self._text = text

    ##############################################

    def __str__(self) -> str:
        return self._text

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._text}'

####################################################################################################

class PortTypeModifier(AstLeaf):

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    ##############################################

    def __str__(self) -> str:
        return self._name

    # def pretty_print(self, level: int=0) -> str:
    #     return self.pretty_print_class(level, False) + f' {self._name}'

####################################################################################################

class Branch(AstLeaf):

    ##############################################

    def __init__(self, name: str) -> None:
        # Fixme: source
        self._name = name

    ##############################################

    def __str__(self) -> str:
        return f'{self._name}#branch'

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._name}'

####################################################################################################

class InnerParameter(AstLeaf):

    """
    Format::

        @device_identifier.subcircuit_name.<subcircuit_name_nn>
        +.device_name[parameter]
    """

    ##############################################

    def __init__(self, element_path: str, parameter_name: str) -> None:
        self._element_path = element_path
        self._parameter_name = parameter_name

    ##############################################

    def __str__(self) -> str:
        return f'@{self._element_path}[self._parameter_name]'

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f' {self._element_path} {self._parameter_name}'

####################################################################################################
####################################################################################################

class InvertedInput(AstNode):

    ##############################################

    def __init__(self, child: str) -> None:
        self._child = child

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        yield self._child
        # return iter((self._child,))

    ##############################################

    def __str__(self) -> str:
        return f'!{self._child}'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._child.pretty_print(level +1)
        return txt

####################################################################################################

class Operator(AstNode):

    NUMBER_OF_OPERANDS = None
    OPERATOR = None

    _unary_operator_map = {}
    _binary_operator_map = {}

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.OPERATOR is not None:
            if issubclass(cls, BinaryOperator):
                d = cls._binary_operator_map
            elif issubclass(cls, UnaryOperator):
                d = cls._unary_operator_map
            d[cls.OPERATOR] = cls

    ##############################################

    @classmethod
    def get_unary(cls, operator: str):   # -> UnaryOperator:
        return cls._unary_operator_map[operator]

    ##############################################

    @classmethod
    def get_binary(cls, operator: str):   # -> BinaryOperator:
        return cls._binary_operator_map[operator]

    ##############################################

    def __init__(self, *args: AstNode) -> None:
        if (self.NUMBER_OF_OPERANDS is not None
            and len(args) != self.NUMBER_OF_OPERANDS):
            raise ValueError('Wrong number of operands')
        self._childs = args

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        return iter(self._childs)

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        indentation = self.indentation(level)
        txt = indentation + self.OPERATOR + os.linesep
        for operand in self:
            txt += operand.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class UnaryOperator(Operator):

    NUMBER_OF_OPERANDS = 1

    ##############################################

    # def __init__(self, operand1):
    #     super().__init__((operand1,))

    ##############################################

    @property
    def operand(self) -> AstNode:
        return self._childs[0]

    @property
    def operand1(self) -> AstNode:
        return self._childs[0]

    ##############################################

    def __str__(self) -> str:
        return f'{self.OPERATOR} {self.operand}'

    # def pretty_print(self, level: int=0) -> str:
    #     # return ' '.join((self.OPERATOR, str(self.operand1)))
    #     indentation = self.indentation(level)
    #     return indentation + {self.OPERATOR} + ' ' + self.operand1.pretty_print()

####################################################################################################

class BinaryOperator(UnaryOperator):

    NUMBER_OF_OPERANDS = 2

    ##############################################

    # def __init__(self, operand1, operand2):
    #     super().__init__((operand1, operand2))

    ##############################################

    @property
    def operand2(self) -> AstNode:
        return self._childs[1]

    ##############################################

    def __str__(self) -> str:
        return f'{self.operand1} {self.OPERATOR} {self.operand2}'

    # def pretty_print(self, level: int=0) -> str:
    # return ' '.join((str(self.operand1), self.OPERATOR, str(self.operand2)))
    # return f'{self.OPERATOR} {self.operand1} {self.operand2}'

####################################################################################################

# class TernaryOperator(Operator):
#     NUMBER_OF_OPERANDS = 3

####################################################################################################

class Negation(UnaryOperator):
    # fixme: name
    OPERATOR = '-'
    PRECEDENCE = 1

class Not(UnaryOperator):
    OPERATOR = '!'
    PRECEDENCE = 1

####################################################################################################

class Power(BinaryOperator):
    OPERATOR = '**'
    PRECEDENCE = 2

BinaryOperator._binary_operator_map['^'] = Power

class Multiplication(BinaryOperator):
    OPERATOR = '*'
    PRECEDENCE = 3

class Division(BinaryOperator):
    OPERATOR = '/'
    PRECEDENCE = 3

class Modulo(BinaryOperator):
    OPERATOR = '%'
    PRECEDENCE = 3

class IntegerDivision(BinaryOperator):
    OPERATOR = '\\'
    PRECEDENCE = 3

class Addition(BinaryOperator):
    OPERATOR = '+'
    PRECEDENCE = 4

class Subtraction(BinaryOperator):
    OPERATOR = '-'
    PRECEDENCE = 4

####################################################################################################

class Equal(BinaryOperator):
    OPERATOR = '=='
    PRECEDENCE = 5

class NotEqual(BinaryOperator):
    OPERATOR = '!='
    PRECEDENCE = 5

class LessEqual(BinaryOperator):
    OPERATOR = '<='

class GreaterEqual(BinaryOperator):
    OPERATOR = '>='
    PRECEDENCE = 5

class Less(BinaryOperator):
    OPERATOR = '<'
    PRECEDENCE = 5

class Greater(BinaryOperator):
    OPERATOR = '>'
    PRECEDENCE = 5

####################################################################################################

class And(BinaryOperator):
    OPERATOR = '&&'
    PRECEDENCE = 6

class Or(BinaryOperator):
    OPERATOR = '||'
    PRECEDENCE = 7

####################################################################################################

class If(AstNode):

    PRECEDENCE = 8

    ##############################################

    def __init__(self, condition: AstNode, then_expression: AstNode, else_expression: AstNode) -> None:
        self._condition = condition
        self._then_expression = then_expression
        self._else_expression = else_expression

    ##############################################

    @property
    def condition(self) -> AstNode:
        return self._condition

    ##############################################

    @property
    def then_expression(self) -> AstNode:
        return self._then_expression

    ##############################################

    @property
    def else_expression(self) -> AstNode:
        return self._else_expression

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        return iter((self._condition, self._then_expression, self._else_expression))

    ##############################################

    def __str__(self):
        return f'{self._condition} ? {self._then_expression} : {self._else_expression}'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._condition.pretty_print(level +1)
        txt += self._then_expression.pretty_print(level +1).rstrip() + os.linesep
        txt += self._else_expression.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class Group(AstNode):

    ##############################################

    def __init__(self, child: AstNode) -> None:
        self._child = child

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        yield self._child
        # return iter((self._node,))

    ##############################################

    def __str__(self) -> str:
        # if self._child is not None:
        return f'{self.LEFT} {self._child} {self.RIGHT}'

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level) + self._child.pretty_print(level +1)

####################################################################################################

class ParenthesisGroup(Group):
    LEFT = '('
    RIGHT = ')'

class BraceGroup(Group):
    LEFT = '{'
    RIGHT = '}'

class QuoteGroup(Group):
    LEFT = "'"
    RIGHT = "'"

class BracketGroup(Group):
    LEFT = '['
    RIGHT = ']'
    # Fixme: CONTEXTUAL SYNTAX !!! in_offset=[0.1 -0.2]

    ##############################################

    def __init__(self, child: AstNode) -> None:
        self._child = self._fix_uminus(child)

    ##############################################

    @classmethod
    def _fix_uminus(cls, child: AstNode) -> AstNode:
        """Fix pattern like::

              -
                  -
                      -
                          Number -0.1 None
                          Number 0.2 None
                      Number 0.3 None
                  Number 0.4 None
        """
        new_child = SpaceList()
        for node in child:
            # Is it a subtraction not within a brace ?
            if isinstance(node, Subtraction):
                for _ in cls._fix_uminus_subtraction(node):
                    new_child.append(_)
            else:
                new_child.append(node)
        return new_child

    ##############################################

    @classmethod
    def _fix_uminus_subtraction(cls, node: Subtraction) -> AstNode:
        left = node.operand1
        right = node.operand2
        if isinstance(left, Subtraction) and isinstance(right, Number):
            # Fix recursive case
            # Replace (- (- ... b) c) by (... -b -c) in the AST
            new_child = SpaceList()
            for _ in cls._fix_uminus_inner(left):
                new_child.append(_)
            new_child.append(right.negate())
        elif isinstance(left, Number) and isinstance(right, Number):
            # Replace (- a b) by (a -b) in the AST
            new_child = SpaceList(left, right.negate())
        else:
            return node
        return new_child

####################################################################################################

class List(AstNode):

    SEPARATOR = ''

    ##############################################

    def __init__(self, *args: AstNode) -> None:
        self._childs = list(args)

    ##############################################

    def append(self, item: AstNode) -> None:
        self._childs.append(item)

    ##############################################

    def __len__(self) -> int:
        return len(self._childs)

    def __bool__(self) -> int:
        return bool(self._childs)

    def __iter__(self) -> Iterator[AstNode]:
        return iter(self._childs)

    def __getitem__(self, _slice: slice) -> AstNode:
        return self._childs[_slice]

    ##############################################

    def __str__(self) -> str:
        return self.SEPARATOR.join([str(_) for _ in self._childs])

    def pretty_print(self, level: int=0) -> str:
        txt = ''
        for obj in self:
            txt += obj.pretty_print(level).rstrip() + os.linesep
        return txt

    ##############################################

    # def iter_on_leaf(self, slice_: slice=None) -> Iterator[tuple[int, AstLeaf]]:
    def iter_on_leaf(self, slice_: slice=None) -> Iterator[AstLeaf]:
        childs = self._childs
        if slice_ is not None:
            childs = childs[slice_]
        for position, child in enumerate(childs):
            if child.is_leaf:
                # yield position, child
                yield child
            else:
                break

    ##############################################

    # def iter_on_set(self, slice_: slice=None) -> Iterator['Set']:
    #     # Fixme: duplicated
    #     childs = self._childs
    #     if slice_ is not None:
    #         childs = childs[slice_]
    #     for child in childs:
    #         if isinstance(child, Set):
    #             yield child

    ##############################################

    def find_first_set(self) -> int:
        for position, child in enumerate(self._childs):
            if isinstance(child, Set):
                return position
        return -1

####################################################################################################

class SpaceList(List):
    SEPARATOR = ' '

class CommaList(List):
    SEPARATOR = ', '

class Tuple(CommaList):

    ##############################################

    def __str__(self) -> str:
        return '(' + super().__str__() + ')'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        for obj in self:
            txt += obj.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class Function(AstNode):

    ##############################################

    def __init__(self, name: str, parameters: CommaList) -> None:
        self._name = name
        self._parameters = parameters

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        return iter(self._parameters)

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    ##############################################

    def __str__(self) -> str:
        # if self._parameters:
        return f'{self._name}({self._parameters})'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level, False) + f' {self._name}' + os.linesep
        txt += self._parameters.pretty_print(level +1)
        return txt

####################################################################################################

class PortModifierFunction(AstNode):

    ##############################################

    def __init__(self, port_type: PortTypeModifier, parameters: SpaceList) -> None:
        self._port_type = port_type
        self._parameters = parameters

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        return iter(self._parameters)

    ##############################################

    def __str__(self) -> str:
        return f'{self._port_type}({self._parameters})'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level, False) + f' {self._port_type.name}' + os.linesep
        txt += self._parameters.pretty_print(level +1)
        return txt

####################################################################################################

class PortModifierVector(PortModifierFunction):
    pass

####################################################################################################

class Set(AstNode):

    ##############################################

    def __init__(self, left: AstNode, right: AstNode) -> None:
        self._left = left
        self._right = right

    ##############################################

    def __iter__(self) -> Iterator[AstNode]:
        return iter((self._left, self._right))

    @property
    def left(self) -> AstNode:
        return self._left

    @property
    def right(self) -> AstNode:
        return self._right

    @property
    def left_id(self) -> str:
        if isinstance(self._left, Id):
            return str(self._left)
        else:
            raise ValueError('left is not an Id instance')

    ##############################################

    def __str__(self) -> str:
        return f'{self._left}={self._right}'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._left.pretty_print(level +1).rstrip() + os.linesep
        txt += self._right.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class Command(AstNode):

    ##############################################

    def __init__(self, name: str, childs: SpaceList=None) -> None:
        self._name = name
        self._childs = childs

    ##############################################

    def __len__(self) -> int:
        return len(self._childs)

    def __iter__(self) -> Iterator[AstNode]:
        return iter(self._childs)

    def __getitem__(self, _slice: slice) -> Iterator[AstNode]:
        return self._childs[_slice]

    ##############################################

    @property
    def name(self):
        return self._name

    @property
    def childs(self) -> SpaceList:
        return self._childs

    @property
    def first_child(self) -> AstNode:
        return self._childs[0]

    child = first_child

    ##############################################

    def __str__(self) -> str:
        if self._childs:
            return f'{self._name} {self._childs}'
        else:
            return f'{self._name}'

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level, False) + f' {self._name}' + os.linesep
        if self._childs is not None:
            txt += self._childs.pretty_print(level +1)
        return txt

    ##############################################

    @property
    def first_letter(self) -> str:
        return self._name[0].upper()

    @property
    def after_first_letter(self) -> str:
        return self._name[1:]

    ##############################################

    @property
    def is_dot_command(self) -> bool:
        return self.first_letter == '.'

####################################################################################################

class DotCommand(Command):

    ##############################################

    @property
    def is_dot_command(self) -> bool:
        return True
