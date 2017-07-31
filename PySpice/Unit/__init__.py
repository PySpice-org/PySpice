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

"""This module implements units.

A shortcut is defined for each unit prefix, e.g. :class:`pico`, :class:`nano`, :class:`micro`,
:class:`milli`, :class:`kilo`, :class:`mega`, :class:`tera`.

A shortcut is defined for each unit and prefix as the concatenation of *u_*, an unit prefix and an
unit suffix, e.g. :class:`u_pV`, :class:`u_nV`, :class:`u_uV` :class:`u_mV`, :class:`u_V`,
:class:`u_kV`, :class:`u_MV`, :class:`u_TV`.

Some shortcuts have UTF-8 and ASCII variants:

* For micro, we have the prefix *μ* and *u*.
* For Ohm, we have :class:`u_Ω` and :class:`u_Ohm`.
* For Degree Celcius, we have :class:`u_°C` and :class:`u_Degree`.

"""

####################################################################################################

from . import Unit as _Unit
from . import SiUnits as _SiUnits

####################################################################################################

####################################################################################################

# Define shortcuts for unit prefixes : ..., micro, milli, kilo, mega, ...

def _build_prefix_shortcut(unit_prefix):
    unit_cls_name = unit_prefix.__class__.__name__
    cls_name = unit_cls_name.lower()
    unit_power = _Unit.UnitPower(power=unit_prefix)
    _Unit.UnitPower.register(unit_power)
    shortcut = lambda value: _Unit.UnitValue(unit_power, value)
    globals()[cls_name] = shortcut

for unit_prefix in _Unit.UnitPrefixMetaclass.prefix_iter():
    if unit_prefix.__class__ != _Unit.ZeroPower:
        _build_prefix_shortcut(unit_prefix) # capture unit_prefix

####################################################################################################

# Fixme: better ???

class FrequencyValue(_Unit.UnitValue, _Unit.FrequencyMixin):
    pass

class PeriodValue(_Unit.UnitValue, _Unit.PeriodMixin):
    pass

####################################################################################################

# Define unit shortcuts

def _exec_body(ns, unit_prefix):
    ns['__power__'] = unit_prefix

def _build_unit_prefix_shortcut(unit, unit_prefix):
    name = 'u_' + str(unit_prefix) + unit.unit_suffix
    if unit.__class__ == _SiUnits.Hertz:
        value_ctor = FrequencyValue
    elif unit.__class__ == _SiUnits.Second:
        value_ctor = PeriodValue
    else:
        value_ctor = _Unit.UnitValue
    unit_power = _Unit.UnitPower(unit, unit_prefix, value_ctor)
    _Unit.UnitPower.register(unit_power)
    shortcut = lambda value: value_ctor(unit_power, value)
    globals()[name] = shortcut
    ascii_name = name
    for args in (
            ('μ', 'u'),
            ('Ω', 'Ohm'),
            ('°C', 'Degree'), # ° is illegal ???
    ):
        ascii_name = ascii_name.replace(*args)
    if ascii_name != name:
        globals()[ascii_name] = shortcut

def _build_unit_shortcut(unit):
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
