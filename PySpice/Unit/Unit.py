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

import collections
import math
# import numbers

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class UnitPrefixMetaclass(type):

    """Metaclass to register unit prefixes"""

    __prefixes__ = {} # singletons

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
        meta.__prefixes__[power] = cls()

    ##############################################

    @classmethod
    def prefix_iter(cls):
        return cls.__prefixes__.values()

    ##############################################

    @classmethod
    def get(cls, power):
        return cls.__prefixes__[power]

####################################################################################################

class UnitPrefix(metaclass=UnitPrefixMetaclass):

    """This class implements a unit prefix like kilo"""

    __power__ = None
    __prefix__ = ''

    ##############################################

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.__power__, self.__prefix__)

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

    @property
    def is_defined_in_spice(self):

        return self.spice_prefix is not None

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

    ##############################################

    def str(self, spice=False):

        if spice:
            return self.spice_prefix
        else:
            return self.__prefix__

####################################################################################################

class ZeroPower(UnitPrefix):
    __power__ = 0
    __prefix__ = ''
    __spice_prefix__ = ''

_zero_power = UnitPrefixMetaclass.get(0)

####################################################################################################

class SiDerivedUnit:

    """This class implements an unit defined as powers of SI base units.
    """

    # SI base units
    __base_units__ = (
        'm',
        'kg',
        's',
        'A',
        'K',
        'mol',
        'cd',
    )

    ##############################################

    def __init__(self, string=None, powers=None):

        if powers is not None:
            self._powers = self.new_powers()
            self._powers.update(powers)
        elif string is not None:
            self._powers = self.parse_si(string)
        else:
            self._powers = self.new_powers()

        self._hash = self.to_hash(self._powers)
        self._string = self.to_string(self._powers)

    ##############################################

    @property
    def powers(self):
        return self._powers

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
    def new_powers(cls):
        return {unit: 0 for unit in cls.__base_units__}

    ##############################################

    @classmethod
    def parse_si(cls, string):

        si_powers = cls.new_powers()
        if string:
            for unit_powers in string.split('*'):
                parts = unit_powers.split('^')
                unit = parts[0]
                if len(parts) == 1:
                    powers = 1
                else:
                    powers = int(parts[1])
                si_powers[unit] += powers
        return si_powers

    ##############################################

    @classmethod
    def to_hash(cls, powers):

        hash_ = ''
        for unit in cls.__base_units__:
            hash_ += str(powers[unit])
        return hash_

    ##############################################

    @classmethod
    def to_string(cls, si_powers):

        units = []
        for unit in cls.__base_units__:
            powers = si_powers[unit]
            if powers == 1:
                units.append(unit)
            elif powers > 1 or powers < 0:
                units.append('{}^{}'.format(unit, powers))
        return '*'.join(units)

    ##############################################

    # @property
    def is_base_unit(self):

        count = 0
        for powers in self._powers.values():
            if powers == 1:
                count += 1
            elif powers != 0:
                return False
        return count == 1

    ##############################################

    # @property
    def is_anonymous(self):

        return self._hash == '0'*len(self.__base_units__)

    ##############################################

    def __bool__(self):

        return not self.is_anonymous()

    ##############################################

    def clone(self):

        return self.__class__(powers=self._powers)

    ##############################################

    def __eq__(self, other):

        return self._hash == other.hash

    ##############################################

    def __ne__(self, other):

        return self._hash != other.hash

    ##############################################

    def __mul__(self, other):

        powers = {unit: self._powers[unit] + other._powers[unit]
                  for unit in self.__base_units__}
        return self.__class__(powers=powers)

    ##############################################

    def __imul__(self, other):

        for unit in self.__base_units__:
            self._powers[unit] += other.powers[unit]
        self._hash = self.to_hash(self._powers)
        self._string = self.to_string(self._powers)

        return self

    ##############################################

    def __truediv__(self, other):

        powers = {unit: self._powers[unit] - other._powers[unit]
                  for unit in self.__base_units__}
        return self.__class__(powers=powers)

    ##############################################

    def __itruediv__(self, other):

        for unit in self.__base_units__:
            self._powers[unit] -= other.powers[unit]
        self._hash = self.to_hash(self._powers)
        self._string = self.to_string(self._powers)

        return self

    ##############################################

    def inverse(self):

        powers = {unit: -self._powers[unit]
                  for unit in self.__base_units__}
        return self.__class__(powers=powers)

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
            cls.__si_unit__ = si_unit

    ##############################################

    @classmethod
    def register_unit(meta, cls):

        obj = cls()
        meta.__units__[obj.unit_suffix] = obj

        if obj.si_unit:
            hash_ = obj.si_unit.hash
            if hash_ in meta.__hash_map__:
                meta.__hash_map__[hash_].append(obj)
            else:
                meta.__hash_map__[hash_] = [obj]

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

class Unit(metaclass=UnitMetaclass):

    """This class implements an unit.
    """

    __unit_name__ = ''
    __unit_suffix__ = ''
    __quantity__ = ''
    __si_unit__ = SiDerivedUnit()
    __default_unit__ = False
    # __spice_suffix__ = ''

    _logger = _module_logger.getChild('Unit')

    ##############################################

    def __init__(self, si_unit=None):

        self._unit_name = self.__unit_name__
        self._unit_suffix = self.__unit_suffix__
        self._quantity = self.__quantity__

        if si_unit is None:
            self._si_unit = self.__si_unit__
        else:
            self._si_unit = si_unit

    ##############################################

    def __repr__(self):

        return '{0}({1})'.format(self.__class__.__name__, str(self))

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

    ##############################################

    @property
    def is_anonymous(self):
        return self._si_unit.is_anonymous()

    ##############################################

    @classmethod
    def is_default_unit(cls):
        return cls.__default_unit__

    @classmethod
    def is_base_unit(cls):
        return False

    ##############################################

    def __eq__(self, other):

        """self == other"""

        return self._si_unit == other.si_unit

    ##############################################

    def __ne__(self, other):

        """self != other"""

        # The default __ne__ doesn't negate __eq__ until 3.0.

        return not (self == other)

    ##############################################

    def _equivalent_unit_power(self, si_unit):

        equivalent_unit = UnitPower.from_si_unit(si_unit)
        if equivalent_unit is not None:
            return equivalent_unit
        else:
            return UnitPower(Unit(si_unit))

    ##############################################

    def _equivalent_unit(self, si_unit):

        equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
        if equivalent_unit is not None:
            return equivalent_unit
        else:
            return Unit(si_unit)

    ##############################################

    def _equivalent_unit_or_power(self, si_unit, unit_power):

        if unit_power:
            return self._equivalent_unit_power(si_unit)
        else:
            return self._equivalent_unit(si_unit)

    ##############################################

    def mul(self, other, unit_power=False):

        si_unit = self._si_unit * other.si_unit
        return self._equivalent_unit_or_power(si_unit, unit_power)

    ##############################################

    def div(self, other, unit_power=False):

        si_unit = self._si_unit / other.si_unit
        return self._equivalent_unit_or_power(si_unit, unit_power)

    ##############################################

    def inverse(self, unit_power=False):

        si_unit = self._si_unit.inverse()
        return self._equivalent_unit_or_power(si_unit, unit_power)

    ##############################################

    def __str__(self):

        if self._unit_suffix:
            return self._unit_suffix
        else:
            return str(self._si_unit)

    ##############################################

    def is_same_unit(self, value):

        return value.unit == self

    ##############################################

    def validate(self, value, none=False):

        if none and value is None:
            return None
        if isinstance(value, UnitValue):
            if  self.is_same_unit(value):
                return value
            else:
                raise UnitError
        else:
            unit_power = UnitPower.from_unit_power(self)
            return unit_power.new_value(value)

####################################################################################################

class SiBaseUnit(Unit):

    """This class implements an SI base unit."""

    ##############################################

    @classmethod
    def is_base_unit(cls):
        return True

    ##############################################

    @classmethod
    def is_default_unit(cls):
        return True

####################################################################################################

class UnitPower:

    """This class implements an unit power.
    """

    __unit_map__ = {} # Unit power singletons
    __unit_power_map__ = {}

    __value_ctor__ = None

    ##############################################

    @classmethod
    def register(cls, unit_power):
        unit = unit_power.unit
        unit_prefix = unit_power.power
        if unit_prefix.is_unit and unit.is_default_unit():
            key = unit.si_unit.hash
            # print('Register', key, unit_power)
            cls.__unit_map__[key] = unit_power
        if unit.unit_suffix:
            unit_key = str(unit)
        else:
            unit_key = '_'
        power_key = unit_prefix.power
        # print('Register', unit_key, power_key, unit_power)
        if unit_key not in cls.__unit_power_map__:
            cls.__unit_power_map__[unit_key] = {}
        cls.__unit_power_map__[unit_key][power_key] = unit_power

    ##############################################

    @classmethod
    def from_si_unit(cls, si_unit):
        return cls.__unit_map__.get(si_unit.hash, None)

    ##############################################

    @classmethod
    def from_unit_power(cls, unit, power=0):

        if unit.unit_suffix:
            unit_key = str(unit)
        else:
            if power == 0:
                return _simple_unit_power
            unit_key = '_'
        try:
            return cls.__unit_power_map__[unit_key][power]
        except KeyError:
            return None

    ##############################################

    def __init__(self, unit=None, power=None, value_ctor=None):

        if unit is None:
            self._unit = Unit()
        else:
            self._unit = unit
        if power is None:
            self._power = _zero_power
        else:
            self._power = power

        if value_ctor is None:
            self._value_ctor = self.__value_ctor__
        else:
            self._value_ctor = value_ctor

    ##############################################

    def __repr__(self):

        return '{0}({1})'.format(self.__class__.__name__, str(self))

    ##############################################

    @property
    def unit(self):
        return self._unit

    @property
    def power(self):
        return self._power

    @property
    def scale(self):
        return self._power.scale

    ##############################################

    @property
    def is_anonymous(self):
        return self._unit.is_anonymous

    ##############################################

    def clone(self):
        return self.__class__(self._unit, self._power)

    ##############################################

    def is_same_unit(self, other):

        return self._unit == other.unit

    ##############################################

    def check_unit(self, other):

        if not self.is_same_unit(other):
            raise UnitError

    ##############################################

    def is_same_power(self, other):

        return self._power == other.power

    ##############################################

    def __eq__(self, other):

        """self == other"""

        return self.is_same_unit(other) and self.is_same_power(other)

    ##############################################

    def __ne__(self, other):

        """self != other"""

        # The default __ne__ doesn't negate __eq__ until 3.0.

        return not (self == other)

    ##############################################

    def str(self, spice=False, unit=True):

        string = self._power.str(spice)
        if unit:
            string += str(self._unit)
        if spice:
            # Ngspice don't support utf-8
            string = string.replace('Ω', 'Ohm') # utf-8 cea0
            string = string.replace('μ',   'u') # utf-8 cebc
        return string

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

        return self.str(spice=True, unit=True)

    ##############################################

    def __str__(self):

        return self.str(spice=False, unit=True)

    ##############################################

    def new_value(self, value):

        if isinstance(value, collections.Iterable):
            return [self._value_ctor(self, x) for x in value]
        else:
            return self._value_ctor(self, value)

####################################################################################################

class UnitValue: # numbers.Real

    """This class implements a value with an unit and a power (prefix).

    The value is not converted to float if the value is an int.
    """

    _logger = _module_logger.getChild('UnitValue')

    ##############################################

    @classmethod
    def simple_value(cls, value):

        return cls(_simple_unit_power, value)

    ##############################################

    def __init__(self, unit_power, value):

        self._unit_power = unit_power

        if isinstance(value, UnitValue):
            # Fixme: anonymous ???
            if not self.is_same_unit(value):
                raise UnitError
            if self.is_same_power(value):
                self._value = value.value
            else:
                self._value = self._convert_scalar_value(value)
        elif isinstance(value, int):
            self._value = value # to keep as int
        else:
            self._value = float(value)

    ##############################################

    def __repr__(self):

        return '{0}({1})'.format(self.__class__.__name__, str(self))

    ##############################################

    @property
    def unit_power(self):
        return self._unit_power

    @property
    def unit(self):
        return self._unit_power.unit

    @property
    def power(self):
        return self._unit_power.power

    @property
    def scale(self):
        return self._unit_power.power.scale

    @property
    def value(self):
        return self._value

    ##############################################

    def clone(self):
        return self.__class__(self._unit_power, self._value)

    ##############################################

    def clone_unit_power(self, value):
        return self.__class__(self._unit_power, value)

    ##############################################

    # def clone_unit(self, value, power):
    #     return self.__class__(UnitPower(self.unit, power), value)

    ##############################################

    def is_same_unit(self, other):

        return self._unit_power.is_same_unit(other.unit_power)

    ##############################################

    def _check_unit(self, other):

        if not self.is_same_unit(other):
            raise UnitError

    ##############################################

    def is_same_power(self, other):

        return self._unit_power.is_same_power(other.unit_power)

    ##############################################

    def __eq__(self, other):

        """self == other"""

        if isinstance(other, UnitValue):
            return self.is_same_unit(other) and float(self) == float(other)
        else:
            return float(self) == float(other)

    ##############################################

    def __ne__(self, other):

        """self != other"""

        # The default __ne__ doesn't negate __eq__ until 3.0.

        return not (self == other)

    ##############################################

    def _convert_value(self, other):

        """Convert the value of other to the power of self."""

        self._check_unit(other)
        if self.is_same_power(other):
            return other.value
        else:
            return other.value * (other.scale / self.scale) # for numerical precision

    ##############################################

    def _convert_scalar_value(self, value):

        return float(value) / self.scale

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
        string += self._unit_power.str(spice, unit)
        return string

    ##############################################

    def str_space(self):
        return self.str(space=True)

    ##############################################

    def str_spice(self):

        return self.str(spice=True, space=False, unit=True)

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

        if (isinstance(other, UnitValue)):
            self._check_unit(other)
            new_obj = self.clone()
            new_obj._value += self._convert_value(other)
            return new_obj
        else:
            return float(self) + other

    ##############################################

    def __iadd__(self, other):

        """self += other"""

        self._check_unit(other)
        self._value += self._convert_value(other)
        return self

    ##############################################

    def __radd__(self, other):

        """other + self"""

        return float(self) + other

    ##############################################

    def __neg__(self):

        """-self"""

        return self.clone_unit_power(-self._value)

    ##############################################

    def __pos__(self):

        """+self"""

        return self.clone()

    ##############################################

    def __sub__(self, other):

        """self - other"""

        if (isinstance(other, UnitValue)):
            self._check_unit(other)
            new_obj = self.clone()
            new_obj._value -= self._convert_value(other)
            return new_obj
        else:
            return float(self) - other

    ##############################################

    def __isub__(self, other):

        """self -= other"""

        self._check_unit(other)
        self._value -= self._convert_value(other)
        return self

    ##############################################

    def __rsub__(self, other):

        """other - self"""

        return other - float(self)

    ##############################################

    def __mul__(self, other):

        """self * other"""

        if (isinstance(other, UnitValue)):
            equivalent_unit = self.unit.mul(other.unit, True)
            value = float(self) * float(other)
            return equivalent_unit.new_value(value)
        else:
            try: # scale value
                scalar = float(other)
                new_obj = self.clone()
                new_obj._value *= scalar
                return new_obj
            except (ValueError, TypeError): # Numpy raises TypeError
                return float(self) * other

    ##############################################

    def __imul__(self, other):

        """self *= other"""

        if (isinstance(other, UnitValue)):
            raise UnitError
        else: # scale value
            # Fixme: right ?
            self._value *= self._convert_value(other)
            return self

    ##############################################

    def __rmul__(self, other):

        """other * self"""

        if (isinstance(other, UnitValue)):
            raise NotImplementedError # Fixme: when ???
        else: # scale value
            return self.__mul__(other)

    ##############################################

    def __floordiv__(self, other):

        """self // other """

        if (isinstance(other, UnitValue)):
            equivalent_unit = self.unit.div(other.unit, True)
            value = float(self) // float(other)
            return equivalent_unit.new_value(value)
        else:
            try: # scale value
                scalar = float(other)
                new_obj = self.clone()
                new_obj._value //= scalar
                return new_obj
            except (ValueError, TypeError): # Numpy raises TypeError
                return float(self) // other

    ##############################################

    def __ifloordiv__(self, other):

        """self //= other """

        if (isinstance(other, UnitValue)):
            raise NotImplementedError
        else: # scale value
            self._value //= float(other)
            return self

    ##############################################

    def __rfloordiv__(self, other):

        """other // self"""

        if (isinstance(other, UnitValue)):
            raise NotImplementedError # Fixme: when ???
        else: # scale value
            return other // float(self)

    ##############################################

    def __truediv__(self, other):

        """self / other"""

        if (isinstance(other, UnitValue)):
            equivalent_unit = self.unit.div(other.unit, True)
            value = float(self) / float(other)
            return equivalent_unit.new_value(value)
        else:
            try: # scale value
                scalar = float(other)
                new_obj = self.clone()
                new_obj._value /= scalar
                return new_obj
            except (ValueError, TypeError): # Numpy raises TypeError
                return float(self) / other

    ##############################################

    def __itruediv__(self, other):

        """self /= other"""

        if (isinstance(other, UnitValue)):
            raise NotImplementedError
        else: # scale value
            self._value /= float(other)
            return self

    ##############################################

    def __rtruediv__(self, other):

        """other / self"""

        if (isinstance(other, UnitValue)):
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

        return self.clone_unit_power(abs(self._value))

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

        equivalent_unit = self.unit.inverse(unit_power=True)
        inverse_value = 1. / float(self)

        return equivalent_unit.new_value(inverse_value)

    ##############################################

    def get_unit_power(self, power=0):

        unit_power = UnitPower.from_unit_power(self.unit, power)
        if unit_power is not None:
            return unit_power
        else:
            raise NameError("Unit power not found for {} and power {}".format(self, power))

    ##############################################

    def convert(self, unit_power):

        """Convert the value to another power."""

        self._unit_power.check_unit(unit_power)
        if self._unit_power.is_same_power(unit_power):
            return self
        else:
            value = float(self) / unit_power.scale
            return unit_power.new_value(value)

    ##############################################

    def convert_to_power(self, power=0):

        """Convert the value to another power."""

        if power == 0:
            value = float(self)
        else:
            value = float(self) / 10**power

        return self.get_unit_power(power).new_value(value)

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
            if power == int(self.power):
                # print('Unit.canonise noting to do for', self)
                return self
            else:
                # print('Unit.canonise convert', self, 'to', power)
                # print('Unit.canonise convert', self, 'to', Unit)
                return self.convert_to_power(power)
        except Exception as e: # Fixme: fallback
            self._logger.warning(e)
            return self

####################################################################################################

# Reset
UnitPower.__value_ctor__ = UnitValue

_simple_unit_power = UnitPower()

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
