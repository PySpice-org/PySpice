####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
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

"""This module implements Abstract Syntactic Tree for Spice expressions.
"""

####################################################################################################

import logging
import os

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class StatementList:

    ##############################################

    def __init__(self, *statements):

        self._statements = list(statements)

    ##############################################

    def __nonzero__(self):

        return bool(self._statements)

    ##############################################

    def __iter__(self):

        return iter(self._statements)

    ##############################################

    def add(self, statement):

        self._statements.append(statement)

    ##############################################

    def __str__(self):

        return os.linesep.join([str(statement) for statement in self])

####################################################################################################

class Program(StatementList):
    pass

####################################################################################################

class Variable:

    ##############################################

    def __init__(self, name):
        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    def __str__(self):
        return self._name

####################################################################################################

class Constant:

    ##############################################

    def __init__(self, value):
        self._value = value

    ##############################################

    def __str__(self):
        return str(self._value)

####################################################################################################

class IntConstant(Constant):

    ##############################################

    def __int__(self):
        return self._value

####################################################################################################

class FloatConstant(Constant):

    ##############################################

    def __float__(self):
        return self._value

####################################################################################################

class Expression:

    NUMBER_OF_OPERANDS = None

    ##############################################

    def __init__(self, *args, **kwargs):

        if (self.NUMBER_OF_OPERANDS is not None
            and len(args) != self.NUMBER_OF_OPERANDS):
            raise ValueError("Wrong number of operands")

        self._operands = args

    ##############################################

    def iter_on_operands(self):
        return iter(self._operands)

    ##############################################

    @property
    def operand(self):
        return self._operands[0]

    @property
    def operand1(self):
        return self._operands[0]

    @property
    def operand2(self):
        return self._operands[1]

    @property
    def operand3(self):
        return self._operands[2]

class UnaryExpression(Expression):
    NUMBER_OF_OPERANDS = 1

class BinaryExpression(Expression):
    NUMBER_OF_OPERANDS = 2

class TernaryExpression(Expression):
    NUMBER_OF_OPERANDS = 3

####################################################################################################

class OperatorMetaclass(type):

    """Metaclass to register operators"""

    _declaration_order = 0
    _operators = []
    _unary_operator_map = {}
    _binary_operator_map = {}

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):

        cls = type.__new__(meta, class_name, base_classes, attributes)
        if cls.OPERATOR is not None:
            meta.register_prefix(cls)
        return cls

    ##############################################

    @classmethod
    def register_prefix(meta, cls):

        cls._declaration_order  = meta._declaration_order
        meta._declaration_order += 1
        meta._operators.append(cls)
        if issubclass(cls, UnaryOperator):
            d = meta._unary_operator_map
        elif issubclass(cls, BinaryOperator):
            d = meta._binary_operator_map
        d[cls.OPERATOR] = cls

    ##############################################

    @classmethod
    def operator_iter(cls):
        return iter(cls._operators)

    ##############################################

    @classmethod
    def get_unary(cls, operator):
        return cls._unary_operator_map[operator]

    ##############################################

    @classmethod
    def get_binary(cls, operator):
        return cls._binary_operator_map[operator]

####################################################################################################

class OperatorMixin(metaclass=OperatorMetaclass):
    OPERATOR = None
    _declaration_order = 0

####################################################################################################

class UnaryOperator(UnaryExpression, OperatorMixin):

    def __str__(self):
        return ' '.join((self.OPERATOR, str(self.operand1)))

####################################################################################################

class BinaryOperator(BinaryExpression, OperatorMixin):

    def __str__(self):
        return ' '.join((str(self.operand1), self.OPERATOR, str(self.operand2)))

####################################################################################################

class Assignation(BinaryExpression):

    @property
    def variable(self):
        return self._operands[1]

    @property
    def value(self):
        return self._operands[0]

    def __str__(self):
        return ' '.join((str(self.destination), '=', str(self.value)))

####################################################################################################

class Negation(UnaryOperator):
    OPERATOR = '-'
    PRECEDENCE = 1

class Not(UnaryOperator):
    OPERATOR = '!'
    PRECEDENCE = 1

####################################################################################################

class power(BinaryOperator):
    OPERATOR = '**'
    PRECEDENCE = 2

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

class If: #(TernaryExpression)

    # c ? x : y

    PRECEDENCE = 8

    ##############################################

    def __init__(self, condition, then_expression, else_expression):

        self._condition = condition
        self._then_expression = then_expression
        self._else_expression = else_expression

    ##############################################

    @property
    def condition(self):
        return self._condition

    ##############################################

    @property
    def then_expression(self):
        return self._then_expression

    ##############################################

    @property
    def else_expression(self):
        return self._else_expression

    ##############################################

    # def _str_compound_expression(self, expressions):

    #     string = '(' + os.linesep
    #     if expressions:
    #         string += str(expressions) + os.linesep
    #     string += ')'

    #     return string

    ##############################################

    def __str__(self):

        return '{} ? {} : {}'.format(self._condition, self._then_expression, self._else_expression)

####################################################################################################

class Function(Expression):

    ##############################################

    def __init__(self, name, *args):

        super(Function, self).__init__(*args)
        self._name = name

    ##############################################

    @property
    def name(self):
        return self._name

    ##############################################

    def __str__(self):

        parameters = ', '.join([str(operand) for operand in self.iter_on_operands()])
        return self._name + ' (' + parameters  + ')'
