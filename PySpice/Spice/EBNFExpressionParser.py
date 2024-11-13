import logging
import os
import csv

from unicodedata import normalize
from PySpice.Unit.Unit import UnitValue, ZeroPower, PrefixedUnit, UnitMetaclass, UnitPrefixMetaclass
from PySpice.Unit.SiUnits import Tera, Giga, Mega, Kilo, Milli, Micro, Nano, Pico, Femto
from PySpice.Tools.StringTools import join_lines
from .Expressions import *

from .ExpressionGrammar import ExpressionParser as parser
from .ExpressionModel import ExpressionModelBuilderSemantics
from tatsu import to_python_sourcecode, to_python_model, compile
from tatsu.model import NodeWalker

_module_logger = logging.getLogger(__name__)


class ParseError(NameError):
    pass


class Statement:
    """ This class implements a statement, in fact a line in a Spice netlist. """

    @staticmethod
    def arg_to_python(x):

        if x:
            if str(x)[0].isdigit():
                return str(x)
            else:
                return "'{}'".format(x)
        else:
            return ''

    @staticmethod
    def args_to_python(*args):

        return [Statement.arg_to_python(x) for x in args]

    @staticmethod
    def kwargs_to_python(self, **kwargs):
        return Statement.join_args(*['{}={}'.format(key, self.value_to_python(value))
                                     for key, value in kwargs.items()])

    @staticmethod
    def join_args(self, *args):
        return ', '.join(args)


class ExpressionModelWalker(NodeWalker):

    def __init__(self):
        self._scales = (Tera(), Giga(), Mega(), Kilo(), Milli(), Micro(), Nano(), Pico(), Femto())
        self._suffix = dict([(normalize("NFKD", unit.prefix).lower(), PrefixedUnit(power=unit))
                             for unit in self._scales] +
                            [(normalize("NFKD", unit.spice_prefix).lower(), PrefixedUnit(power=unit))
                             for unit in self._scales
                             if unit.spice_prefix is not None]
                            )
        self._functions = {"abs": Abs,
                           "agauss": AGauss,
                           "acos": ACos,
                           "acosh": ACosh,
                           "arctan": ATan,
                           "asin": ASin,
                           "asinh": ASinh,
                           "atan": ATan,
                           "atan2": ATan2,
                           "atanh": ATanh,
                           "aunif": AUnif,
                           "ceil": Ceil,
                           "cos": Cos,
                           "cosh": Cosh,
                           "db": Db,
                           "ddt": Ddt,
                           "ddx": Ddx,
                           "exp": Exp,
                           "ln": Ln,
                           "log": Ln,
                           "log10": Log10,
                           "floor": Floor,
                           "gauss": Gauss,
                           "i": I,
                           "if": If,
                           "img": Img,
                           "int": Int,
                           "limit": Limit,
                           "m": M,
                           "max": Max,
                           "min": Min,
                           "nint": NInt,
                           "ph": Ph,
                           "pow": Pow,
                           "pwr": Pow,
                           "pwrs": Pwrs,
                           "r": Re,
                           "rand": Rand,
                           "re": Re,
                           "sdt": Sdt,
                           "sgn": Sgn,
                           "sign": Sign,
                           "sin": Sin,
                           "sinh": Sinh,
                           "sqrt": Sqrt,
                           "stp": Stp,
                           "tan": Tan,
                           "tanh": Tanh,
                           "unif": Unif,
                           "uramp": URamp,
                           "v": V
                           }
        self._relational = {
            "<": LT,
            "<=": LE,
            "==": EQ,
            "!=": NE,
            ">=": GE,
            ">": GT
        }

    def walk_SpiceExpression(self, node, data):
        return self.walk(node.ast, data)

    def walk_GenericExpression(self, node, data):
        if node.value is None:
            return self.walk(node.braced, data)
        else:
            return self.walk(node.value, data)

    def walk_BracedExpression(self, node, data):
        return self.walk(node.ast, data)

    def walk_Ternary(self, node, data):
        t = self.walk(node.t, data)
        x = self.walk(node.x, data)
        y = self.walk(node.y, data)
        return self._functions["if"](t, x, y)

    def walk_Conditional(self, node, data):
        return self.walk(node.expr, data)

    def walk_And(self, node, data):
        left = self.walk(node.left, data)
        if node.right is None:
            return left
        else:
            right = self.walk(node.right, data)
            return And(left, right)

    def walk_Not(self, node, data):
        operator = self.walk(node.operator, data)
        if node.op is None:
            return operator
        else:
            return Not(operator)

    def walk_Or(self, node, data):
        left = self.walk(node.left, data)
        if node.right is None:
            return left
        else:
            right = self.walk(node.right, data)
            return Or(left, right)

    def walk_Xor(self, node, data):
        left = self.walk(node.left, data)
        if node.right is None:
            return left
        else:
            right = self.walk(node.right, data)
            return Xor(left, right)

    def walk_Relational(self, node, data):
        if node.factor is None:
            left = self.walk(node.left, data)
            right = self.walk(node.right, data)
            return self._relational[node.op](left, right)
        else:
            return self.walk(node.factor, data)

    def walk_ConditionalFactor(self, node, data):
        if node.boolean is None:
            return self.walk(node.expr, data)
        else:
            return node.boolean.lower() == "true"

    def walk_Expression(self, node, data):
        if node.term is None:
            return self.walk(node.ternary, data)
        else:
            return self.walk(node.term, data)

    def walk_Functional(self, node, data):
        return self.walk(node.ast, data)

    def walk_Functions(self, node, data):
        l_func = node.func.lower()
        function = self._functions[l_func]
        if function.nargs == 0:
            return function()
        elif l_func == 'v':
            nodes = self.walk(node.node, data)
            if isinstance(nodes, list):
                return function(*nodes)
            else:
                return function(nodes)
        elif l_func == 'i':
            device = self.walk(node.device, data)
            return function(device)
        elif function.nargs == 1:
            x = self.walk(node.x, data)
            return function(x)
        elif l_func == 'limit':
            x = self.walk(node.x, data)
            y = self.walk(node.y, data)
            z = self.walk(node.z, data)
            return function(x, y, z)
        elif l_func == 'atan2':
            x = self.walk(node.x, data)
            y = self.walk(node.y, data)
            return function(y, x)
        elif l_func in ('aunif', 'unif'):
            mu = self.walk(node.mu, data)
            alpha = self.walk(node.alpha, data)
            return function(mu, alpha)
        elif l_func == "ddx":
            f = node.f
            x = self.walk(node.x, data)
            return function(Symbol(f), x)
        elif function.nargs == 2:
            x = self.walk(node.x, data)
            y = self.walk(node.y, data)
            return function(x, y)
        elif l_func == "if":
            t = self.walk(node.t, data)
            x = self.walk(node.x, data)
            y = self.walk(node.y, data)
            return function(t, x, y)
        elif l_func == "limit":
            x = self.walk(node.x, data)
            y = self.walk(node.y, data)
            z = self.walk(node.z, data)
            return function(x, y, z)
        elif l_func in ('agauss', 'gauss'):
            mu = self.walk(node.mu, data)
            alpha = self.walk(node.alpha, data)
            n = self.walk(node.n, data)
            return function(mu, alpha, n)
        else:
            raise NotImplementedError("Function: {}".format(node.func));

    def walk_Term(self, node, data):
        return self.walk(node.ast, data)

    def walk_AddSub(self, node, data):
        lhs = self.walk(node.left, data)
        if node.right is not None:
            rhs = self.walk(node.right, data)
            if node.op == "+":
                return Add(lhs, rhs)
            else:
                return Sub(lhs, rhs)
        else:
            return lhs

    def walk_ProdDivMod(self, node, data):
        lhs = self.walk(node.left, data)
        if node.right is not None:
            rhs = self.walk(node.right, data)
            if node.op == "*":
                return Mul(lhs, rhs)
            elif node.op == "/":
                return Div(lhs, rhs)
            else:
                return Mod(lhs, rhs)
        else:
            return lhs

    def walk_Sign(self, node, data):
        operator = self.walk(node.operator, data)
        if node.op is not None:
            if node.op == "-":
                if isinstance(operator, (int, float)):
                    return -operator
                else:
                    return Neg(operator)
            else:
                if not isinstance(operator, (int, float)):
                    return Pos(operator)
        return operator

    def walk_Exponential(self, node, data):
        lhs = self.walk(node.left, data)
        if node.right is not None:
            rhs = self.walk(node.right, data)
            return Power(lhs, rhs)
        else:
            return lhs

    def walk_Factor(self, node, data):
        return self.walk(node.ast, data)

    def walk_Variable(self, node, data):
        if node.variable is None:
            return self.walk(node.factor, data)
        else:
            return Symbol(node.variable)

    def walk_Value(self, node, data):
        real = 0.0
        if node.real is not None:
            real = self.walk(node.real, data)
        imag = None
        if node.imag is not None:
            imag = self.walk(node.imag, data)
        value = 0.0
        if imag is None:
            value = real
        else:
            value = complex(float(real), float(imag))
        if node.unit is not None:
            unit = self.walk(node.unit, data)
            if type(unit) is not str:
                if not isinstance(value, UnitValue):
                    value = PrefixedUnit.from_si_unit(unit.si_unit).new_value(value)
                else:
                    value = PrefixedUnit.from_prefixed_unit(unit, value.power).new_value(value.value)
        return value

    def walk_ImagValue(self, node, data):
        return self.walk(node.value, data)

    def walk_RealValue(self, node, data):
        return self.walk(node.value, data)

    def walk_NumberScale(self, node, data):
        value = ExpressionModelWalker._to_number(self.walk(node.value, data))
        scale = node.scale
        if scale is not None:
            scale = normalize("NFKD", scale).lower()
            value = PrefixedUnit(power=UnitPrefixMetaclass.get(scale)).new_value(value)
        return value

    def walk_Float(self, node, data):
        value = ExpressionModelWalker._to_number(node.ast)
        return value

    def walk_Int(self, node, data):
        value = int(node.ast)
        return value

    def walk_Unit(self, node, data):
        unit = UnitMetaclass.from_prefix(node.ast.lower())
        if unit is None:
            unit = node.ast
        return unit

    def walk_Hz(self, node, data):
        return UnitMetaclass.from_prefix(node.ast.lower())

    def walk_Comment(self, node, data):
        # TODO implement comments on devices
        return node.ast

    def walk_Separator(self, node, data):
        if node.comment is not None:
            return self.walk(node.comment, data)

    def walk_NetNode(self, node, data):
        return node.node

    def walk_Filename(self, node, data):
        return node.ast

    def walk_BinaryPattern(self, node, data):
        return ''.join(node.pattern)

    def walk_closure(self, node, data):
        return ''.join(node)

    def walk_list(self, node, data):
        return [self.walk(e, data) for e in iter(node)]

    def walk_object(self, node, data):
        raise ParseError("No walker defined for the node: {}".format(node))

    @staticmethod
    def _to_number(value):
        if type(value) is tuple:
            value = value[0]
        try:
            int_value = int(value)
            float_value = float(value)
            if int_value == float_value:
                return int_value
            else:
                return float_value
        except ValueError:
            return float(value)


class ParsingData:
    def __init__(self):
        self._root = None
        self._present = None
        self._context = []


class ExpressionParser:
    """ This class parse a Spice netlist file and build a syntax tree.

    Public Attributes:

      :attr:`circuit`

      :attr:`models`

      :attr:`subcircuits`

    """

    _logger = _module_logger.getChild('ExpressionParser')

    ##############################################

    _parser = parser(whitespace='', semantics=ExpressionModelBuilderSemantics())
    _walker = ExpressionModelWalker()

    def __init__(self):
        pass

    @staticmethod
    def parse(source=None):
        # Fixme: empty source

        if source is not None:
            raw_code = source
        else:
            raise ValueError("No path or source")

        try:
            model = ExpressionParser._parser.parse(raw_code)
        except Exception as e:
            raise ParseError(str(e)) from e

        data = ParsingData()
        expr = ExpressionParser._walker.walk(model, data)
        return expr

    @staticmethod
    def _regenerate():
        from PySpice.Spice import __file__ as spice_file
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(spice_file)))
        grammar_file = os.path.join(location, "expressiongrammar.ebnf")
        with open(grammar_file, "r") as grammar_ifile:
            grammar = grammar_ifile.read();
        with open(grammar_file, "w") as grammar_ofile:
            model = compile(str(grammar))
            grammar_ofile.write(str(model))
        python_file = os.path.join(location, "ExpressionGrammar.py")
        python_grammar = to_python_sourcecode(grammar)
        with open(python_file, 'w') as grammar_ofile:
            grammar_ofile.write(python_grammar)
        python_model = to_python_model(grammar)
        model_file = os.path.join(location, "ExpressionModel.py")
        with open(model_file, 'w') as model_ofile:
            model_ofile.write(python_model)
