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

"""This module implements a parser for Spice expressions.
"""

####################################################################################################

import logging

####################################################################################################

import ply.lex as lex
import ply.yacc as yacc

####################################################################################################

from .Ast import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# def ensure_statement_list(x):
#     if isinstance(x, StatementList):
#         return x
#     else:
#         return StatementList(x)

####################################################################################################

class Parser:

    _logger = _module_logger.getChild('Parser')

    ##############################################

    reserved = {
    }

    tokens = [
        'NAME',
        # 'INT', 'FLOAT',
        'NUMBER',
        'SEMICOLON',
        'LEFT_PARENTHESIS', 'RIGHT_PARENTHESIS',
        'SET',
        'NOT',
        'POWER',
        'MULTIPLY',
        'DIVIDE', 'INT_DIVIDE', 'MODULO',
        'PLUS', 'MINUS',
        'EQUAL', 'NOT_EQUAL', 'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL',
        'AND', 'OR',
        'IF', 'COLON',
    ] + list(reserved.values())

    ##############################################

    def t_error(self, token):
        self._logger.error("Illegal character '%s' at line %u and position %u" %
                           (token.value[0],
                            token.lexer.lineno,
                            token.lexer.lexpos - self._previous_newline_position))
        # token.lexer.skip(1)
        raise NameError('Lexer error')

    ##############################################

    t_ignore  = ' \t'

    def t_newline(self, t):
        r'\r?\n+'
        # Track newline
        t.lexer.lineno += len(t.value)
        self._previous_newline_position = t.lexer.lexpos
        # t.type = 'SEMICOLON'
        # return t

    t_ignore_COMMENT = r'\#[^\n]*'

    ##############################################

    t_SEMICOLON = r';'

    t_LEFT_PARENTHESIS = r'\('
    t_RIGHT_PARENTHESIS = r'\)'

    t_SET = r'='

    t_NOT = r'!'

    t_POWER = r'\*\*'

    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_INT_DIVIDE = r'\/'

    t_PLUS = r'\+'
    t_MINUS = r'-'

    t_EQUAL = r'=='
    t_NOT_EQUAL = r'!='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_LESS_EQUAL = r'<='
    t_GREATER_EQUAL = r'>='

    t_AND = r'&&'
    t_OR = r'\|\|'

    t_IF = r'\?'
    t_COLON = r':'

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = self.reserved.get(t.value, 'NAME') # Fixme: ???
        return t

    # def t_INT(self, t):
    #     r'\d+'
    #     t.value = int(t.value)
    #     return t

    # exponent_part = r"""([eE][-+]?[0-9]+)"""
    # fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
    # floating_constant = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))[FfLl]?)'

    def t_NUMBER(self, t):
        # 1 1. 1.23 .1
        # r'\d*\.?\d+([eE][-+]?\d+)?'
        # r'(\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+)'
        r'\d+\.\d+(e(\+|-)?(\d+))? | \d+\.(e(\+|-)?(\d+))? | \.\d+(e(\+|-)?(\d+))? | \d+'
        t.value = t.value
        return t

    ##############################################
    #
    # Grammar
    #

    # from lowest
    precedence = (
        ('left', 'IF'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL', 'NOT_EQUAL', 'EQUAL'),
        ('left', 'MINUS', 'PLUS'),
        ('left', 'INT_DIVIDE', 'MODULO', 'DIVIDE', 'MULTIPLY'),
        ('left', 'POWER'),
        ('left', 'NOT'), # , 'NEGATION'
    )

    def p_error(self, p):
        if p:
            self._logger.error("Syntax error at '%s'", p.value)
            raise NameError('Syntax Error')
        else:
            self._logger.error("Syntax Error at End Of File")
            raise NameError("Syntax Error at End Of File" )

    # start = 'program'
    start = 'statement'

    # def p_empty(self, p):
    #     'empty :'
    #     pass

    def p_statement(self, t):
        'statement : expression'
        print('statement', t[1])

    # def p_program(self, p):
    #     '''program : statement
    #                | program statement
    #                | empty
    #     '''
    #     if len(p) == 3:
    #         statement = p[2]
    #     else:
    #         statement = p[1]
    #     if statement is not None:
    #         self._program.add(statement)

    # def p_statement(self, p):
    #     '''statement : expression_statement
    #     '''
    #     p[0] = p[1]

    # def p_expression_statement(self, p):
    #     '''expression_statement : assignation SEMICOLON
    #                             | function SEMICOLON
    #                             | SEMICOLON
    #     '''
    #     if len(p) == 3:
    #         p[0] = p[1]

    # def p_statement_list(self, p):
    #     '''statement_list : statement
    #                       | statement_list statement
    #     '''
    #     if len(p) == 3:
    #         p[1].add(p[2])
    #         p[0] = p[1]
    #     else:
    #         p[0] = StatementList(p[1])

    # def p_expression_list(self, p):
    #     '''expression_list : expression
    #                        | expression_list COMMA expression
    #     '''
    #     if len(p) == 3:
    #         p[1].add(p[2])
    #         p[0] = p[1]
    #     else:
    #         p[0] = StatementList(p[1])

    # def p_function(self, p):
    #     '''function : NAME LEFT_PARENTHESIS expression_list RIGHT_PARENTHESIS
    #                 | NAME LEFT_PARENTHESIS RIGHT_PARENTHESIS
    #     '''
    #     if len(p) == 5:
    #         p[0] = Function(p[1], p[3])
    #     else:
    #         p[0] = Function(p[1])

    def p_variable(self, p):
        '''variable : NAME
        '''
        p[0] = Variable(p[1])

    # def p_assignation(self, p):
    #     'assignation : variable SET expression'
    #     p[0] = Assignation(p[3], p[1]) # eval value first

    # def p_interger(self, p):
    #     '''constant : INT
    #     '''
    #     p[0] = IntConstant(p[1])

    def p_float(self, p):
        '''constant : NUMBER
        '''
        if '.' in p[1]:
            p[0] = FloatConstant(p[1])
        else:
            p[0] = IntConstant(p[1])

    def p_value(self, p):
        '''expression : variable
                      | constant
        '''
        p[0] = p[1]

    def p_unnary_operation(self, p):
        # OP ...
        '''expression : MINUS expression
                      | NOT expression
        '''
        p[0] = OperatorMetaclass.get_unary(p[1])(p[2])

    def p_binary_operation(self, p):
        # ... OP ...
        '''expression : expression POWER expression
                      | expression MULTIPLY expression
                      | expression DIVIDE expression
                      | expression MODULO expression
                      | expression INT_DIVIDE expression
                      | expression PLUS expression
                      | expression MINUS expression
                      | expression EQUAL expression
                      | expression NOT_EQUAL expression
                      | expression LESS expression
                      | expression GREATER expression
                      | expression LESS_EQUAL expression
                      | expression GREATER_EQUAL expression
                      | expression AND expression
                      | expression OR expression
        '''
        p[0] = OperatorMetaclass.get_binary(p[2])(p[1], p[3])

    def p_if(self, p):
        '''expression : expression IF expression COLON expression
        '''
        p[0] = If(p[1], p[3], p[5])

    ##############################################

    def __init__(self):

        self._build()

    ##############################################

    def _build(self, **kwargs):

        self._lexer = lex.lex(module=self, **kwargs)
        self._parser = yacc.yacc(module=self, **kwargs)

    ##############################################

    def _reset(self):

        self._previous_newline_position = 0
        # self._program = Program()

    ##############################################

    def parse(self, text):

        self._reset() # Fixme: after ?
        self._parser.parse(text, lexer=self._lexer)
        # return self._program

    ##############################################

    def test_lexer(self, text):

        self._reset()
        self._lexer.input(text)
        while True:
            token = self._lexer.token()
            if not token:
                break
            print(token)
