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

"""This module implements a AST for Spice.
"""

# Fixme: duplicate code

####################################################################################################

__all__ = [
    'Addition',
    'And',
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
    'ModelFunction',
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
    'Tuple',
    'UnaryOperator',
]

####################################################################################################

import os

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

####################################################################################################

class Integer(AstNode):

    ##############################################

    def __init__(self, value: int | float) -> None:
        self._value = value

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f" {self._value}"

####################################################################################################

class Number(AstNode):

    ##############################################

    def __init__(self, value: int | float, unit: str | None, extra_unit: str | None) -> None:
        self._value = value
        self._unit = unit
        self._extra_unit = extra_unit
        # self._is_interger = isinstance(value, int) and not unit and not extra_unit

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f" {self._value} {self._unit} {self._extra_unit}"

####################################################################################################

class Id(AstNode):

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f" {self._name}"

####################################################################################################

class PortTypeModifier(AstNode):

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    ##############################################

    # def pretty_print(self, level: int=0) -> str:
    #     return self.pretty_print_class(level, False) + f" {self._name}"

####################################################################################################

class Branch(AstNode):

    ##############################################

    def __init__(self, name: str) -> None:
        # Fixme: source
        self._name = name

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f" {self._name}"

####################################################################################################

class InvertedInput(AstNode):

    ##############################################

    def __init__(self, node: str) -> None:
        self._node = node

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._node.pretty_print(level +1)
        return txt

####################################################################################################

class InnerParameter(AstNode):

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

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level, False) + f" {self._element_path} {self._parameter_name}"

####################################################################################################

class Operator(AstNode):

    NUMBER_OF_OPERANDS = None
    OPERATOR = None

    # _operators = []
    _unary_operator_map = {}
    _binary_operator_map = {}

    ##############################################

    def __init_subclass__(cls, **kwargs) -> None:
        if cls.OPERATOR is not None:
            # cls._operators.append(cls)
            if issubclass(cls, BinaryOperator):
                d = cls._binary_operator_map
            elif issubclass(cls, UnaryOperator):
                d = cls._unary_operator_map
            d[cls.OPERATOR] = cls

    ##############################################

    # @classmethod
    # def operator_iter(cls):
    #     return iter(cls._operators)

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
            raise ValueError("Wrong number of operands")
        self._operands = args

    ##############################################

    @property
    def operands(self):
        return iter(self._operands)

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        indentation = self.indentation(level)
        txt = indentation + self.OPERATOR + os.linesep
        for operand in self.operands:
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
        return self._operands[0]

    @property
    def operand1(self) -> AstNode:
        return self._operands[0]

    ##############################################

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
        return self._operands[1]

    ##############################################

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

    # def _str_compound_expression(self, expressions):
    #     string = '(' + os.linesep
    #     if expressions:
    #         string += str(expressions) + os.linesep
    #     string += ')'
    #     return string

    ##############################################

    # def __str__(self):
    #     return '{} ? {} : {}'.format(self._condition, self._then_expression, self._else_expression)

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._condition.pretty_print(level +1)
        txt += self._then_expression.pretty_print(level +1).rstrip() + os.linesep
        txt += self._else_expression.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class Group(AstNode):

    ##############################################

    def __init__(self, ast_node: AstNode) -> None:
        self._ast_node = ast_node

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        return self.pretty_print_class(level) + self._ast_node.pretty_print(level +1)

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

####################################################################################################

class List(AstNode):

    ##############################################

    def __init__(self, *args: AstNode) -> None:
        self._list = list(args)

    ##############################################

    def append(self, item: AstNode) -> None:
        self._list.append(item)

    ##############################################

    def __len__(self) -> int:
        return len(self._list)

    def __bool__(self) -> int:
        return bool(self._list)

    def __iter__(self) -> int:
        return iter(self._list)

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        txt = ''
        for obj in self:
            txt += obj.pretty_print(level).rstrip() + os.linesep
        return txt

####################################################################################################

class SpaceList(List):
    SEPARATOR = ' '

class CommaList(List):
    SEPARATOR = ', '

class Tuple(CommaList):

    ##############################################

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

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level, False) + f' {self._name}' + os.linesep
        txt += self._parameters.pretty_print(level +1)
        return txt

####################################################################################################

class ModelFunction(AstNode):

    ##############################################

    def __init__(self, name: str, parameters: SpaceList) -> None:
        self._name = name
        self._parameters = parameters

    ##############################################

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

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level)
        txt += self._left.pretty_print(level +1).rstrip() + os.linesep
        txt += self._right.pretty_print(level +1).rstrip() + os.linesep
        return txt

####################################################################################################

class Command(AstNode):

    ##############################################

    def __init__(self, name: str, expressions: SpaceList=None) -> None:
        self._name = name
        self._expressions = expressions

    ##############################################

    def pretty_print(self, level: int=0) -> str:
        txt = self.pretty_print_class(level, False) + f' {self._name}' + os.linesep
        if self._expressions is not None:
            txt += self._expressions.pretty_print(level +1)
        return txt

    ##############################################

    @property
    def first_letter(self):
        return self._name[0].lower()

    ##############################################

    @property
    def is_dot_command(self):
        return self.first_letter == '.'

####################################################################################################

class DotCommand(Command):

    ##############################################

    @property
    def is_dot_command(self):
        return True
