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

import types

from . import Unit as _Unit
from .Unit import Unit

####################################################################################################

# Import unit prefix shortcuts
for cls in _Unit.unit_prefix_classes.values():
    globals()[cls.__name__] = cls

####################################################################################################

# Define SI units

class Metre(_Unit.SiUnit):
    __unit_name__ = 'metre'
    __unit_suffix__ = 'm'
    __quantity__ = 'length'

class Kilogram(_Unit.SiUnit):
    __unit_name__ = 'kilogram'
    __unit_suffix__ = 'kg'
    __quantity__ = 'mass'

class Second(_Unit.SiUnit, _Unit.PeriodMixin):
    __unit_name__ = 'second'
    __unit_suffix__ = 's'
    __quantity__ = 'time'
    __is_si__ = True

# Alias
Period = Second

class Ampere(_Unit.SiUnit):
    __unit_name__ = 'ampere'
    __unit_suffix__ = 'A'
    __quantity__ = 'electric current'

class Kelvin(_Unit.SiUnit):
    __unit_name__ = 'kelvin'
    __unit_suffix__ = 'K'
    __quantity__ = 'thermodynamic temperature'

class Mole(_Unit.SiUnit):
    __unit_name__ = 'mole'
    __unit_suffix__ = 'mol'
    __quantity__ = 'amount of substance'

class Candela(_Unit.SiUnit):
    __unit_name__ = 'candela'
    __unit_suffix__ = 'cd'
    __quantity__ = 'luminosity intensity'

####################################################################################################

# Define Derived units

class Radian(Unit):
    __unit_name__ = 'radian'
    __unit_suffix__ = 'rad'
    __quantity__ = 'angle'
    __si_unit__ = 'm*m^-1'

class Steradian(Unit):
    __unit_name__ = 'steradian'
    __unit_suffix__ = 'sr'
    __quantity__ = 'solid angle'
    __si_unit__ = 'm^2*m^-2'

class Frequency(Unit, _Unit.FrequencyMixin):
    __unit_name__ = 'frequency'
    __unit_suffix__ = 'Hz'
    __quantity__ = 'frequency'
    __si_unit__ = 's^-1'
    __default_unit__ = True

class Newton(Unit):
    __unit_name__ = 'newton'
    __unit_suffix__ = 'N'
    __quantity__ = 'force'
    __si_unit__ = 'kg*m*s^-2'

class Pascal(Unit):
    __unit_name__ = 'pascal'
    __unit_suffix__ = 'Pa'
    __quantity__ = 'pressure'
    __si_unit__ = 'kg*m^-1*s^-2'
    # N/m^2

class Joule(Unit):
    __unit_name__ = 'joule'
    __unit_suffix__ = 'J'
    __quantity__ = 'energy'
    __si_unit__ = 'kg*m^2*s^-2'
    # N*m

class Watt(Unit):
    __unit_name__ = 'watt'
    __unit_suffix__ = 'W'
    __quantity__ = 'power'
    __si_unit__ = 'kg*m^2*s^-3'
    # J/s

class Coulomb(Unit):
    __unit_name__ = 'coulomb'
    __unit_suffix__ = 'C'
    __quantity__ = 'electric charge'
    __si_unit__ = 's*A'

class Volt(Unit):
    __unit_name__ = 'volt'
    __unit_suffix__ = 'V'
    __quantity__ = 'voltage'
    __si_unit__ = 'kg*m^2*s^-3*A^-1'
    # W/A

class Farad(Unit):
    __unit_name__ = 'farad'
    __unit_suffix__ = 'F'
    __quantity__ = 'capacitance'
    __si_unit__ = 'kg^-1*m^-2*s^4*A^2'
    # C/V

class Ohm(Unit):
    __unit_name__ = 'ohm'
    __unit_suffix__ = 'Ω'
    __quantity__ = 'electric resistance, impedance, reactance'
    __si_unit__ = 'kg*m^2*s^-3*A^-2'
    # V/A

class Siemens(Unit):
    __unit_name__ = 'siemens'
    __unit_suffix__ = 'S'
    __quantity__ = 'electrical conductance'
    __si_unit__ = 'kg^-1*m^-2*s^3*A^2'
    # A/V

class Weber(Unit):
    __unit_name__ = 'weber'
    __unit_suffix__ = 'Wb'
    __quantity__ = 'magnetic flux'
    __si_unit__ = 'kg*m^2*s^-2*A^-1'
    # V*s

class Tesla(Unit):
    __unit_name__ = 'tesla'
    __unit_suffix__ = ''
    __quantity__ = 'T'
    __si_unit__ = 'kg*s^-2*A^-1'
    # Wb/m2

class Henry(Unit):
    __unit_name__ = 'henry'
    __unit_suffix__ = 'H'
    __quantity__ = 'inductance'
    __si_unit__ = 'kg*m^2*s^-2*A^-2'
    # Wb/A

class DegreeCelcius(Unit):
    __unit_name__ = 'degree celcuis'
    __unit_suffix__ = '°C'
    __quantity__ = 'temperature relative to 273.15 K'
    __si_unit__ = 'K'

class Lumen(Unit):
    __unit_name__ = 'lumen'
    __unit_suffix__ = 'lm'
    __quantity__ = 'luminous flux'
    __si_unit__ = 'cd'
    # cd*sr

class Lux(Unit):
    __unit_name__ = 'lux'
    __unit_suffix__ = 'lx'
    __quantity__ = 'illuminance'
    __si_unit__ = 'm^-2*cd'
    # lm/m2

class Becquerel(Unit):
    __unit_name__ = 'becquerel'
    __unit_suffix__ = 'Bq'
    __quantity__ = 'radioactivity (decays per unit time)'
    __si_unit__ = 's^-1'

class Gray(Unit):
    __unit_name__ = 'gray'
    __unit_suffix__ = 'Gy'
    __quantity__ = 'absorbed dose (of ionizing radiation)'
    __si_unit__ = 'm^2*s^-2'
    # J/kg

class Sievert(Unit):
    __unit_name__ = 'sievert'
    __unit_suffix__ = 'Sv'
    __quantity__ = ' equivalent dose (of ionizing radiation)'
    __si_unit__ = 'm^2*s^-2'

class Katal(Unit):
    __unit_name__ = 'katal'
    __unit_suffix__ = 'kat'
    __quantity__ = 'catalytic activity'
    __si_unit__ = 'mol*s^-1'

####################################################################################################

# class Mil(Unit):
#     __scale__ = 25.4e-6 # mm
#     __spice_suffix__ = 'mil'

####################################################################################################

# Define unit shortcuts

def _exec_body(ns, unit_prefix):
    ns['__power__'] = unit_prefix

for unit in _Unit.UnitMetaclass.unit_iter():
    suffix = unit.__unit_suffix__
    if unit not in (Kilogram,) and suffix:
        # Fixme: kilogram
        for unit_prefix_cls in _Unit.UnitPrefixMetaclass.prefix_iter():
            unit_prefix = unit_prefix_cls() # Fixme: need instance
            prefix = unit_prefix.spice_prefix
            if prefix is not None:
                name = 'u_' + str(unit_prefix) + suffix
                # globals()[name] = lambda value: unit(value, power=unit_prefix)
                if unit_prefix_cls is not _Unit.ZeroPower:
                    cls = types.new_class(name, (unit,), exec_body=lambda ns: _exec_body(ns, unit_prefix))
                else:
                    cls = unit
                globals()[name] = cls
                ascii_name = name
                for args in (
                        ('μ', 'u'),
                        ('Ω', 'Ohm'),
                        ('°C', 'Degree'), # ° is illegal ???
                ):
                    ascii_name = ascii_name.replace(*args)
                if ascii_name != name:
                    globals()[ascii_name] = cls
