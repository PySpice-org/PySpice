import numpy as np
import operator as op


class Expression:
    def __call__(self, **kwargs):
        raise NotImplementedError("The call function is not implemented in class: {}".format(type(self)))

    def __str__(self):
        raise NotImplementedError("The str function is not implemented in class: {}".format(type(self)))

    def __abs__(self, symbol):
        return Abs(symbol)

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __mod__(self, other):
        return Mod(self, other)

    def __pow__(self, other):
        return Power(self, other)

    def __neg__(self):
        return Neg(self)

    def __pos__(self):
        return Pos(self)

    def __lt__(self, other):
        return LT(self, other)

    def __le__(self, other):
        return LE(self, other)

    def __eq__(self, other):
        return EQ(self, other)

    def __ne__(self, other):
        return NE(self, other)

    def __ge__(self, other):
        return GE(self, other)

    def __gt__(self, other):
        return GT(self, other)

    def __not__(self):
        return Not(self)


class Function(Expression):
    nargs = 0

    def __init__(self, func, *symbols):
        self._func = func
        self._symbols = symbols
        if isinstance(self.__class__.nargs, tuple):
            if len(symbols) not in self.__class__.nargs:
                raise ValueError("The number of arguments is not correct: {} != {}".format(
                    len(self._symbols),
                    self.__class__.nargs
                ))
        else:
            if len(symbols) != self.__class__.nargs:
                raise ValueError("The number of arguments is not correct: {} != {}".format(
                    len(self._symbols),
                    self.__class__.nargs
                ))

    def __str__(self):
        arguments = ", ".join([str(symbol) for symbol in self._symbols])
        return "{:s}({:s})".format(self.__class__.__name__.lower(), arguments)

    def __call__(self, **kwargs):
        result = [symbol if isinstance(symbol, (bool, int, float, complex)) else symbol.subs(**kwargs)
                  for symbol in self._symbols]
        expr = [True for element in result
                if isinstance(element, Expression)]
        if len(expr) > 0:
            return self.__class__(*result)
        else:
            return self._func(*result)


class BinaryOperator(Expression):
    def __init__(self, op, string, lhs, rhs):
        self._lhs = lhs
        self._op = op
        self._rhs = rhs
        self._string = string

    def __str__(self):
        return "({:s} {:s} {:s})".format(str(self._lhs), str(self._string), str(self._rhs))

    def __call__(self, **kwargs):
        lhs = self._lhs.subs(**kwargs)
        rhs = self._rhs.subs(**kwargs)
        if isinstance(lhs, Expression) or isinstance(rhs, Expression):
            return self.__class__(lhs, rhs)
        else:
            return self._op(lhs, rhs)


class UnaryOperator(Expression):
    def __init__(self, op, string, operator):
        self._op = op
        self._operator = operator
        self._string = string

    def __str__(self):
        return "({:s}({:s}))".format(str(self._string), str(self._operator))

    def __call__(self, **kwargs):
        operator = self._operator.subs(**kwargs)
        if isinstance(operator, Expression):
            return self.__class__(operator)
        else:
            return self._op(operator)


class Add(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Add, self).__init__(op.add, "+", lhs, rhs)


class Sub(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Sub, self).__init__(op.sub, "-", lhs, rhs)


class Mul(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Mul, self).__init__(op.mul, "*", lhs, rhs)


class Div(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Div, self).__init__(op.truediv, "/", lhs, rhs)


class Mod(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Mod, self).__init__(op.mod, "%", lhs, rhs)


class Power(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Power, self).__init__(op.pow, "**", lhs, rhs)


class Neg(UnaryOperator):
    def __init__(self, operator):
        super(Neg, self).__init__(op.neg, "-", operator)


class Pos(UnaryOperator):
    def __init__(self, operator):
        super(Pos, self).__init__(op.pos, "+", operator)


class LT(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(LT, self).__init__(op.lt, "<", lhs, rhs)


class LE(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(LE, self).__init__(op.le, "<=", lhs, rhs)


class EQ(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(EQ, self).__init__(op.eq, "==", lhs, rhs)


class NE(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(NE, self).__init__(op.ne, "!=", lhs, rhs)


class GE(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(GE, self).__init__(op.ge, ">=", lhs, rhs)


class GT(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(GT, self).__init__(op.gt, ">", lhs, rhs)


class Not(UnaryOperator):
    def __init__(self, operator):
        super(Not, self).__init__(lambda operator: not operator, "not", operator)


class And(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(And, self).__init__(lambda lhs, rhs: lhs and rhs, "and", lhs, rhs)


class Or(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Or, self).__init__(lambda lhs, rhs: lhs or rhs, "or", lhs, rhs)


class Xor(BinaryOperator):
    def __init__(self, lhs, rhs):
        super(Xor, self).__init__(lambda lhs, rhs: lhs != rhs, "xor", lhs, rhs)


class Abs(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Abs, self).__init__(np.abs, *symbol)


class ACos(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ACos, self).__init__(np.arccos, *symbol)


class ACosh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ACosh, self).__init__(np.arccosh, *symbol)


class AGauss(Function):
    nargs = 3

    def __init__(self, *symbol):
        super(AGauss, self).__init__(lambda mu, alpha, n: np.normal(mu,
                                                                    alpha / n,
                                                                    1), *symbol)


class ASin(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ASin, self).__init__(np.arcsin, *symbol)


class ASinh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ASinh, self).__init__(np.arcsinh, *symbol)


class ATan(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ATan, self).__init__(np.arctan, *symbol)


class ATan2(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(ATan2, self).__init__(np.arctan2, *symbol)


class ATanh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(ATanh, self).__init__(np.arctanh, *symbol)


class AUnif(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(AUnif, self).__init__(lambda mu, alpha: np.uniform(mu - alpha,
                                                                 mu + alpha,
                                                                 1), *symbol)


class Ceil(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Ceil, self).__init__(np.ceil, *symbol)


class Cos(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Cos, self).__init__(np.cos, *symbol)


class Cosh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Cosh, self).__init__(np.cosh, *symbol)


class Db(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Db, self).__init__(10*np.log10, *symbol)


class Ddt(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Ddt, self).__init__(np.diff, *symbol)


class Ddx(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Ddx, self).__init__(np.diff, *symbol)


class Exp(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Exp, self).__init__(np.exp, *symbol)


class Floor(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Floor, self).__init__(np.floor, *symbol)


class Gauss(Function):
    nargs = 3

    def __init__(self, *symbol):
        def __init__(self, *symbol):
            super(Gauss, self).__init__(lambda mu, alpha, n: np.normal(mu,
                                                                       alpha * mu / n,
                                                                       1), *symbol)


class If(Function):
    nargs = 3

    def __init__(self, *symbol):
        super(If, self).__init__(lambda t, x, y: x if t else y, *symbol)


class Img(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Img, self).__init__(np.imag, *symbol)


class Int(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Int, self).__init__(int, *symbol)


class Limit(Function):
    nargs = 3

    def __init__(self, *symbol):
        super(Limit, self).__init__(lambda x, y, z: y if x < y else z if x > z else x, *symbol)


class Ln(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Ln, self).__init__(np.log, *symbol)


class Log10(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Log10, self).__init__(np.log10, *symbol)


class M(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(M, self).__init__(np.abs, *symbol)


class Max(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Max, self).__init__(np.max, *symbol)


class Min(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Min, self).__init__(np.min, *symbol)


class NInt(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(NInt, self).__init__(np.round, *symbol)


class Ph(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Ph, self).__init__(np.angle, *symbol)


class Pow(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Pow, self).__init__(lambda x, y: np.power(x, y), *symbol)


class Pwr(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Pwr, self).__init__(lambda x, y: np.power(x, y), *symbol)


class Pwrs(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Pwrs, self).__init__(lambda x, y: np.copysign(np.power(np.abs(x), y), x), *symbol)


class Rand(Function):
    nargs = 0

    def __init__(self, *symbol):
        super(Rand, self).__init__(np.random.rand(1), *symbol)


class Re(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Re, self).__init__(np.real, *symbol)


class Sdt(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Sdt, self).__init__(np.trapz, *symbol)


class Sgn(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Sgn, self).__init__(np.sign, *symbol)


class Sign(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Sign, self).__init__(np.copysign, *symbol)


class Sin(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Sin, self).__init__(np.sin, *symbol)


class Sinh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Sinh, self).__init__(np.sinh, *symbol)


class Sqrt(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Sqrt, self).__init__(np.sqrt, *symbol)


class Stp(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Stp, self).__init__(lambda x: x * (x > 0), *symbol)


class Tan(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Tan, self).__init__(np.arctan, *symbol)


class Tanh(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(Tanh, self).__init__(np.cosh, *symbol)


class Unif(Function):
    nargs = 2

    def __init__(self, *symbol):
        super(Unif, self).__init__(lambda mu, alpha: np.uniform(mu * (1. - alpha),
                                                                mu * (1. + alpha),
                                                                1), *symbol)


class URamp(Function):
    nargs = 1

    def __init__(self, *symbol):
        super(URamp, self).__init__(lambda x: x * (x > 0), *symbol)


class Symbol(Expression):
    def __init__(self, name):
        self._name = str(name)

    def __str__(self):
        return self._name

    def subs(self, **kwargs):
        if self._name in kwargs:
            return kwargs[self._name]
        else:
            return self


class I(Symbol):
    nargs = 1

    def __init__(self, device):
        super(I, self).__init__("i({:s})".format(device))


class V(Symbol):
    nargs = (1, 2)

    def __init__(self, *nodes):
        if len(nodes) not in self.__class__.nargs:
            ValueError("Only 1 or two nodes allowed.")
        string = ""
        if len(nodes) == 1:
            string = "v({:s})".format(str(nodes[0]))
        else:
            string = "v({:s}, {:s})".format(str(nodes[0]),
                                            str(nodes[1]))
        super(V, self).__init__(string)


class Table(Symbol):
    def __init__(self, expression, points):
        self._expression = expression
        self._points = points
        string = "table: {{{}}} = {}".format(self._expression,
                                             " ".join(["({}, {})".format(*point)
                                                       for point in self._points]))
        super(Table, self).__init__(string)


class TableFile(Symbol):
    def __init__(self, filename):
        self._filename = filename
        string = "tablefile({})".format(self._filename)
        super(TableFile, self).__init__(string)
