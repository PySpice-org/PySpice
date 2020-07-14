####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2017 Fabrice Salvaire
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

# Note: This module should be outsourced, only code specific to SPICE must remain.

"""This module implements units.

Shortcuts are defined to build unit values easily :

 * for each unit prefix, e.g. :func:`pico`, :func:`nano`, :func:`micro`, :func:`milli`, :func:`kilo`,
   :func:`mega`, :func:`tera`. These shortcuts return unit less values.

 * for each unit and prefix as the concatenation of *u_*, the unit prefix and the
   unit suffix, e.g. :func:`u_pV`, :func:`u_nV`, :func:`u_uV` :func:`u_mV`, :func:`u_V`,
   :func:`u_kV`, :func:`u_MV`, :func:`u_TV`.

Theses unit value constructors accept int, float, object that can be converted to float,
:class:`UnitValue` instance and an iterable on these types.

A shortcut is defined to check an unit value match a particular unit, e.g. :func:`as_V`.  Theses
shortcuts return the value if the unit match else it raises the exception *UnitError*.

A shortcut is defined to access each unit, e.g. :func:`U_V`, :func:`U_A`, :func:`U_s`, :func:`U_Hz`,
:func:`U_Ω`, :func:`U_F`, :func:`U_H.`, as well as for prefixes e.g. :func:`U_mV`.

Some shortcuts have Unicode and ASCII variants:

 * For micro, we have the prefix *μ* and *u*.
 * For Ohm, we have :func:`u_Ω` and :func:`u_Ohm`.

Some examples of usage:

.. code-block:: python3

  foo = kilo(1) # unit less

  resistance_unit = U_Ω

  resistance1 = u_kΩ(1)
  resistance1 = u_kOhm(1) # ASCII variant

  resistance1 = 1@u_kΩ   # using Python 3.5 syntax
  resistance1 = 1 @u_kΩ  # space doesn't matter
  resistance1 = 1 @ u_kΩ #

  resistance2 = as_Ω(resistance1) # check unit

  resistances = u_kΩ(range(1, 11)) # same as [u_kΩ(x) for x in range(1, 11)]
  resistances = range(1, 11)@u_kΩ  # using Python 3.5 syntax

  capacitance = u_uF(200)
  inductance = u_mH(1)
  temperature = u_Degree(25)

  voltage = resistance1 * u_mA(1) # compute unit

  frequency = u_ms(20).frequency
  period = u_Hz(50).period
  pulsation = frequency.pulsation
  pulsation = period.pulsation

.. warning::

   According to the Python `operator precedence
  <https://docs.python.org/3/reference/expressions.html#operator-precedence>`_, division operators
  have a higher priority than the matrix multiplication operator.  In consequence you must had
  parenthesis to perform something like :code:`(10@u_s) / (2@_us)`.

"""

####################################################################################################

import logging
import sys

from . import Unit as _Unit
from . import SiUnits as _SiUnits

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

_version_info = sys.version_info
_has_matmul = _version_info.major * 10 + _version_info.minor >= 35
if not _has_matmul:
    _module_logger.warning("Your Python version doesn't implement @ operator")

####################################################################################################

class UnitValueShorcut:

    ##############################################

    def __init__(self, prefixed_unit):

        self._prefixed_unit = prefixed_unit

    ##############################################

    def _new_value(self, other):

        return self._prefixed_unit.new_value(other)

    ##############################################

    def __call__(self, other):

        """self(other)"""

        return self._new_value(other)

    ##############################################

    def __rmatmul__(self, other):

        """other @ self"""

        return self._new_value(other)

####################################################################################################

def _to_ascii(name):
    ascii_name = name
    for args in (
            ('μ', 'u'),
            ('Ω', 'Ohm'),
            ('°C', 'Degree'),
    ):
        ascii_name = ascii_name.replace(*args)
    return ascii_name

def define_shortcut(name, shortcut) :
    # ° is illegal in Python 3.5
    #  see https://docs.python.org/3/reference/lexical_analysis.html#identifiers
    #      https://www.python.org/dev/peps/pep-3131/
    if '°' not in name:
        globals()[name] = shortcut
    ascii_name = _to_ascii(name)
    if ascii_name != name:
        globals()[ascii_name] = shortcut

####################################################################################################

# Define shortcuts for unit prefixes : ..., micro, milli, kilo, mega, ...

def _build_prefix_shortcut(unit_prefix):
    unit_cls_name = unit_prefix.__class__.__name__
    name = unit_cls_name.lower()
    prefixed_unit = _Unit.PrefixedUnit(power=unit_prefix)
    _Unit.PrefixedUnit.register(prefixed_unit)
    shortcut = lambda value: _Unit.UnitValue(prefixed_unit, value)
    define_shortcut(name, shortcut)

for unit_prefix in _Unit.UnitPrefixMetaclass.prefix_iter():
    if unit_prefix.__class__ != _Unit.ZeroPower:
        _build_prefix_shortcut(unit_prefix) # capture unit_prefix

####################################################################################################

# Fixme: better ???

class FrequencyValue(_Unit.UnitValue, _Unit.FrequencyMixin):
    pass

# Fixme:
class FrequencyValues(_Unit.UnitValues): # , _Unit.FrequencyMixin
    pass

class PeriodValue(_Unit.UnitValue, _Unit.PeriodMixin):
    pass

class PeriodValues(_Unit.UnitValues): # , _Unit.PeriodMixin
    pass

####################################################################################################

# Define unit shortcuts

def _build_unit_type_shortcut(unit):
    name = 'U_' + unit.unit_suffix
    define_shortcut(name, unit)

def _build_as_unit_shortcut(unit):
    name = 'as_' + unit.unit_suffix
    shortcut = unit.validate
    define_shortcut(name, shortcut)

def _exec_body(ns, unit_prefix):
    ns['POWER'] = unit_prefix

def _build_unit_prefix_shortcut(unit, unit_prefix):
    name = 'u_' + str(unit_prefix) + unit.unit_suffix
    if unit.__class__ == _SiUnits.Hertz:
        value_ctor = FrequencyValue
        values_ctor = FrequencyValues
    elif unit.__class__ == _SiUnits.Second:
        value_ctor = PeriodValue
        values_ctor = PeriodValues
    else:
        value_ctor = _Unit.UnitValue
        values_ctor = _Unit.UnitValues
    prefixed_unit = _Unit.PrefixedUnit(unit, unit_prefix, value_ctor, values_ctor)
    _Unit.PrefixedUnit.register(prefixed_unit)
    define_shortcut('U' + name[1:], prefixed_unit)
    shortcut = UnitValueShorcut(prefixed_unit)
    define_shortcut(name, shortcut)

def _build_unit_shortcut(unit):
    _build_as_unit_shortcut(unit)
    _build_unit_type_shortcut(unit)
    for unit_prefix in _Unit.UnitPrefixMetaclass.prefix_iter():
        if unit_prefix.is_defined_in_spice:
            _build_unit_prefix_shortcut(unit, unit_prefix)

for unit in _Unit.UnitMetaclass.unit_iter():
    if unit.unit_suffix and unit.__class__ not in (_SiUnits.Kilogram,):
        # Fixme: kilogram
        _build_unit_shortcut(unit)

####################################################################################################

unit_value = _Unit.UnitValue.simple_value

Frequency = u_Hz
Period = u_s
