####################################################################################################
# 
# PySpice - A Spice package for Python
# Copyright (C) Salvaire Fabrice 2014
# 
####################################################################################################

####################################################################################################

import numbers
import math

####################################################################################################

class Unit(numbers.Real):

    __scale__ = 1.
    __spice_suffix__ = ''
    __unit_suffix__ = ''

    ##############################################

    def __init__(self, value):

        if isinstance(value, Unit):
            if self.__scale__ == value.__scale__:
                self._value = value._value
            else:
                self._value =  float(value) / self.__scale__
        elif isinstance(value, int):
            self._value =  value # to keep as int
        else:
            self._value = float(value)

    ##############################################

    @property
    def value(self):
        return self._value

    ##############################################

    def clone(self):
        return self.__class__(self._value)

    ##############################################

    def convert_value(self, other):

        if isinstance(other, Unit) and self.__scale__ == other.__scale__:
            return other._value
        else:
            return float(other) / self.__scale__

    ##############################################

    def convert(self, other):
        
        return self.__class__(self.convert_value(other))

    ##############################################

    def __float__(self):
        return self._value * self.__scale__

    ##############################################

    def __str__(self):
        return str(self._value) + self.__spice_suffix__

    ##############################################

    def __nonzero__(self):
        """True if self != 0. Called for bool(self)."""
        return self._value != 0

    ##############################################

    def __add__(self, other):
        """self + other"""
        new_obj = self.clone()
        new_obj._value += self.convert_value(other)
        return new_obj

    ##############################################

    def __radd__(self, other):
        """other + self"""
        return other.__add__(self)

    ##############################################

    def __neg__(self):
        """-self"""
        return self.__class__(-self._value)

    ##############################################

    def __pos__(self):
        """+self"""
        return self.clone()

    ##############################################

    def __sub__(self, other):
        """self - other"""
        new_obj = self.clone()
        new_obj._value -= self.convert_value(other)
        return new_obj

    ##############################################

    def __rsub__(self, other):
        """other - self"""
        return other.__sub__(self)

    ##############################################

    def __mul__(self, other):
        """self * other"""
        new_obj = self.clone()
        new_obj._value *= self.convert_value(other)
        return new_obj

    ##############################################

    def __rmul__(self, other):
        """other * self"""
        return other.__mul__(self)

    ##############################################

    def __div__(self, other):
        """self / other without __future__ division

        May promote to float.
        """
        new_obj = self.clone()
        new_obj._value /= self.convert_value(other)
        return new_obj

    ##############################################

    def __rdiv__(self, other):
        """other / self without __future__ division"""
        return other.__div__(self)

    ##############################################

    def __truediv__(self, other):
        """self / other with __future__ division.

        Should promote to float when necessary.
        """
        raise NotImplementedError

    ##############################################

    def __rtruediv__(self, other):
        """other / self with __future__ division"""
        raise NotImplementedError

    ##############################################

    def __pow__(self, exponent):
        """self**exponent; should promote to float or complex when necessary."""
        new_obj = self.clone()
        new_obj._value**=exponent
        return new_obj

    ##############################################

    def __rpow__(self, base):
        """base ** self"""
        raise NotImplementedError

    ##############################################

    def __abs__(self):
        """Returns the Real distance from 0. Called for abs(self)."""
        return self.__class__(abs(self._value))

    ##############################################

    def __eq__(self, other):
        """self == other"""
        return float(self) == float(other)

    ##############################################

    def __ne__(self, other):
        """self != other"""
        # The default __ne__ doesn't negate __eq__ until 3.0.
        return not (self == other)

    ##############################################

    def __trunc__(self):
        """trunc(self): Truncates self to an Integral.

        Returns an Integral i such that:
          * i>0 iff self>0;
          * abs(i) <= abs(self);
          * for any Integral j satisfying the first two conditions,
            abs(i) >= abs(j) [i.e. i has "maximal" abs among those].
        i.e. "truncate towards 0".
        """
        raise NotImplementedError

    ##############################################

    def __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        return (self // other, self % other)

    ##############################################

    def __rdivmod__(self, other):
        """divmod(other, self): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        return (other // self, other % self)

    ##############################################

    def __floordiv__(self, other):
        """self // other: The floor() of self/other."""
        raise NotImplementedError

    ##############################################

    def __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
        raise NotImplementedError

    ##############################################

    def __mod__(self, other):
        """self % other"""
        raise NotImplementedError

    ##############################################

    def __rmod__(self, other):
        """other % self"""
        raise NotImplementedError

    ##############################################

    def __lt__(self, other):
        """self < other

        < on Reals defines a total ordering, except perhaps for NaN."""
        return float(self) < float(other)

    ##############################################

    def __le__(self, other):
        """self <= other"""
        return float(self) <= float(other)

    ##############################################

    def inverse(self, the_class=None):

        inverse = 1. / float(self)
        if the_class is None:
            return self.__class__(inverse / self.__scale__) # Fixme: to func?
        else:
            return the_class(inverse)

####################################################################################################

class tera(Unit):
    """ T Tera 1e12 """
    __scale__ = 1e12
    __spice_suffix__ = 'T'

class giga(Unit):
    """ G Giga 1e9 """
    __scale__ = 1e9
    __spice_suffix__ = 'G'

class mega(Unit):
    """ Meg Mega 1e6 """
    __scale__ = 1e6
    __spice_suffix__ = 'Meg'

class kilo(Unit):
    """ K Kilo 1e3 """
    __scale__ = 1e3
    __spice_suffix__ = 'k'

class mil(Unit):
    """ mil Mil 25.4e-6 """
    __scale__ = 25.4e-6
    __spice_suffix__ = 'mil'

class milli(Unit):
    """ m milli 1e-3 """
    __scale__ = 1e-3
    __spice_suffix__ = 'm'

class micro(Unit):
    """ u micro 1e-6 """
    __scale__ = 1e-6
    __spice_suffix__ = 'u'

class nano(Unit):
    """ n nano 1e-9 """
    __scale__ = 1e-9
    __spice_suffix__ = 'n'

class pico(Unit):
    """ p pico 1e-12 """
    __scale__ = 1e-12
    __spice_suffix__ = 'p'

class femto(Unit):
    """ f femto 1e-15 """
    __scale__ = 1e-15
    __spice_suffix__ = 'f'

####################################################################################################

class Frequency(Unit):

    ##############################################

    @property
    def period(self):
        return self.inverse(Period)

    ##############################################

    @property
    def pulsation(self):
        return self * 2 * math.pi

####################################################################################################

class Period(Unit):

    ##############################################

    @property
    def frequency(self):
        return self.inverse(Frequency)

    ##############################################

    @property
    def pulsation(self):
        return self.frequency.pulsation

####################################################################################################
# 
# End
# 
####################################################################################################
