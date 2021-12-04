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
import ply.yacc as yacc

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class AstLeaf:

    ##############################################

    def __init__(self, type_: str, value: str | int | float, position: int, index: int):
        self._type = type_
        self._value = value
        self._position = position
        self._index = index
        self.parent = None
        self.prev = None
        self.next = None

    ##############################################

    @property
    def type(self) -> str:
        return self._type

    def is_type(self, type_):
        return self._type == type_

    @property
    def value(self) -> str | int | float:
        return self._value

    @property
    def position(self) -> int:
        return self._position

    @property
    def index(self) -> int:
        return self._index

    @property
    def is_head(self) -> bool:
        return self.prev is None

    @property
    def is_last(self) -> bool:
        return self.next is None

    ##############################################

    def __repr__(self) -> str:
        return f"{self._type}: {self._value} @{self._position}"

    ##############################################

    def iter_on_chain(self):
        token = self
        while True:
            yield token
            next_token = token.next
            if next_token is not None:
                token = next_token
            else:
                break

####################################################################################################

def pair_iter(alist):
    number_of_items = len(alist)
    if number_of_items > 1:
        for i in range(number_of_items - 1):
            yield alist[i], alist[i+1]

####################################################################################################

class Ast:

    ##############################################

    def __init__(self):
        # Fixme: purpose
        self._head = None
        self._tokens = []
        self._left_token = None
        self._right_token = None
        self.parent = None
        self.prev = None
        self.next = None

    ##############################################

    def __len__(self) -> int:
        return len(self._tokens)

    def __iter__(self):
        return iter(self._tokens)

    @property
    def head(self) -> AstLeaf:   #  | Ast
        # Fixme: head / first ?
        # return self._tokens[0]
        return self._head

    def iter_on_chain(self):
        yield from self.head.iter_on_chain()
        # Fixme: right_token.prev is linked
        # for token in self.head.iter_on_chain():
        #     if token is not self._right_token:
        #         yield token

    ##############################################

    def append(self, token: AstLeaf):
        token.parent = self
        if not self._tokens:
            self._head = token
        self._tokens.append(token)

    ##############################################

    def append_token(self, lex_token: lex.Token):
        token = AstLeaf(lex_token.type, lex_token.value, lex_token.lexpos, len(self._tokens))
        # Fixme:
        token.parent = self
        if not self._tokens:
            self._head = token
        self._tokens.append(token)

    ##############################################

    def dump(self):
        for token in self:
            print(token)

    ##############################################

    def process(self):
        self._chain()
        self._match_left_right()
        self.dump()
        self._make_ast()
        print()
        print('*** AST')
        self.dump_ast()

    ##############################################

    def _chain(self):
        # token.position = i ???
        for token1, token2 in pair_iter(self._tokens):
            token1.next = token2
            token2.prev = token1

    ##############################################

    def _match_left_right(self):

        def handle_right(label, stack, token):
            if stack:
                left = stack.pop()
                left.right = token
                token.left = left
                print(f"Match {label} {left.index} {token.index}")
            else:
                raise NameError(f"{label} mismatch @{token.position}")

        left_quote = None
        parenthesis_stack = []
        brace_stack = []
        bracket_stack = []
        for i, token in enumerate(self):
            match token.type:
                case 'QUOTE':
                    if left_quote is not None:
                        left_quote.right = token
                        token.left = left_quote
                        print(f"Match quote {left_quote.index} {token.index}")
                        left_quote = None
                    else:
                        left_quote = token
                case 'LEFT_PARENTHESIS':
                    parenthesis_stack.append(token)
                case 'RIGHT_PARENTHESIS':
                    handle_right('parenthesis', parenthesis_stack, token)
                case 'LEFT_BRACE':
                    brace_stack.append(token)
                case 'RIGHT_BRACE':
                    handle_right('brace', brace_stack, token)
                case 'LEFT_BRACKET':
                    bracket_stack.append(token)
                case 'RIGHT_BRACKET':
                    handle_right('bracket', bracket_stack, token)
        if left_quote:
            raise NameError("unmatched quote")
        if parenthesis_stack:
            raise NameError("unmatched parenthesis")
        if bracket_stack:
            raise NameError("unmatched bracket")
        if brace_stack:
            raise NameError("unmatched brace")

    ##############################################

    def _make_ast(self, level=0):
        print(f"_make_ast {level}")
        self.dump_ast()
        print('<<<')

        def group_tokens(left_token):
            right_token = left_token.right
            ast = Ast()
            ast.parent = self
            ast._left_token = left_token
            ast._right_token = right_token
            # Get inner tokens
            for token in left_token.next.iter_on_chain():
                if token is right_token:
                    break
                ast.append(token)
            # Relink
            if left_token.is_head:
                print("left_token is head")
                ast.parent._head = self
                ast.prev = None
            else:
                print("relink left")
                prev = left_token.prev
                prev.next = ast
                ast.prev = prev
            if right_token.is_last:
                print("right_token is last")
                # print("ast next none")
                ast.next = None
            else:
                print("relink next")
                next_ = right_token.next
                next_.prev = ast
                # print("ast next", next_)
                ast.next = next_
            # Fixme: left_token and right_token are still linked
            # break chain for iter_on_chain
            left_token.next = None
            right_token.prev.next = None
            return ast

        # Fixme: process by hierarchical-position order ?
        for type_ in (
                'LEFT_PARENTHESIS',
                'LEFT_BRACKET',
                'LEFT_BRACE',
                'QUOTE',
        ):
            token = self.head
            while True:
                #print(token)
                if isinstance(token, AstLeaf) and token.is_type(type_):
                    print(f"L{level} found {type_} @{token.position}")
                    ast = group_tokens(token)
                    ast._make_ast(level+1)
                    token = token.right.next
                else:
                    token = token.next
                if token is None:
                    break

        print(f"_make_ast {level} done")

    ##############################################

    def dump_ast(self, indent: int=0):
        indent_str = ' '*4*(indent+1)
        if self._left_token is not None:
            print(f'{indent_str}LEFT: {self._left_token}')
            indent_str += ' '*4
        for node in self.iter_on_chain():
            if isinstance(node, AstLeaf):
                print(indent_str + str(node))
            else:
                node.dump_ast(indent+1)
        if self._right_token is not None:
            indent_str = indent_str[:-2]
            print(f'{indent_str}RIGTH: {self._right_token}')

    ##############################################

    # def walk(self):
    #     for node in self:
    #         if isinstance(node, AstLeaf):
    #             yield node
    #         else:
    #             yield node.walk()

####################################################################################################

class Lexer:

    _logger = _module_logger.getChild('Lexer')

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
    t_ID = r'(?i:[a-z_0-9]+)'    # Fixme:

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
        '''
        p[0] = ('dot_command', p[1], p[2])
        return p[0]

    def p_element(self, p):
        '''statement : ID expression_list_space
        '''
        # Fixme: [a-z]...
        p[0] = ('element', p[1], p[2])
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

    def p_brace(self, p):
        '''expression : LEFT_BRACE expression RIGHT_BRACE
        '''
        p[0] = ('{}', p[2])

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

    def p_function(self, p):
        '''function : ID LEFT_PARENTHESIS expression_list_comma RIGHT_PARENTHESIS
                    | ID LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
        '''
        # | ID LEFT_PARENTHESIS RIGHT_PARENTHESIS
        p[0] = ('function', p[1], p[3])

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
        '''expression : ID SET expression
                      | function SET expression
        '''
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
