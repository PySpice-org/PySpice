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

# https://numpy.org/doc/stable/user/basics.subclassing.html#basics-subclassing

####################################################################################################

import logging

import collections.abc as collections
import math
# import numbers

import numpy as np

####################################################################################################

from PySpice.Tools.EnumFactory import EnumFactory

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class UnitPrefixMetaclass(type):

    """Metaclass to register unit prefixes"""

    _prefixes = {} # singletons

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):
        cls = type.__new__(meta, class_name, base_classes, attributes)
        if class_name != 'UnitPrefix':
            meta.register_prefix(cls)
        return cls

    ##############################################

    @classmethod
    def register_prefix(meta, cls):
        power = cls.POWER
        if power is None:
            raise ValueError('Power is None for {}'.format(cls.__name__))
        meta._prefixes[power] = cls()

    ##############################################

    @classmethod
    def prefix_iter(cls):
        return cls._prefixes.values()

    ##############################################

    @classmethod
    def get(cls, power):
        return cls._prefixes[power]

####################################################################################################

class UnitPrefix(metaclass=UnitPrefixMetaclass):

    """This class implements a unit prefix like kilo"""

    POWER = None
    PREFIX = ''

    ##############################################

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.POWER, self.PREFIX)

    ##############################################

    def __int__(self):
        return self.POWER

    ##############################################

    def __str__(self):
        return self.PREFIX

    ##############################################

    @property
    def power(self):
        return self.POWER

    @property
    def prefix(self):
        return self.PREFIX

    @property
    def is_unit(self):
        return self.POWER == 0

    @property
    def scale(self):
        return 10**self.POWER

    ##############################################

    @property
    def spice_prefix(self):
        if hasattr(self, 'SPICE_PREFIX'):
            return self.SPICE_PREFIX
        else:
            return self.PREFIX

    ##############################################

    @property
    def is_defined_in_spice(self):
        return self.spice_prefix is not None

    ##############################################

    def __eq__(self, other):
        return self.POWER == other.POWER

    ##############################################

    def __ne__(self, other):
        return self.POWER != other.POWER

    ##############################################

    def __lt__(self, other):
        return self.POWER < other.POWER

    ##############################################

    def __gt__(self, other):
        return self.POWER > other.POWER

    ##############################################

    def str(self, spice=False):
        if spice:
            return self.spice_prefix
        else:
            return self.PREFIX

####################################################################################################

class ZeroPower(UnitPrefix):
    POWER = 0
    PREFIX = ''
    SPICE_PREFIX = ''

_zero_power = UnitPrefixMetaclass.get(0)

####################################################################################################

class SiDerivedUnit:

    """This class implements a unit defined as powers of SI base units.
    """

    # SI base units
    BASE_UNITS = (
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
        return {unit: 0 for unit in cls.BASE_UNITS}

    ##############################################

    @classmethod
    def parse_si(cls, string):
        si_powers = cls.new_powers()
        if string:
            for prefixed_units in string.split('*'):
                parts = prefixed_units.split('^')
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
        for unit in cls.BASE_UNITS:
            hash_ += str(powers[unit])
        return hash_

    ##############################################

    @classmethod
    def to_string(cls, si_powers):
        units = []
        for unit in cls.BASE_UNITS:
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
    def is_unit_less(self):
        return self._hash == '0'*len(self.BASE_UNITS)

    ##############################################

    def __bool__(self):
        return not self.is_unit_less()

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
                  for unit in self.BASE_UNITS}
        return self.__class__(powers=powers)

    ##############################################

    def __imul__(self, other):
        for unit in self.BASE_UNITS:
            self._powers[unit] += other.powers[unit]
        self._hash = self.to_hash(self._powers)
        self._string = self.to_string(self._powers)
        return self

    ##############################################

    def __truediv__(self, other):
        powers = {unit: self._powers[unit] - other._powers[unit]
                  for unit in self.BASE_UNITS}
        return self.__class__(powers=powers)

    ##############################################

    def __itruediv__(self, other):
        for unit in self.BASE_UNITS:
            self._powers[unit] -= other.powers[unit]
        self._hash = self.to_hash(self._powers)
        self._string = self.to_string(self._powers)
        return self

    ##############################################

    def power(self, value):
        powers = {unit: self._powers[unit] * value
                  for unit in self.BASE_UNITS}
        return self.__class__(powers=powers)

    ##############################################

    def reciprocal(self):
        return self.power(-1)

    ##############################################

    def sqrt(self):
        return self.power(1/2)

    ##############################################

    def square(self):
        return self.power(2)

    ##############################################

    def cbrt(self):
        return self.power(1/3)

####################################################################################################

class UnitMetaclass(type):

    """Metaclass to register units"""

    _units = {}
    _hash_map = {}

    ##############################################

    def __new__(meta, class_name, base_classes, attributes):
        cls = type.__new__(meta, class_name, base_classes, attributes)
        meta.init_unit(cls)
        meta.register_unit(cls)
        return cls

    ##############################################

    @classmethod
    def init_unit(meta, cls):

        si_unit = cls.SI_UNIT
        if not (isinstance(si_unit, SiDerivedUnit) and si_unit):
            # si_unit is not defined
            if cls.is_base_unit():
                si_unit = SiDerivedUnit(cls.UNIT_SUFFIX)
            else: # str
                si_unit = SiDerivedUnit(si_unit)
            cls.SI_UNIT = si_unit

    ##############################################

    @classmethod
    def register_unit(meta, cls):

        obj = cls()
        meta._units[obj.unit_suffix] = obj

        if obj.si_unit:
            hash_ = obj.si_unit.hash
            if hash_ in meta._hash_map:
                meta._hash_map[hash_].append(obj)
            else:
                meta._hash_map[hash_] = [obj]

    ##############################################

    @classmethod
    def unit_iter(meta):
        return meta._units.values()

    ##############################################

    @classmethod
    def from_prefix(meta, prefix):
        return meta._units__.get(prefix, None)

    ##############################################

    @classmethod
    def from_hash(meta, hash_):
        return meta._hash_map.get(hash_, None)

    ##############################################

    @classmethod
    def from_si_unit(meta, si_unit, unique=True):

        # Fixme:
        #  - handle power of units
        #      unit -> numpy vector, divide and test for identical factor
        #      define unit, format as V^2
        #  - complex unit

        units = meta._hash_map.get(si_unit.hash, None)
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

    """This class implements a unit.
    """

    UNIT_NAME = ''
    UNIT_SUFFIX = ''
    QUANTITY = ''
    SI_UNIT = SiDerivedUnit()
    DEFAULT_UNIT = False
    # SPICE_SUFFIX = ''

    _logger = _module_logger.getChild('Unit')

    ##############################################

    def __init__(self, si_unit=None):

        self._unit_name = self.UNIT_NAME
        self._unit_suffix = self.UNIT_SUFFIX
        self._quantity = self.QUANTITY

        if si_unit is None:
            self._si_unit = self.SI_UNIT
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
    def is_unit_less(self):
        return self._si_unit.is_unit_less()

    ##############################################

    @classmethod
    def is_default_unit(cls):
        return cls.DEFAULT_UNIT

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

    def _equivalent_prefixed_unit(self, si_unit):

        equivalent_unit = PrefixedUnit.from_si_unit(si_unit)
        if equivalent_unit is not None:
            return equivalent_unit
        else:
            return PrefixedUnit(Unit(si_unit))

    ##############################################

    def _equivalent_unit(self, si_unit):

        equivalent_unit = UnitMetaclass.from_si_unit(si_unit)
        if equivalent_unit is not None:
            return equivalent_unit
        else:
            return Unit(si_unit)

    ##############################################

    def _equivalent_unit_or_power(self, si_unit, prefixed_unit):
        if prefixed_unit:
            return self._equivalent_prefixed_unit(si_unit)
        else:
            return self._equivalent_unit(si_unit)

    ##############################################

    def multiply(self, other, prefixed_unit=False):
        si_unit = self._si_unit * other.si_unit
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def divide(self, other, prefixed_unit=False):
        si_unit = self._si_unit / other.si_unit
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def power(self, exponent, prefixed_unit=False):
        si_unit = self._si_unit.power(exponent)
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def reciprocal(self, prefixed_unit=False):
        si_unit = self._si_unit.reciprocal()
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def sqrt(self, prefixed_unit=False):
        si_unit = self._si_unit.sqrt()
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def square(self, prefixed_unit=False):
        si_unit = self._si_unit.square()
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

    ##############################################

    def cbrt(self, prefixed_unit=False):
        si_unit = self._si_unit.cbrt()
        return self._equivalent_unit_or_power(si_unit, prefixed_unit)

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
            prefixed_unit = PrefixedUnit.from_prefixed_unit(self)
            return prefixed_unit.new_value(value)

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

class PrefixedUnit:

    """This class implements a prefixed unit.
    """

    _unit_map = {} # Prefixed unit singletons
    _prefixed_unit_map = {}

    _value_ctor = None
    _values_ctor = None

    ##############################################

    @classmethod
    def register(cls, prefixed_unit):
        unit = prefixed_unit.unit
        unit_prefix = prefixed_unit.power
        if unit_prefix.is_unit and unit.is_default_unit():
            key = unit.si_unit.hash
            # print('Register', key, prefixed_unit)
            cls._unit_map[key] = prefixed_unit
        if unit.unit_suffix:
            unit_key = str(unit)
        else:
            unit_key = '_'
        power_key = unit_prefix.power
        # print('Register', unit_key, power_key, prefixed_unit)
        if unit_key not in cls._prefixed_unit_map:
            cls._prefixed_unit_map[unit_key] = {}
        cls._prefixed_unit_map[unit_key][power_key] = prefixed_unit

    ##############################################

    @classmethod
    def from_si_unit(cls, si_unit):
        return cls._unit_map.get(si_unit.hash, None)

    ##############################################

    @classmethod
    def from_prefixed_unit(cls, unit, power=0):

        if unit.unit_suffix:
            unit_key = str(unit)
        else:
            if power == 0:
                return _simple_prefixed_unit
            unit_key = '_'
        try:
            return cls._prefixed_unit_map[unit_key][power]
        except KeyError:
            return None

    ##############################################

    def __init__(self, unit=None, power=None, value_ctor=None, values_ctor=None):

        if unit is None:
            self._unit = Unit()
        else:
            self._unit = unit
        if power is None:
            self._power = _zero_power
        else:
            self._power = power

        if value_ctor is not None:
            self._value_ctor = value_ctor

        if values_ctor is not None:
            self._values_ctor = values_ctor

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
    def is_unit_less(self):
        return self._unit.is_unit_less

    ##############################################

    def clone(self):
        return self.__class__(self._unit, self._power)

    ##############################################

    def is_same_unit(self, other):
        return self._unit == other.unit

    ##############################################

    def check_unit(self, other):
        if not self.is_same_unit(other):
            raise UnitError('{} versus {}'.format(self, other))

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

        # Ngspice User Manual Section 2.3.1  Some naming conventions
        #
        # Letters immediately following a number that are not scale factors are ignored, and
        # letters immediately following a scale factor are ignored.
        #
        # Hence, 10, 10V, 10Volts, and 10Hz all represent the same number, and
        # M, MA, MSec, and  MMhos all represent the same scale factor.
        #
        # Note that 1000, 1000.0, 1000Hz, 1e3, 1.0e3, 1kHz, and 1k all represent the same number.

        # >>> WARNING <<<
        #   Note that M or m denote ’milli’, i.e. 10−3 . Suffix meg has to be used for 106.
        #   see SPICE_PREFIX in SiUnits

        # Fixme: unit clash, e.g. mm ???

        string = self._power.str(spice)

        if unit:
            string += str(self._unit)

        if spice:
            # F is interpreted as f = femto
            if string == 'F':
                string = ''
            else:
                # Ngspice don't support utf-8
                # degree symbole can be encoded str(176) in Extended ASCII
                string = string.replace('°', '')  # U+00B0
                string = string.replace('℃', '')  # U+2103
                # U+2109 ℉
                string = string.replace('Ω', 'Ohm')  # U+CEA0
                string = string.replace('μ',   'u')  # U+CEBC

        return string

    ##############################################

    def str_spice(self):
        return self.str(spice=True, unit=True)

    ##############################################

    def __str__(self):
        return self.str(spice=False, unit=True)

    ##############################################

    def new_value(self, value):
        if isinstance(value, np.ndarray):
            return self._values_ctor.from_ndarray(value, self)
        elif isinstance(value, collections.Iterable):
            return [self._value_ctor(self, x) for x in value]
        else:
            return self._value_ctor(self, value)

####################################################################################################

class UnitValue: # numbers.Real

    """This class implements a value with a unit and a power (prefix).

    The value is not converted to float if the value is an int.
    """

    _logger = _module_logger.getChild('UnitValue')

    ##############################################

    @classmethod
    def simple_value(cls, value):
        return cls(_simple_prefixed_unit, value)

    ##############################################

    def __init__(self, prefixed_unit, value):

        self._prefixed_unit = prefixed_unit

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
    def prefixed_unit(self):
        return self._prefixed_unit

    @property
    def unit(self):
        return self._prefixed_unit.unit

    @property
    def power(self):
        return self._prefixed_unit.power

    @property
    def scale(self):
        return self._prefixed_unit.power.scale

    @property
    def value(self):
        return self._value

    ##############################################

    def clone(self):
        return self.__class__(self._prefixed_unit, self._value)

    ##############################################

    def clone_prefixed_unit(self, value):
        return self.__class__(self._prefixed_unit, value)

    ##############################################

    # def to_unit_values(self):
    #     return self._prefixed_unit.new_value(self._value)

    ##############################################

    # def clone_unit(self, value, power):
    #     return self.__class__(PrefixedUnit(self.unit, power), value)

    ##############################################

    def is_same_unit(self, other):
        return self._prefixed_unit.is_same_unit(other.prefixed_unit)

    ##############################################

    def _check_unit(self, other):
        if not self.is_same_unit(other):
            raise UnitError

    ##############################################

    def is_same_power(self, other):
        return self._prefixed_unit.is_same_power(other.prefixed_unit)

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
        string += self._prefixed_unit.str(spice, unit)
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
        return self.clone_prefixed_unit(-self._value)

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
            equivalent_unit = self.unit.multiply(other.unit, True)
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
            equivalent_unit = self.unit.divide(other.unit, True)
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
            equivalent_unit = self.unit.divide(other.unit, True)
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
        return self.clone_prefixed_unit(abs(self._value))

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

        < on Reals defines a total ordering, except perhaps for NaN.

        """
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

    def reciprocal(self):
        equivalent_unit = self.unit.reciprocal(prefixed_unit=True)
        reciprocal_value = 1. / float(self)
        return equivalent_unit.new_value(reciprocal_value)

    ##############################################

    def get_prefixed_unit(self, power=0):
        prefixed_unit = PrefixedUnit.from_prefixed_unit(self.unit, power)
        if prefixed_unit is not None:
            return prefixed_unit
        else:
            raise NameError("Prefixed unit not found for {} and power {}".format(self, power))

    ##############################################

    def convert(self, prefixed_unit):
        """Convert the value to another power."""
        self._prefixed_unit.check_unit(prefixed_unit)
        if self._prefixed_unit.is_same_power(prefixed_unit):
            return self
        else:
            value = float(self) / prefixed_unit.scale
            return prefixed_unit.new_value(value)

    ##############################################

    def convert_to_power(self, power=0):
        """Convert the value to another power."""
        if power == 0:
            value = float(self)
        else:
            value = float(self) / 10**power
        return self.get_prefixed_unit(power).new_value(value)

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

class UnitValues(np.ndarray):

    """This class implements a Numpy array with a unit and a power (prefix).

    """

    _logger = _module_logger.getChild('UnitValues')

    CONVERSION = EnumFactory('ConversionType', (
        'NOT_IMPLEMENTED',
        'NO_CONVERSION',
        'FLOAT',
        'UNIT_MATCH',
        'UNIT_MATCH_NO_OUT_CAST',
        'NEW_UNIT'
        ))

    # Reference_documentation:
    #   https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.ndarray.html
    #   https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html
    #   https://docs.scipy.org/doc/numpy-1.13.0/reference/ufuncs.html
    UFUNC_MAP = {
        # Math operations
        # --------------------------------------------------
        np.add:          CONVERSION.UNIT_MATCH,
        np.subtract:     CONVERSION.UNIT_MATCH,
        np.multiply:     CONVERSION.NEW_UNIT,
        np.divide:       CONVERSION.NEW_UNIT,
        np.logaddexp:    CONVERSION.FLOAT,
        np.logaddexp2:   CONVERSION.FLOAT,
        np.true_divide:  CONVERSION.NEW_UNIT,
        np.floor_divide: CONVERSION.NEW_UNIT,
        np.negative:     CONVERSION.NO_CONVERSION,
        np.positive:     CONVERSION.NO_CONVERSION,
        np.power:        CONVERSION.NEW_UNIT,
        np.remainder:    CONVERSION.UNIT_MATCH,
        np.mod:          CONVERSION.UNIT_MATCH,
        np.fmod:         CONVERSION.UNIT_MATCH,
        np.divmod:       CONVERSION.UNIT_MATCH,
        np.absolute:     CONVERSION.NO_CONVERSION,
        np.fabs:         CONVERSION.NO_CONVERSION,
        np.rint:         CONVERSION.NO_CONVERSION,
        np.sign:         CONVERSION.NO_CONVERSION,
        np.heaviside:    CONVERSION.NOT_IMPLEMENTED, # !
        np.conj:         CONVERSION.NOT_IMPLEMENTED, # !
        np.exp:          CONVERSION.FLOAT,
        np.exp2:         CONVERSION.FLOAT,
        np.log:          CONVERSION.FLOAT,
        np.log2:         CONVERSION.FLOAT,
        np.log10:        CONVERSION.FLOAT,
        np.expm1:        CONVERSION.FLOAT,
        np.log1p:        CONVERSION.FLOAT,
        np.sqrt:         CONVERSION.NEW_UNIT,
        np.square:       CONVERSION.NEW_UNIT,
        np.cbrt:         CONVERSION.NEW_UNIT,
        np.reciprocal:   CONVERSION.NEW_UNIT,

        # Trigonometric functions
        # --------------------------------------------------
        np.sin:     CONVERSION.FLOAT,
        np.cos:     CONVERSION.FLOAT,
        np.tan:     CONVERSION.FLOAT,
        np.arcsin:  CONVERSION.FLOAT,
        np.arccos:  CONVERSION.FLOAT,
        np.arctan:  CONVERSION.FLOAT,
        np.arctan2: CONVERSION.FLOAT,
        np.hypot:   CONVERSION.FLOAT,
        np.sinh:    CONVERSION.FLOAT,
        np.cosh:    CONVERSION.FLOAT,
        np.tanh:    CONVERSION.FLOAT,
        np.arcsinh: CONVERSION.FLOAT,
        np.arccosh: CONVERSION.FLOAT,
        np.arctanh: CONVERSION.FLOAT,
        np.deg2rad: CONVERSION.FLOAT,
        np.rad2deg: CONVERSION.FLOAT,

        # Bit-twiddling functions
        # --------------------------------------------------
        np.bitwise_and: CONVERSION.NOT_IMPLEMENTED, # Nonsense
        np.bitwise_or:  CONVERSION.NOT_IMPLEMENTED, # Nonsense
        np.bitwise_xor: CONVERSION.NOT_IMPLEMENTED, # Nonsense
        np.invert:      CONVERSION.NOT_IMPLEMENTED, # Nonsense
        np.left_shift:  CONVERSION.NOT_IMPLEMENTED, # Nonsense
        np.right_shift: CONVERSION.NOT_IMPLEMENTED, # Nonsense

        # Comparison functions
        # --------------------------------------------------
        np.greater:       CONVERSION.UNIT_MATCH_NO_OUT_CAST,
        np.greater_equal: CONVERSION.UNIT_MATCH_NO_OUT_CAST,
        np.less:          CONVERSION.UNIT_MATCH_NO_OUT_CAST,
        np.less_equal:    CONVERSION.UNIT_MATCH_NO_OUT_CAST,
        np.not_equal:     CONVERSION.UNIT_MATCH_NO_OUT_CAST,
        np.equal:         CONVERSION.UNIT_MATCH_NO_OUT_CAST,

        np.logical_and:   CONVERSION.UNIT_MATCH,
        np.logical_or:    CONVERSION.UNIT_MATCH,
        np.logical_xor:   CONVERSION.UNIT_MATCH,
        np.logical_not:   CONVERSION.UNIT_MATCH,

        np.maximum:       CONVERSION.UNIT_MATCH,
        np.minimum:       CONVERSION.UNIT_MATCH,
        np.fmax:          CONVERSION.UNIT_MATCH,
        np.fmin:          CONVERSION.UNIT_MATCH,

        # Floating functions
        # --------------------------------------------------
        np.isfinite:  CONVERSION.NOT_IMPLEMENTED, # ! _T
        np.isinf:     CONVERSION.NOT_IMPLEMENTED, # ! _T
        np.isnan:     CONVERSION.NOT_IMPLEMENTED, # ! _T
        np.fabs:      CONVERSION.NOT_IMPLEMENTED, # ! _
        np.signbit:   CONVERSION.NOT_IMPLEMENTED, # ! _T
        np.copysign:  CONVERSION.NOT_IMPLEMENTED, # !
        np.nextafter: CONVERSION.NOT_IMPLEMENTED, # !
        np.spacing:   CONVERSION.NOT_IMPLEMENTED, # !
        np.modf:      CONVERSION.NOT_IMPLEMENTED, # !
        np.ldexp:     CONVERSION.NOT_IMPLEMENTED, # !
        np.frexp:     CONVERSION.NOT_IMPLEMENTED, # !
        np.fmod:      CONVERSION.NOT_IMPLEMENTED, # !
        np.floor:     CONVERSION.NOT_IMPLEMENTED, # !
        np.ceil:      CONVERSION.NO_CONVERSION,
        np.trunc:     CONVERSION.NO_CONVERSION,

        # Statistic functions
        # --------------------------------------------------
        np.mean:      CONVERSION.NO_CONVERSION,
    }

    ##############################################

    @classmethod
    def from_ndarray(cls, array, prefixed_unit):

        # cls._logger.debug('UnitValues.__new__ ' + str((cls, array, prefixed_unit)))

        # obj = cls(prefixed_unit, array.shape, array.dtype) # Fixme: buffer ???
        # obj[...] = array[...]

        obj = array.view(UnitValues)
        obj._prefixed_unit = prefixed_unit

        if isinstance(array, UnitValues):
            return array.convert(prefixed_unit)

        return obj

    ##############################################

    def __new__(cls,
                prefixed_unit,
                shape, dtype=float, buffer=None, offset=0, strides=None, order=None):

        # Called for explicit constructor
        #  obj = UnitValues(prefixed_unit, shape)

        # cls._logger.debug('UnitValues.__new__ ' + str((cls, prefixed_unit, shape, dtype, buffer, offset, strides, order)))

        obj = super(UnitValues, cls).__new__(cls, shape, dtype, buffer, offset, strides, order)
        # obj = np.asarray(input_array).view(cls)

        obj._prefixed_unit = prefixed_unit

        return obj

    ##############################################

    def __array_finalize__(self, obj):

        # self._logger.debug('UnitValues.__new__ ' + '\n  {}'.format(obj))

        # self is a new object resulting from ndarray.__new__(UnitValues, ...)
        # therefore it only has attributes that the ndarray.__new__ constructor gave it
        # i.e. those of a standard ndarray.

        # We could have got to the ndarray.__new__ call in 3 ways:

        # From an explicit constructor - e.g. UnitValues():
        #    obj is None
        #    we are in the middle of the UnitValues.__new__ constructor

        if obj is None:
            return

        # From view casting - e.g arr.view(UnitValues):
        #    obj is arr
        #    type(obj) can be UnitValues

        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is UnitValues

        self._prefixed_unit = getattr(obj, '_prefixed_unit', None) # Fixme: None

    ##############################################

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):

        # - "ufunc" is the ufunc object that was called
        # - "method" is a string indicating how the ufunc was called, either
        #       "__call__" to indicate it was called directly,
        #       or one of its "ufuncs.methods": "reduce", "accumulate",  "reduceat", "outer", or "at".
        # - "inputs" is a tuple of the input arguments to the ufunc
        # - "kwargs" contains any optional or keyword arguments passed to the function.
        #    This includes any *out* arguments, which are always contained in a tuple.

        # ufunc.reduce(a[, axis, dtype, out, keepdims])     Reduces a‘s dimension by one, by applying ufunc along one axis.
        # ufunc.accumulate(array[, axis, dtype, out, ...])  Accumulate the result of applying the operator to all elements.
        # ufunc.reduceat(a, indices[, axis, dtype, out])    Performs a (local) reduce with specified slices over a single axis.
        # ufunc.outer(A, B, **kwargs)                       Apply the ufunc op to all pairs (a, b) with a in A and b in B.
        # ufunc.at(a, indices[, b])                         Performs unbuffered in place operation on operand ‘a’ for elements specified by ‘indices’.

        # self._logger.debug(
        #     '\n  self={}\n  ufunc={}\n  method={}\n  inputs={}\n  kwargs={}'
        #     .format(self, ufunc, method, inputs, kwargs))

        # ufunc=<ufunc 'multiply'>
        # method=__call__
        # inputs=(UnitValues(mV, [0 1 2 3 4 5 6 7 8 9]), 2)

        # ufunc=<ufunc 'sin'>
        # method=__call__
        # inputs=(UnitValues(mV, [0 1 2 3 4 5 6 7 8 9]),)
        # kwargs={}

        # ufunc=<ufunc 'add'>
        # method=__call__
        # inputs=(UnitValues(mV, [0 1 2 3 4 5 6 7 8 9]), UnitValues(mV, [0 1 2 3 4 5 6 7 8 9]))

        # ufunc=<ufunc 'add'>
        # method=reduce
        # inputs=(WaveForm  [10 12 14 16 18 20 22 24 26 28]@mV,)

        prefixed_unit = self._prefixed_unit

        conversion = self.UFUNC_MAP[ufunc]
        self._logger.debug("Conversion for {} is {}".format(ufunc, conversion))

        # e.g. np.mean do an internal call to reduce
        if method != '__call__':
            conversion = self.CONVERSION.NO_CONVERSION

        # Cast inputs to ndarray
        args = []
        if conversion == self.CONVERSION.NO_CONVERSION:
            # should be 1 arg
            args = [( input_.as_ndarray(False) if isinstance(input_, UnitValues) else input_ )
                    for input_ in inputs]
        #
        elif conversion == self.CONVERSION.FLOAT:
            if not prefixed_unit.is_unit_less:
                # raise ValueError("Must be unit less")
                self._logger.warning("Should be unit less")
            args = [( input_.as_ndarray(True) if isinstance(input_, UnitValues) else input_ )
                    for input_ in inputs]
        #
        elif conversion in (self.CONVERSION.UNIT_MATCH, self.CONVERSION.UNIT_MATCH_NO_OUT_CAST):
            # len(inputs) == 2
            other = inputs[1]
            if isinstance(other, (UnitValues, UnitValue)):
                self._check_unit(other)
                args.append(self.as_ndarray())
                nd_other = self._convert_value(other)
                if isinstance(other, UnitValues):
                    nd_other = nd_other.as_ndarray()
                elif isinstance(other, UnitValue):
                    nd_other = float(nd_other)
                args.append(nd_other)
            else:
                raise ValueError
        #
        elif conversion == self.CONVERSION.NEW_UNIT:
            if len(inputs) == 1:
                #! Fixme: power
                if ufunc == np.sqrt:
                    prefixed_unit = self.unit.sqrt(True)
                elif ufunc == np.square:
                    prefixed_unit = self.unit.square(True)
                elif ufunc == np.cbrt:
                    prefixed_unit = self.unit.cbrt(True)
                elif ufunc == np.reciprocal:
                    prefixed_unit = self.unit.reciprocal(True)
                else:
                    raise NotImplementedError
                args.append(self.as_ndarray(True))
            elif len(inputs) == 2:
                other = inputs[1]
                if isinstance(other, (UnitValues, UnitValue)):
                    if ufunc == np.multiply:
                        prefixed_unit = self.unit.multiply(other.unit, True)
                    elif ufunc in (np.divide, np.true_divide, np.floor_divide):
                        prefixed_unit = self.unit.divide(other.unit, True)
                    else:
                        raise NotImplementedError
                    args.append(self.as_ndarray(True))
                    if isinstance(other, UnitValue):
                        args.append(float(other))
                    else:
                        args.append(other.as_ndarray(True))
                elif ufunc in (np.multiply, np.divide, np.true_divide, np.floor_divide, np.power):
                    if ufunc == np.power:
                        prefixed_unit = self.unit.power(other, True)
                    args.append(self.as_ndarray())
                    args.append(other)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        #
        else: # self.CONVERSION.NOT_IMPLEMENTED
            raise NotImplementedError

        # self._logger.debug("Output unit is {}".format(prefixed_unit))

        # Cast outputs to ndarray
        outputs = kwargs.pop('out', None)
        if outputs:
            out_args = []
            for output in outputs:
                if isinstance(output, UnitValues):
                    out_args.append(output.as_ndarray())
                else:
                    out_args.append(output)
            kwargs['out'] = tuple(out_args)
        else:
            outputs = (None,) * ufunc.nout

        # Call ufunc
        results = super(UnitValues, self).__array_ufunc__(ufunc, method, *args, **kwargs)
        if results is NotImplemented:
            return NotImplemented

        # ensure results is a tuple
        if ufunc.nout == 1:
            results = (results,)

        # Cast results
        if conversion in (self.CONVERSION.FLOAT, self.CONVERSION.UNIT_MATCH_NO_OUT_CAST):
            # Fixme: ok ???
            results = tuple(( result if output is None else output )
                            for result, output in zip(results, outputs))
        else:
            results = tuple(( UnitValues.from_ndarray(np.asarray(result), prefixed_unit) if output is None else output )
                            for result, output in zip(results, outputs))

        # list or scalar
        return results[0] if len(results) == 1 else results

    ##############################################

#   def __array_wrap__(self, out_array, context=None):
#
#       self._logger.debug('\n  self={}\n  out_array={}\n  context={}'.format(self, out_array, context))
#
#       return super(UnitValues, self).__array_wrap__(out_array, context)

    ##############################################

    def as_ndarray(self, scale=False):
        array = self.view(np.ndarray)
        if scale:
            return array * self.scale
        else:
            return array

    ##############################################

    def __getitem__(self, slice_):

        value = super(UnitValues, self).__getitem__(slice_)

        if isinstance(value, UnitValue): # slice
            return value
        else:
            return self._prefixed_unit.new_value(value)

    ##############################################

    def __setitem__(self, slice_, value):

        if isinstance(value, UnitValue):
            self._check_unit(value)
            value = self._convert_value(value).value
        elif isinstance(value, UnitValues):
            self._check_unit(value)
            value = self._convert_value(value)

        super(UnitValues, self).__setitem__(slice_, value)

    ##############################################

    # def __getstate__(self):
    #     # https://docs.python.org/3/library/pickle.html#object.__getstate__
    #     return {
    #         'data': super(UnitValues, self).__getstate__(),
    #         'prefixed_unit': self._prefixed_unit,
    #     }

    ##############################################

    def __reduce__(self):
        # https://docs.python.org/3/library/pickle.html#object.__reduce__
        np_state = super(UnitValues, self).__reduce__()
        # ( <built-in function _reconstruct>,
        #   (<class 'PySpice.Unit.Unit.UnitValues'>, (0,), b'b'),
        #   (1, (1, 1), dtype('float64'), False, b'\x00\x00\x80?\x00\x00\x80?') )
        obj_state = (self._prefixed_unit,) + np_state[2]
        return np_state[:2] + (obj_state,) + np_state[3:]

    ##############################################

    def __setstate__(self, state):
        # https://docs.python.org/3/library/pickle.html#object.__setstate__
        super(UnitValues, self).__setstate__(state[1:])
        self._prefixed_unit = state[0]

    ##############################################

    def __contains__(self, value):
        raise NotImplementedError

    ##############################################

    def __repr__(self):
        # return repr(self.as_ndarray())
        return '{}({})'.format(self.__class__.__name__, str(self))

    ##############################################

    @property
    def prefixed_unit(self):
        return self._prefixed_unit

    @property
    def unit(self):
        return self._prefixed_unit.unit

    @property
    def power(self):
        return self._prefixed_unit.power

    @property
    def scale(self):
        return self._prefixed_unit.power.scale

    ##############################################

    def is_same_unit(self, other):
        return self._prefixed_unit.is_same_unit(other.prefixed_unit)

    ##############################################

    def _check_unit(self, other):
        if not self.is_same_unit(other):
            raise UnitError

    ##############################################

    def is_same_power(self, other):
        return self._prefixed_unit.is_same_power(other.prefixed_unit)

    ##############################################

    def __eq__(self, other):
        """self == other"""
        if isinstance(other, UnitValues):
            return self.is_same_unit(other) and self.as_ndarray() == other.as_ndarray()
        else:
            raise ValueError

    ##############################################

    def _convert_value(self, other):
        """Convert the value of other to the power of self."""
        self._check_unit(other)
        if self.is_same_power(other):
            return other
        else:
            return other * (other.scale / self.scale) # for numerical precision

    ##############################################

    def __str__(self):
        return str(self.as_ndarray()) + '@' + str(self._prefixed_unit)

    ##############################################

    def reciprocal(self):
        equivalent_unit = self.unit.reciprocal(prefixed_unit=True)
        reciprocal_value = 1. / np.as_ndarray(True)
        return self.from_ndarray(reciprocal_value, equivalent_unit)

    ##############################################

    def get_prefixed_unit(self, power=0):
        prefixed_unit = PrefixedUnit.from_prefixed_unit(self.unit, power)
        if prefixed_unit is not None:
            return prefixed_unit
        else:
            raise NameError("Prefixed unit not found for {} and power {}".format(self, power))

    ##############################################

    def convert(self, prefixed_unit):
        """Convert the value to another power."""
        self._prefixed_unit.check_unit(prefixed_unit)
        if self._prefixed_unit.is_same_power(prefixed_unit):
            return self
        else:
            value = self.as_ndarray(True) / prefixed_unit.scale
            return prefixed_unit.new_value(value)

    ##############################################

    def convert_to_power(self, power=0):
        """Convert the value to another power."""
        value = self.as_ndarray(True)
        if power != 0:
            value /= 10**power
        return self.get_prefixed_unit(power).new_value(value)

####################################################################################################

# Reset
PrefixedUnit._value_ctor = UnitValue
PrefixedUnit._values_ctor = UnitValues

_simple_prefixed_unit = PrefixedUnit()

####################################################################################################

class FrequencyMixin:

    """ This class implements a frequency mixin. """

    ##############################################

    @property
    def period(self):
        r""" Return the period :math:`T = \frac{1}{f}`. """
        return self.reciprocal()

    ##############################################

    @property
    def pulsation(self):
        r""" Return the pulsation :math:`\omega = 2\pi f`. """
        # Fixme: UnitValues
        return float(self * 2 * math.pi)

####################################################################################################

class PeriodMixin:

    """ This class implements a period mixin. """

    ##############################################

    @property
    def frequency(self):
        r""" Return the period :math:`f = \frac{1}{T}`. """
        return self.reciprocal()

    ##############################################

    @property
    def pulsation(self):
        r""" Return the pulsation :math:`\omega = \frac{2\pi}{T}`. """
        return self.frequency.pulsation
