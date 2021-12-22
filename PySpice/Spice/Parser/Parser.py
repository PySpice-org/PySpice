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

"""This module tries to implements a LALR parser for Spice.

**Notes**

* Ngspice only use a LALR parser to parse mathematical expression.
* Ngspice syntax is sometimes contextual.
* We can implement a tokenizer.
* But the Ngspice's rules to group the tokens is unknown, i.e. how to handle :code:`() {} [] '' =`
  and to make the AST.
* Moreover it is more difficult to implement by hand such algorithm.  Some experimental codes was
  removed in favour of this LALR parser.

**Known Syntax Issues**

* :code:`in_offset=[0.1 -0.2]` is interpreted as a subtraction due to the space token separator.  We
  could fix that by adding the unary minus in the float regexp, but it would break the parsing of
  mathematical expressions.  A workaround is to use a brace expression, :code:`{-0.2}`.  Can we fix
  the AST afterwards ???  For example, remove recursively the unary minus from the AST.

"""

__all__ = ['SpiceParser']

####################################################################################################
# Fixme:
#
#  Valid syntax ???
#  print res .endc
####################################################################################################

####################################################################################################

import logging
from typing import Optional

import ply.lex as lex
import ply.yacc as yacc

from .Ast import *

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class SpiceParser:

    _logger = _module_logger.getChild('SpiceParser')

    ##############################################

    # When building the master regular expression, rules are added in the following order:
    #   - All tokens defined by functions are added in the same order as they appear in the lexer file.
    #   - Tokens defined by strings are added next by sorting them in order of decreasing regular
    #     expression length (longer expressions are added first).

    tokens = [
        # 'END_OF_LINE_COMMENT',

        # in this order
        'ID',
        'NUMBER',

        # sorted by length
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
    ]

    ##############################################

    def t_error(self, token):
        self._logger.error(f"Illegal character '{token.value[0]}' at line {token.lexer.lineno} and position {token.lexer.lexpos}")
        # token.lexer.skip(1)
        raise NameError('Lexer error')

    ##############################################

    t_ignore = ' \t'

    ##############################################

    # t_END_OF_LINE_COMMENT = r';|\$'

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

    # Note: ID and NUMBER must be defined in a function in order to be sorted the right order
    #       Else 2N2222A will be split in two tokens

    def t_ID(self, t):
        # Fixme:
        r'''
        (?i:
            [a-z_0-9]+
            (\.[a-z_0-9.]+) ?
        )'''
        # t.value = Id(t.value)
        return t

    # @TOKEN(identifier)
    def t_NUMBER(self, t):
        # Fixme: CONTEXTUAL SYNTAX !!! in_offset=[0.1 -0.2]
        r'''
        (?i:
            (?P<NUMBER_PART>
                # [-+]?
                (?:
                    (?: \d* \. \d+ )   # .1 .12 ... 9.1 98.1 ...
                    |
                    (?: \d+ \.? )      # 1. 12. ... 1 12 ...
                )
                (?: e [+-]? \d+ ) ?
            )
            (?P<UNIT_PART>
                (meg) | (mil) | [tgkmunpf]
            ) ?
            (?P<EXTRA_UNIT>
                [a-z]*
            )
        )
        '''
        match = t.lexer.lexmatch.groupdict()
        value = match['NUMBER_PART']
        unit = match['UNIT_PART']
        extra_unit = match['EXTRA_UNIT']
        try:
            value = int(value)
        except ValueError:
            value = float(value)
        if isinstance(value, int) and not unit and not extra_unit:
            t.value = Integer(value)
        else:
            t.value = Number(value, unit, extra_unit)
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
    # start = ''

    def _command(self, p, cls):
        if len(p) == 3:
            p[0] = cls(p[1], p[2])
        else:
            p[0] = cls(p[1])
        return p[0]

    def p_command(self, p):
        '''command : ID expression_list_space
                   | ID
        '''
        return self._command(p, Command)

    # Fixme: could be merged with command
    def p_dot_command(self, p):
        '''command : DOT_COMMAND expression_list_space
                   | DOT_COMMAND
        '''
        return self._command(p, DotCommand)

    def p_branch(self, p):
        '''expression : ID BRANCH
        '''
        p[0] = Branch(p[1])

    def p_tilde(self, p):
        # Fixme: node, number is a node integer
        '''expression : TILDE ID
                      | TILDE NUMBER
        '''
        p[0] = InvertedInput(p[2])

    def p_inner_parameter(self, p):
        '''expression : AT ID LEFT_BRACKET ID RIGHT_BRACKET
        '''
        p[0] = InnerParameter(p[2], p[4])

    def p_number(self, p):
        '''expression : NUMBER
        '''
        p[0] = p[1]

    def p_id(self, p):
        '''expression : ID
        '''
        p[0] = Id(p[1])

    def p_uminus(self, p):
        '''expression : MINUS expression %prec UMINUS'''
        # %prec UMINUS overrides the default rule precedence-setting it to that of UMINUS in the precedence specifier.
        _ = p[2]
        if isinstance(_, (Integer, Number)):
            p[0] = _.negate()
        else:
            p[0] = Negation(_)

    def p_unnary_operation(self, p):
        '''expression : NOT expression
        '''
        p[0] = Not(p[2])

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
        p[0] = Operator.get_binary(p[2])(p[1], p[3])

    def p_parenthesis(self, p):
        '''expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
        '''
        p[0] = ParenthesisGroup(p[2])

    def p_if(self, p):
        '''expression : expression QUESTION expression COLON expression
        '''
        p[0] = If(p[1], p[3], p[5])

    def p_brace_expression(self, p):
        '''brace_expression : LEFT_BRACE expression RIGHT_BRACE
        '''
        p[0] = BraceGroup(p[2])

    def p_brace(self, p):
        '''expression : brace_expression
        '''
        p[0] = p[1]

    def p_quote(self, p):
        '''expression : QUOTE expression QUOTE
        '''
        p[0] = QuoteGroup(p[2])

    def p_expression_list_space(self, p):
        '''expression_list_space : expression
                                 | expression_list_space expression
        '''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = SpaceList(p[1])

    def p_expression_list_comma(self, p):
        '''expression_list_comma : expression
                                 | expression_list_comma COMMA expression
        '''
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = CommaList(p[1])

    def p_array(self, p):
        '''expression : LEFT_BRACKET expression_list_space RIGHT_BRACKET'''
        p[0] = BracketGroup(p[2])

    def p_tuple(self, p):
        '''tuple : LEFT_PARENTHESIS expression COMMA expression RIGHT_PARENTHESIS
        '''
        p[0] = Tuple(p[2], p[4])

    def p_tuple_list(self, p):
        '''tuple_list : tuple
                      | tuple_list tuple
        '''
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = SpaceList(p[1])

    def p_function(self, p):
        '''function : ID LEFT_PARENTHESIS expression_list_comma RIGHT_PARENTHESIS
                    | ID LEFT_PARENTHESIS expression_list_space RIGHT_PARENTHESIS
        '''
        # Match: sqrt(9)
        p[0] = Function(p[1], p[3])

    def p_function_expression(self, p):
        '''expression : function'''
        p[0] = p[1]

    def p_port_type_modifier(self, p):
        '''port_type_modifier : MODULO ID
        '''
        # Fixme: use token %[a-z]+ ?
        p[0] = PortTypeModifier(p[2])

    def p_port_modifier_function(self, p):
        '''expression : port_type_modifier LEFT_PARENTHESIS expression_list_space RIGHT_PARENTHESIS
        '''
        p[0] = PortModifierFunction(p[1], p[3])

    def p_port_modifier_vector(self, p):
        '''expression : port_type_modifier LEFT_BRACKET expression_list_space RIGHT_BRACKET
        '''
        p[0] = PortModifierVector(p[1], p[3])

    def p_set_id(self, p):
        '''expression : ID SET expression
                      | ID SET expression COMMA expression
        '''
        if len(p) == 5:
            p[0] = Set(Id(p[1]), Tuple(p[3], p[5]))
        else:
            p[0] = Set(Id(p[1]), p[3])

    def p_parameter(self, p):
        # Fixme:
        #   .ic v(cc) = 0 v(cc2) = 0
        #   Q23 10 24 13 QMOD IC=0.6, 5.0
        # Fixme: expression => recursive
        '''expression : function SET expression
                      | brace_expression SET tuple_list
        '''
        p[0] = Set(p[1], p[3])

    def p_error(self, p):
        if p is not None:
            self._logger.error(f"Syntax error at '{p.value}'")
            raise NameError('Syntax Error')
        else:
            self._logger.error("Syntax Error at End Of File")
            raise NameError("Syntax Error at End Of File")

    ##############################################

    def __init__(self) -> None:
        self._build()

    ##############################################

    def _build(self, **kwargs) -> None:
        self._lexer = lex.lex(module=self, **kwargs)
        self._parser = yacc.yacc(module=self, **kwargs)

    ##############################################

    def lex(self, text: str):
        self._lexer.input(text)
        while True:
            token = self._lexer.token()
            if token:
                yield token
            else:
                break

    ##############################################

    @staticmethod
    def dot_command(line: str) -> Optional[str]:
        if not line.startswith('.'):
            return None
        i = line.find(' ')
        if i == -1:
            _ = line
        else:
            _ = line[:i]
        return _.lower()

    @staticmethod
    def right_of(line: str, prefix: str) -> str:
        return line[len(prefix):].strip()

    ##############################################

    def parse(self, line: str) -> Command:
        """Parse a spice line.

        The LALR parser don't handle :code:`.include`, :code:`.lib` and :code:`.title`.

        It raises :code:`NameError('Syntax Error')`

        """

        line = line.strip()

        dot_command = self.dot_command(line)
        if dot_command is not None:
            match dot_command:
                case '.include':
                    return DotCommand(
                        '.include',
                        SpaceList(
                            Text(self.right_of(line, '.include').strip('"'))
                        )
                    )
                case '.lib':
                    # Fixme: how ngspice handle space in filename ?
                    _ = self.right_of(line, '.lib')
                    i = _.rfind(' ')
                    return DotCommand(
                        '.lib',
                        SpaceList(
                            Text(_[:i].rstrip()),
                            Text(_[i+1:])
                        )
                    )
                case '.title':
                    # Not handled by parser by commodity
                    return DotCommand(
                        '.title',
                        SpaceList(
                            Text(self.right_of(line, '.title'))
                        )
                    )

        # self._parser.defaulted_states = {}
        return self._parser.parse(line, lexer=self._lexer, debug=False)
