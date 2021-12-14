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

"""This module implements a parser for Spice expressions.
"""

####################################################################################################

# Fixme:
#
#  Valid syntax ???
#  print res .endc
#

####################################################################################################

import logging

####################################################################################################

import ply.lex as lex
import ply.yacc as yacc

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceParser:

    _logger = _module_logger.getChild('SpiceParser')

    ##############################################

    reserved = {
    }

    ##############################################

    # When building the master regular expression, rules are added in the following order:
    #   - All tokens defined by functions are added in the same order as they appear in the lexer file.
    #   - Tokens defined by strings are added next by sorting them in order of decreasing regular
    #     expression length (longer expressions are added first).

    tokens = [
        'END_OF_LINE_COMMENT',

        'MINUS',
        'NOT',
        'POWER',
        'MULTIPLY',
        'DIVIDE',
        'MODULO',
        'INT_DIVIDE',
        'ADD',
        'EQUAL',
        'NOT_EQUAL',
        'LESS_EQUAL',
        'GREATER_EQUAL',
        'LESS',
        'GREATER',
        'AND',
        'OR',
        'QUESTION', 'COLON',

        'LEFT_PARENTHESIS', 'RIGHT_PARENTHESIS',
        'COMMA',

        'LEFT_BRACKET', 'RIGHT_BRACKET',

        'LEFT_BRACE', 'RIGHT_BRACE',
        'QUOTE',
        'SET',

        'BRANCH',
        'AT',

        'TILDE',

        'STRING',

        'DOT_COMMAND',
        'ID',
        'INNER_ID',
        'NUMBER',
    ] + list(reserved.values())

    ##############################################

    def t_error(self, token):
        self._logger.error(
            "Illegal character '%s' at line %u and position %u" %
            (token.value[0],
             token.lexer.lineno,
             token.lexer.lexpos))
        # token.lexer.skip(1)
        raise NameError('Lexer error')

    ##############################################

    t_ignore = ' \t'

    ##############################################

    t_END_OF_LINE_COMMENT = r';|\$'

    t_MINUS = r'-'
    t_NOT = r'!'
    t_POWER = r'(\*\*)|\^'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_INT_DIVIDE = r'\\'
    t_ADD = r'\+'
    t_EQUAL = r'=='
    t_NOT_EQUAL = r'!='
    t_LESS_EQUAL = r'<='
    t_GREATER_EQUAL = r'>='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_QUESTION = r'\?'
    t_COLON = r':'

    t_LEFT_PARENTHESIS = r'\('
    t_RIGHT_PARENTHESIS = r'\)'
    t_COMMA = r','

    t_LEFT_BRACKET = r'\['
    t_RIGHT_BRACKET = r'\]'

    t_LEFT_BRACE = r'\{'
    t_RIGHT_BRACE = r'\}'

    t_QUOTE = r"'"
    t_SET = r'='

    t_BRANCH = r'\#branch'
    t_AT = r'@'

    t_TILDE = r'~'

    t_STRING = r'"((\\")|[^"])*"'

    t_DOT_COMMAND = r'\.(?i:[a-z]+)'

    # Fixme:
    # t_ID = r'(?i:[a-z_0-9]+)'    # Fixme:
    t_ID = r'(?i:[a-z_0-9]+(\.[a-z_0-9.]+)?)'    # Fixme:

    # @TOKEN(identifier)
    def t_NUMBER(self, t):
        # Match 1 1. 1.23 .1
        #   https://www.debuggex.com
        r'(?i:(?P<NUMBER_PART>\d+\.\d+(e(\+|-)?(\d+))?|\d+\.(e(\+|-)?(\d+))?|\.\d+(e(\+|-)?(\d+))?|\d+)(?P<UNIT_PART>(meg)|(mil)|[tgkmunpf])?(?P<EXTRA_UNIT>[a-z]*))'
        match = t.lexer.lexmatch.groupdict()
        value = match['NUMBER_PART']
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        t.value = (value, match['UNIT_PART'], match['EXTRA_UNIT'])
        return t

    ##############################################
    #
    # Grammar
    #

    # from lowest
    precedence = (
        ('left', 'QUESTION', 'COLON'),   # Fixme: left ?
        ('left', 'OR'),
        ('left', 'AND'),
        ('nonassoc', 'EQUAL', 'NOT_EQUAL', 'LESS_EQUAL', 'GREATER_EQUAL', 'LESS', 'GREATER'),
        ('left', 'ADD', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MODULO', 'INT_DIVIDE'),
        ('left', 'POWER'),
        ('right', 'UMINUS', 'NOT'),
    )

    # Normally, the first rule found in a yacc specification defines the starting grammar rule
    # (top level rule). To change this, simply supply a start specifier in your file.
    # start = 'statement'

    # def p_program(self, p):
    #     'program : statement'
    #     return p[1]

    def p_dot_command(self, p):
        '''statement : DOT_COMMAND expression_list_space
                     | DOT_COMMAND
        '''
        if len(p) == 3:
            p[0] = ('dot_command', p[1], p[2])
        else:
            p[0] = ('dot_command', p[1])
        return p[0]

    def p_element(self, p):
        '''statement : ID expression_list_space
                     | ID
        '''
        # Fixme: op
        # Fixme: [a-z]...
        if len(p) == 3:
            p[0] = ('command', p[1], p[2])
        else:
            p[0] = ('command', p[1])
        return p[0]

    # def p_empty(self, p):
    #     'empty :'
    #     pass

    def p_modulo_id(self, p):
        '''modulo_id : MODULO ID
        '''
        p[0] = ('modulo_id', p[1])

    def p_branch(self, p):
        '''branch_id : ID BRANCH
        '''
        p[0] = ('branch', p[1])

    def p_tilde(self, p):
        # Fixme: node, number is integer
        '''expression : TILDE ID
                      | TILDE NUMBER
        '''
        p[0] = ('~', p[2])

    def p_inner_parameter(self, p):
        '''expression : AT ID LEFT_BRACKET ID RIGHT_BRACKET
        '''
#                      | AT INNER_ID LEFT_BRACKET ID RIGHT_BRACKET
        p[0] = ('@', p[2], p[4])

    def p_value(self, p):
        '''expression : NUMBER
                      | ID
                      | branch_id
        '''
        p[0] = p[1]

    def p_uminus(self, p):
        '''expression : MINUS expression %prec UMINUS'''
        # %prec UMINUS overrides the default rule precedence-setting it to that of UMINUS in the precedence specifier.
        p[0] = (p[1], p[2])

    def p_unnary_operation(self, p):
        '''expression : NOT expression
        '''
        # ADD expression
        p[0] = (p[1], p[2])

    def p_binary_operation(self, p):
        '''expression : expression POWER expression
                      | expression MULTIPLY expression
                      | expression DIVIDE expression
                      | expression MODULO expression
                      | expression INT_DIVIDE expression
                      | expression ADD expression
                      | expression MINUS expression
                      | expression EQUAL expression
                      | expression NOT_EQUAL expression
                      | expression LESS_EQUAL expression
                      | expression GREATER_EQUAL expression
                      | expression LESS expression
                      | expression GREATER expression
                      | expression AND expression
                      | expression OR expression
        '''
        p[0] = (p[2], p[1], p[3])

    def p_parenthesis(self, p):
        '''expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
        '''
        # | LEFT_BRACE expression RIGHT_BRACE
        p[0] = ('()', p[2])

    def p_if(self, p):
        '''expression : expression QUESTION expression COLON expression
        '''
        p[0] = ('?', p[1], p[3], p[5])

    def p_brace_expression(self, p):
        '''brace_expression : LEFT_BRACE expression RIGHT_BRACE
        '''
        p[0] = ('{}', p[2])

    def p_brace(self, p):
        '''expression : brace_expression
        '''
        p[0] = p[1]

    def p_quote(self, p):
        '''expression : QUOTE expression QUOTE
        '''
        p[0] = ("''", p[2])

    def p_expression_list_space(self, p):
        '''expression_list_space : expression
                                 | expression_list_space expression
        '''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_expression_list_comma(self, p):
        '''expression_list_comma : expression
                                 | expression_list_comma COMMA expression
        '''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_array(self, p):
        '''expression : LEFT_BRACKET expression_list_space RIGHT_BRACKET'''
        p[0] = ('[]', p[2])


    def p_tuple(self, p):
        '''tuple : LEFT_PARENTHESIS expression COMMA expression RIGHT_PARENTHESIS
        '''
        p[0] = ('tuple', p[2], p[4])
        # '''tuple : LEFT_PARENTHESIS expression_list_comma RIGHT_PARENTHESIS
        # '''
        # p[0] = ('tuple', p[1])

    def p_tuple_list(self, p):
        '''tuple_list : tuple
                      | tuple_list tuple
        '''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_function(self, p):
        '''function : ID LEFT_PARENTHESIS expression_list_comma RIGHT_PARENTHESIS
                    | ID LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
        '''
        # | ID LEFT_PARENTHESIS RIGHT_PARENTHESIS
        p[0] = ('function', p[1], p[3])
        # '''function : ID tuple
        # '''
        # # | ID LEFT_PARENTHESIS RIGHT_PARENTHESIS
        # p[0] = ('function', p[1], p[2])

    def p_function_expression(self, p):
        '''expression : function'''
        p[0] = p[1]

    def p_model_function(self, p):
        '''expression : ID LEFT_PARENTHESIS expression_list_space RIGHT_PARENTHESIS
                      | modulo_id LEFT_PARENTHESIS expression_list_space RIGHT_PARENTHESIS
        '''
        # | ID LEFT_PARENTHESIS RIGHT_PARENTHESIS
        p[0] = ('model_function', p[1], p[3])

    def p_parameter(self, p):
        # Fixme:
        #   .ic v(cc) = 0 v(cc2) = 0
        #   Q23 10 24 13 QMOD IC=0.6, 5.0
        '''expression : ID SET expression
                      | function SET expression
                      | brace_expression SET tuple_list
                      | ID SET expression COMMA expression
        '''
        if len(p) == 5:
            p[0] = ('=', p[1], (p[3], p[5]))
        else:
            p[0] = ('=', p[1], p[3])

    def p_error(self, p):
        if p is not None:
            self._logger.error(f"Syntax error at '{p.value}'")
            raise NameError('Syntax Error')
        else:
            self._logger.error("Syntax Error at End Of File")
            raise NameError("Syntax Error at End Of File")

    ##############################################

    def __init__(self):
        self._build()

    ##############################################

    def _build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)
        self._parser = yacc.yacc(module=self, **kwargs)

    ##############################################

    def lex(self, text: str):
        self._lexer.input(text)
        root = Ast()
        while True:
            token = self._lexer.token()
            if token:
                root.append_token(token)
            else:
                break
        root.process()

    ##############################################

    def parse(self, text):
        # self._parser.defaulted_states = {}
        _ = self._parser.parse(text, lexer=self._lexer, debug=False)
        print(f'ast {_}')
