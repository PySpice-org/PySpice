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

    __number_of_operands__ = None

    ##############################################

    def __init__(self, *args, **kwargs):

        if (self.__number_of_operands__ is not None
            and len(args) != self.__number_of_operands__):
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
    __number_of_operands__ = 1

class BinaryExpression(Expression):
    __number_of_operands__ = 2

class TernaryExpression(Expression):
    __number_of_operands__ = 3

####################################################################################################

class OperatorMetaclass(type):

    """Metaclass to register operators"""

    __declaration_order__ = 0
    __operators__ = []
    __unary_operator_map__ = {}
    __binary_operator_map__ = {}

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):

        cls = type.__new__(meta, class_name, base_classes, attributes)
        if cls.__operator__ is not None:
            meta.register_prefix(cls)
        return cls

    ##############################################

    @classmethod
    def register_prefix(meta, cls):

        cls.__declaration_order__  = meta.__declaration_order__
        meta.__declaration_order__ += 1
        meta.__operators__.append(cls)
        if issubclass(cls, UnaryOperator):
            d = meta.__unary_operator_map__
        elif issubclass(cls, BinaryOperator):
            d = meta.__binary_operator_map__
        d[cls.__operator__] = cls

    ##############################################

    @classmethod
    def operator_iter(cls):
        return iter(cls.__operators__)

    ##############################################

    @classmethod
    def get_unary(cls, operator):
        return cls.__unary_operator_map__[operator]

    ##############################################

    @classmethod
    def get_binary(cls, operator):
        return cls.__binary_operator_map__[operator]

####################################################################################################

class OperatorMixin(metaclass=OperatorMetaclass):
    __operator__ = None
    __declaration_order__ = 0

####################################################################################################

class UnaryOperator(UnaryExpression, OperatorMixin):

    def __str__(self):
        return ' '.join((self.__operator__, str(self.operand1)))

####################################################################################################

class BinaryOperator(BinaryExpression, OperatorMixin):

    def __str__(self):
        return ' '.join((str(self.operand1), self.__operator__, str(self.operand2)))

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
    __operator__ = '-'
    __precedence__ = 1

class Not(UnaryOperator):
    __operator__ = '!'
    __precedence__ = 1

####################################################################################################

class power(BinaryOperator):
    __operator__ = '**'
    __precedence__ = 2

class Multiplication(BinaryOperator):
    __operator__ = '*'
    __precedence__ = 3

class Division(BinaryOperator):
    __operator__ = '/'
    __precedence__ = 3

class Modulo(BinaryOperator):
    __operator__ = '%'
    __precedence__ = 3

class IntegerDivision(BinaryOperator):
    __operator__ = '\\'
    __precedence__ = 3

class Addition(BinaryOperator):
    __operator__ = '+'
    __precedence__ = 4

class Subtraction(BinaryOperator):
    __operator__ = '-'
    __precedence__ = 4

####################################################################################################

class Equal(BinaryOperator):
    __operator__ = '=='
    __precedence__ = 5

class NotEqual(BinaryOperator):
    __operator__ = '!='
    __precedence__ = 5

class LessEqual(BinaryOperator):
    __operator__ = '<='

class GreaterEqual(BinaryOperator):
    __operator__ = '>='
    __precedence__ = 5

class Less(BinaryOperator):
    __operator__ = '<'
    __precedence__ = 5

class Greater(BinaryOperator):
    __operator__ = '>'
    __precedence__ = 5

####################################################################################################

class And(BinaryOperator):
    __operator__ = '&&'
    __precedence__ = 6

class Or(BinaryOperator):
    __operator__ = '||'
    __precedence__ = 7

####################################################################################################

class If: #(TernaryExpression)

    # c ? x : y

    __precedence__ = 8

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
