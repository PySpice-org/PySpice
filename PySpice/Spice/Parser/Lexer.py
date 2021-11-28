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

import logging

####################################################################################################

import ply.lex as lex

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Lexer:

    _logger = _module_logger.getChild('Lexer')

    ##############################################

    reserved = {
    }

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

        'SHARP',
        'AT',

        'TILDE',

        'DOT_COMMAND',
        'ID',
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

    t_QUOTE = r'\''
    t_SET = r'='

    t_SHARP = r'\#'
    t_AT = r'@'

    t_TILDE = r'~'

    t_DOT_COMMAND = r'\.(?i:[a-z]+)'
    t_ID = r'(?i:[a-z_][a-z_0-9]*)'    # Fixme:

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

    def __init__(self):
        self._build()

    ##############################################

    def _build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    ##############################################

    def test_lexer(self, text):
        self._lexer.input(text)
        while True:
            token = self._lexer.token()
            if not token:
                break
            print(token)
