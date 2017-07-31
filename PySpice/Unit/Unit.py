####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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

####################################################################################################

"""This module implements units.

A shortcut is defined for each unit prefix, e.g. :class:`pico`, :class:`nano`, :class:`micro`,
:class:`milli`, :class:`kilo`, :class:`mega`, :class:`tera`.

"""

####################################################################################################

import logging

import math
# import numbers
import types

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class UnitPrefixMetaclass(type):

    """Metaclass to register unit prefixes"""

    __prefixes__ = {}

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):

        cls = type.__new__(meta, class_name, base_classes, attributes)
        if class_name != 'UnitPrefix':
            meta.register_prefix(cls)
        return cls

    ##############################################

    @classmethod
    def register_prefix(meta, cls):

        power = cls.__power__
        if power is None:
            raise ValueError('Power is None for {}'.format(cls.__name__))
        meta.__prefixes__[power] = cls

    ##############################################

    @classmethod
    def prefix_iter(cls):
        return cls.__prefixes__.values()

####################################################################################################

class UnitPrefix(metaclass=UnitPrefixMetaclass):

    """This class implements a unit prefix like kilo"""

    __power__ = None
    __prefix__ = ''

    ##############################################

    def __int__(self):
        return self.__power__

    ##############################################

    def __str__(self):
        return self.__prefix__

    ##############################################

    @property
    def power(self):
        return self.__power__

    @property
    def prefix(self):
        return self.__prefix__

    @property
    def is_unit(self):
        return self.__power__ == 0

    @property
    def scale(self):
        return 10**self.__power__

    ##############################################

    @property
    def spice_prefix(self):

        if hasattr(self, '__spice_prefix__'):
            return self.__spice_prefix__
        else:
            return self.__prefix__

    ##############################################

    def __eq__(self, other):

        return self.__power__ == other.__power__

    ##############################################

    def __ne__(self, other):

        return self.__power__ != other.__power__

    ##############################################

    def __lt__(self, other):

        return self.__power__ < other.__power__

    ##############################################

    def __gt__(self, other):

        return self.__power__ > other.__power__

####################################################################################################

# Define SI unit prefixes

class Yotta(UnitPrefix):
    __power__ = 24
    __prefix__ = 'Y'
    __spice_prefix__ = None

class Zetta(UnitPrefix):
    __power__ = 21
    __prefix__ = 'Z'
    __spice_prefix__ = None

class Exa(UnitPrefix):
    __power__ = 12
    __prefix__ = 'E'
    __spice_prefix__ = None

class Peta(UnitPrefix):
    __power__ = 15
    __prefix__ = 'P'
    __spice_prefix__ = None

class Tera(UnitPrefix):
    __power__ = 12
    __prefix__ = 'T'

class Giga(UnitPrefix):
    __power__ = 9
    __prefix__ = 'G'

class Mega(UnitPrefix):
    __power__ = 6
    __prefix__ = 'M'
    __spice_prefix__ = 'Meg'

class Kilo(UnitPrefix):
    __power__ = 3
    __prefix__ = 'k'

class Hecto(UnitPrefix):
    __power__ = 2
    __prefix__ = 'h'
    __spice_prefix__ = None

class Deca(UnitPrefix):
    __power__ = 1
    __prefix__ = 'da'
    __spice_prefix__ = None

class ZeroPower(UnitPrefix):
    __power__ = 0
    __prefix__ = ''
    __spice_prefix__ = ''

class Milli(UnitPrefix):
    __power__ = -3
    __prefix__ = 'm'

class Micro(UnitPrefix):
    __power__ = -6
    __prefix__ = 'μ'
    __spice_prefix__ = 'u'

class Nano(UnitPrefix):
    __power__ = -9
    __prefix__ = 'n'

class Pico(UnitPrefix):
    __power__ = -12
    __prefix__ = 'p'

class Femto(UnitPrefix):
    __power__ = -15
    __prefix__ = 'f'
    __spice_prefix__ = None

class Atto(UnitPrefix):
    __power__ = -18
    __prefix__ = 'a'
    __spice_prefix__ = None

class Zepto(UnitPrefix):
    __power__ = -21
    __prefix__ = 'z'
    __spice_prefix__ = None

class Yocto(UnitPrefix):
    __power__ = -24
    __prefix__ = 'y'
    __spice_prefix__ = None

# Fixme: ngspice defines mil

####################################################################################################

class SiDerivedUnit:

    """This class implements an unit based on SI units"""

    # SI units
    __units__ = (
        'm',
        'kg',
        's',
        'A',
        'K',
        'mol',
        'cd',
    )

    ##############################################

    def __init__(self, string=None, power=None):

        if power is not None:
            self._power = self.new_power()
            self._power.update(power)
        elif string is not None:
            self._power = self.parse_si(string)
        else:
            self._power = self.new_power()

        self._hash = self.to_hash(self._power)
        self._string = self.to_string(self._power)

    ##############################################

    @property
    def power(self):
        return self._power

    @property
    def hash(self):
        return self._hash

    @property
    def string(self):
        return self._string

    def __str__(self):
        return self._string

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._string)

    ##############################################

    @classmethod
    def new_power(cls):
        return {unit: 0 for unit in cls.__units__}

    ##############################################

    @classmethod
    def parse_si(cls, string):

        si_power = cls.new_power()
        if string:
            for unit_power in string.split('*'):
                parts = unit_power.split('^')
                unit = parts[0]
                if len(parts) == 1:
                    power = 1
                else:
                    power = int(parts[1])
                si_power[unit] += power
        return si_power

    ##############################################

    @classmethod
    def to_hash(cls, power):

        hash_ = ''
        for unit in cls.__units__:
            hash_ += str(power[unit])
        return hash_

    ##############################################

    @classmethod
    def to_string(cls, si_power):

        units = []
        for unit in cls.__units__:
            power = si_power[unit]
            if power == 1:
                units.append(unit)
            elif power > 1 or power < 0:
                units.append('{}^{}'.format(unit, power))
        return '*'.join(units)

    ##############################################

    def is_base_unit(self):

        count = 0
        for power in self._power.values():
            if power == 1:
                count += 1
            elif power != 0:
                return False
        return count == 1

    ##############################################

    def is_anonymous(self):

        return self._hash == '0'*len(self.__units__)

    ##############################################

    def __bool__(self):

        return not self.is_anonymous()

    ##############################################

    def clone(self):

        return self.__class__(power=self._power)

    ##############################################

    def __eq__(self, other):

        return self._hash == other._hash

    ##############################################

    def __ne__(self, other):

        return self._hash != other._hash

    ##############################################

    def __mul__(self, other):

        power = {unit: self._power[unit] + other._power[unit]
                 for unit in self.__units__}
        return self.__class__(power=power)

    ##############################################

    def __imul__(self, other):

        for unit in self.__units__:
            self._power[unit] += other.power[unit]
        self._hash = self.to_hash(self._power)
        self._string = self.to_string(self._power)

        return self

    ##############################################

    def __truediv__(self, other):

        power = {unit: self._power[unit] - other._power[unit]
                 for unit in self.__units__}
        return self.__class__(power=power)

    ##############################################

    def __itruediv__(self, other):

        for unit in self.__units__:
            self._power[unit] -= other.power[unit]
        self._hash = self.to_hash(self._power)
        self._string = self.to_string(self._power)

        return self

    ##############################################

    def inverse(self):

        power = {unit: -self._power[unit]
                    for unit in self.__units__}
        return self.__class__(power=power)

####################################################################################################

class UnitMetaclass(type):

    """Metaclass to register units"""

    __units__ = {}
    __hash_map__ = {}

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):

        cls = type.__new__(meta, class_name, base_classes, attributes)
        meta.init_unit(cls)
        meta.register_unit(cls)
        return cls

    ##############################################

    @classmethod
    def init_unit(meta, cls):

        si_unit = cls.__si_unit__
        if not (isinstance(si_unit, SiDerivedUnit) and si_unit):
            # si_unit is not defined
            if cls.is_base_unit():
                si_unit = SiDerivedUnit(cls.__unit_suffix__)
            else: # str
                si_unit = SiDerivedUnit(si_unit)
            cls.__si_unit__  = si_unit

    ##############################################

    @classmethod
    def register_unit(meta, cls):

        meta.__units__[cls.__unit_suffix__] = cls

        if cls.__si_unit__ and cls.__power__.is_unit:
            hash_ = cls.__si_unit__.hash
            if hash_ in meta.__hash_map__:
                meta.__hash_map__[hash_].append(cls)
            else:
                meta.__hash_map__[hash_] = [cls]

    ##############################################

    @classmethod
    def unit_iter(meta):
        return meta.__units__.values()

    ##############################################

    @classmethod
    def from_prefix(meta, prefix):
        return meta._units__.get(prefix, None)

    ##############################################

    @classmethod
    def from_hash(meta, hash_):
        return meta.__hash_map__.get(hash_, None)

    ##############################################

    @classmethod
    def from_si_unit(meta, si_unit, unique=True):

        units = meta.__hash_map__.get(si_unit.hash, None)
        if unique and units is not None:
            if len(units) > 1:
                units = [unit for unit in units if unit.is_default_unit()]
                if len(units) == 1:
                    return units[0]
                else:
                    raise NameError("Unit clash", units)
            else:
                return units[0]
        else:
            return units

####################################################################################################

class UnitError(ValueError):
    pass

####################################################################################################

class Unit(metaclass=UnitMetaclass): # numbers.Real,

    """This class implements a value with an unit and a power (prefix).

    The value is not converted to float if the value is an int.
    """

    __unit_name__ = ''
    __unit_suffix__ = ''
    __quantity__ = ''
    __si_unit__ = SiDerivedUnit()
    __power__ = ZeroPower()
    __default_unit__ = False
    # __spice_suffix__ = ''

    _logger = _module_logger.getChild('Unit')

    ##############################################

    def __init__(self, value, si_unit=None, power=None):

        self._unit_name = self.__unit_name__
        self._unit_suffix = self.__unit_suffix__
        self._quantity = self.__quantity__

        if si_unit is None:
            self._si_unit = self.__si_unit__
        else:
            self._si_unit = si_unit
        # print('Unit ctor', self.__class__.__name__, self._unit_suffix, ':', self._si_unit)

        if power is None:
            self._power = self.__power__
        else:
            self._power = power

        if isinstance(value, Unit):
            if self.is_same_power(value):
                self._value = value.value
            else:
                self._value =  float(value) / self.scale
        elif isinstance(value, int):
            self._value = value # to keep as int
        else:
            self._value = float(value)

    ##############################################

    def __repr__(self):

        return '{0}({1})'.format(self.__class__.__name__, str(self))

    ##############################################

    @classmethod
    def is_default_unit(cls):
        return cls.__default_unit__

    ##############################################

    @property
    def unit_name(self):
        return self._unit_name

    @property
    def unit_suffix(self):
        return self._unit_suffix

    @property
    def quantity(self):
        return self._quantity

    @property
    def si_unit(self):
        return self._si_unit

    @property
    def power(self):
        return self._unit_suffix

    ##############################################

    @property
    def scale(self):
        return self._power.scale

    ##############################################

    @property
    def value(self):
        return self._value

    ##############################################

    def clone(self):
        return self.__class__(self._value)

    ##############################################

    @classmethod
    def is_base_unit(cls):
        return False

    ##############################################

    def is_same_unit(self, other):

        return self._si_unit == other.si_unit

    ##############################################

    def _check_unit(self, other):

        if not self.is_same_unit(other):
            raise UnitError

    ##############################################

    def is_same_power(self, other):

        # isinstance(other, Unit) and
        return self._power == other._power

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

    def convert_value(self, other):

        self._check_unit(other)
        if self.is_same_power(other):
            return other._value
        else:
            return float(other) / self.scale

    ##############################################

    def convert(self, other):

        return self.__class__(self.convert_value(other))

    ##############################################

    def __int__(self):

        return int(self._value * self.scale)

    ##############################################

    def __float__(self):

        return float(self._value * self.scale)

    ##############################################

    def str(self, spice=False, space=False, unit=True):

        string = str(self._value)
        if space:
            string += ' '
        string += self._power.spice_prefix if spice else self._power.prefix
        if unit:
            if self._unit_suffix:
                string += self._unit_suffix
            else:
                string += str(self._si_unit)
        return string

    ##############################################

    def str_space(self):
        return self.str(space=True)

    ##############################################

    def str_spice(self):

        # Ngspice User Manual Section 2.3.1  Some naming conventions
        #
        # Letters immediately following a number that are not scale factors are ignored, and letters
        # im- mediately following a scale factor are ignored. Hence, 10, 10V, 10Volts, and 10Hz all
        # represent the same number, and M, MA, MSec, and MMhos all represent the same scale
        # factor. Note that 1000, 1000.0, 1000Hz, 1e3, 1.0e3, 1kHz, and 1k all represent the same
        # number. Note that M or m denote ’milli’, i.e. 10−3 . Suffix meg has to be used for 106 .

        # Fixme: unit clash, e.g. mm ???

        string = self.str(spice=True, space=False, unit=True)
        # Ngspice don't support utf-8
        string = string.replace('Ω', 'Ohm') # utf-8 cea0
        string = string.replace('μ',   'u') # utf-8 cebc
        return string

    ##############################################

    def __str__(self):

        return self.str(spice=False, space=True, unit=True)

    ##############################################

    def __bool__(self):

        """True if self != 0. Called for bool(self)."""

        return self._value != 0

    ##############################################

    def __add__(self, other):

        """self + other"""

        self._check_unit(other)
        new_obj = self.clone()
        new_obj._value += self.convert_value(other)
        return new_obj

    ##############################################

    def __iadd__(self, other):

        """self += other"""

        self._check_unit(other)
        self._value += self.convert_value(other)
        return self

    ##############################################

    def __radd__(self, other):

        """other + self"""

        raise float(self) + other

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

        self._check_unit(other)
        new_obj = self.clone()
        new_obj._value -= self.convert_value(other)
        return new_obj

    ##############################################

    def __isub__(self, other):

        """self -= other"""

        self._check_unit(other)
        self._value -= self.convert_value(other)
        return self

    ##############################################

    def __rsub__(self, other):

        """other - self"""

        raise other - float(self)

    ##############################################

    def __mul__(self, other):

        """self * other"""

        if (isinstance(other, Unit)):
            si_unit = self.si_unit * other.si_unit
            equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
            value = float(self) * float(other)
            if equivalent_unit is not None:
                return equivalent_unit(value)
            else:
                return Unit(value, si_unit=si_unit)
        else: # scale value
            new_obj = self.clone()
            new_obj._value *= float(other)
            return new_obj

    ##############################################

    def __imul__(self, other):

        """self *= other"""

        if (isinstance(other, Unit)):
            raise UnitError
        else: # scale value
            # Fixme: right ?
            self._value *= self.convert_value(other)
            return self

    ##############################################

    def __rmul__(self, other):

        """other * self"""

        if (isinstance(other, Unit)):
            raise NotImplementedError # Fixme: when ???
        else: # scale value
            return self.__mul__(other)

    ##############################################

    def __floordiv__(self, other):

        """self // other """

        if (isinstance(other, Unit)):
            si_unit = self.si_unit / other.si_unit
            equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
            value = float(self) // float(other)
            if equivalent_unit is not None:
                return equivalent_unit(value)
            else:
                return Unit(value, si_unit=si_unit)
        else: # scale value
            new_obj = self.clone()
            new_obj._value //= float(other)
            return new_obj

    ##############################################

    def __ifloordiv__(self, other):

        """self //= other """

        if (isinstance(other, Unit)):
            raise NotImplementedError
        else: # scale value
            self._value //= float(other)
            return self

    ##############################################

    def __rfloordiv__(self, other):

        """other // self"""

        if (isinstance(other, Unit)):
            raise NotImplementedError # Fixme: when ???
        else: # scale value
            return other // float(self)

    ##############################################

    def __truediv__(self, other):

        """self / other"""

        if (isinstance(other, Unit)):
            si_unit = self.si_unit / other.si_unit
            equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
            value = float(self) / float(other)
            if equivalent_unit is not None:
                return equivalent_unit(value)
            else:
                return Unit(value, si_unit=si_unit)
        else: # scale value
            new_obj = self.clone()
            new_obj._value /= float(other)
            return new_obj

    ##############################################

    def __itruediv__(self, other):

        """self /= other"""

        if (isinstance(other, Unit)):
            raise NotImplementedError
        else: # scale value
            self._value /= float(other)
            return self

    ##############################################

    def __rtruediv__(self, other):

        """other / self"""

        if (isinstance(other, Unit)):
            raise NotImplementedError # Fixme: when ???
        else: # scale value
            return other / float(self)

    ##############################################

    def __pow__(self, exponent):

        """self**exponent; should promote to float or complex when necessary."""

        new_obj = self.clone()
        new_obj._value **= float(exponent)
        return new_obj

    ##############################################

    def __ipow__(self, exponent):

        self._value **= float(exponent)
        return self

    ##############################################

    def __rpow__(self, base):

        """base ** self"""

        raise NotImplementedError

    ##############################################

    def __abs__(self):

        """Returns the Real distance from 0. Called for abs(self)."""

        return self.__class__(abs(self._value))

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

    def __ceil__(self):

        return math.ceil(float(self))

    ##############################################

    def __floor__(self):

        return math.floor(float(self))

    ##############################################

    def __round__(self):

        return round(float(self))

    ##############################################

    def inverse(self):

        si_unit = self._si_unit.inverse()
        equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
        inverse_value = 1. / float(self)
        if equivalent_unit is not None:
            return equivalent_unit(inverse_value)
        else:
            return Unit(inverse_value, si_unit=si_unit)

    ##############################################

    def canonise(self):

        # log10(10**n) = n    log10(1) = 0   log10(10**-n) = -n   log10(0) = -oo

        try:
            abs_value = abs(float(self))
            log = math.log(abs_value)/math.log(1000)
            # if abs_value >= 1:
            #     power = 3 * int(log)
            # else:
            #     if log - int(log): # frac
            #         power = 3 * (int(log) -1)
            #     else:
            #         power = 3 * int(log)
            power = int(log)
            if abs_value < 1 and (log - int(log)):
                power -= 1
            power *= 3
            # print('Unit.canonise', self, self._value, int(self._power), '->', float(self), power)
            if power == int(self._power):
                # print('Unit.canonise noting to do for', self)
                return self
            elif power == 0:
                # print('Unit.canonise convert', self, 'to', Unit)
                return Unit(float(self), si_unit=self._si_unit)
            else:
                # Fixme: retrieve root unit
                cls = unit_prefix_classes[power]
                # print('Unit.canonise convert', self, 'to', cls)
                return Unit(float(self) / 10**power, si_unit=self._si_unit, power=cls.__power__)
        except Exception as e: # Fixme: fallback
            self._logger.warning(e)
            return self

####################################################################################################

# Define shortcuts for unit prefixes : ..., micro, milli, kilo, mega, ...

unit_prefix_classes = {}
for unit_prefix in UnitPrefixMetaclass.prefix_iter():
    if unit_prefix != ZeroPower:
        unit_cls_name = unit_prefix.__name__
        cls_name = unit_cls_name.lower()
        cls = types.new_class(cls_name, (Unit,))
        cls.__power__ = unit_prefix() # Instantiate class
        unit_prefix_classes[unit_prefix.__power__] = cls
        # Fixme: use def ?
        globals()[cls_name] = cls

####################################################################################################

class SiUnit(Unit):

    """This class implements an SI unit."""

    ##############################################

    @classmethod
    def is_base_unit(cls):
        return True

    ##############################################

    @classmethod
    def is_default_unit(cls):
        return True

####################################################################################################

class FrequencyMixin:

    """ This class implements a frequency mixin. """

    ##############################################

    @property
    def period(self):
        r""" Return the period :math:`T = \frac{1}{f}`. """
        return self.inverse()

    ##############################################

    @property
    def pulsation(self):
        r""" Return the pulsation :math:`\omega = 2\pi f`. """
        return float(self * 2 * math.pi)

####################################################################################################

class PeriodMixin:

    """ This class implements a period mixin. """

    ##############################################

    @property
    def frequency(self):
        r""" Return the period :math:`f = \frac{1}{T}`. """
        return self.inverse()

    ##############################################

    @property
    def pulsation(self):
        r""" Return the pulsation :math:`\omega = \frac{2\pi}{T}`. """
        return self.frequency.pulsation
