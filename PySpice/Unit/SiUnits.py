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

####################################################################################################

"""This module defines SI prefixes and units.
"""

####################################################################################################

from .Unit import UnitPrefix, SiBaseUnit, Unit

####################################################################################################

# Define SI unit prefixes

class Yotta(UnitPrefix):
    _power_ = 24
    _prefix_ = 'Y'
    _spice_prefix_ = None

class Zetta(UnitPrefix):
    _power_ = 21
    _prefix_ = 'Z'
    _spice_prefix_ = None

class Exa(UnitPrefix):
    _power_ = 18
    _prefix_ = 'E'
    _spice_prefix_ = None

class Peta(UnitPrefix):
    _power_ = 15
    _prefix_ = 'P'
    _spice_prefix_ = None

class Tera(UnitPrefix):
    _power_ = 12
    _prefix_ = 'T'

class Giga(UnitPrefix):
    _power_ = 9
    _prefix_ = 'G'

class Mega(UnitPrefix):
    _power_ = 6
    _prefix_ = 'M'
    _spice_prefix_ = 'Meg'

class Kilo(UnitPrefix):
    _power_ = 3
    _prefix_ = 'k'

class Hecto(UnitPrefix):
    _power_ = 2
    _prefix_ = 'h'
    _spice_prefix_ = None

class Deca(UnitPrefix):
    _power_ = 1
    _prefix_ = 'da'
    _spice_prefix_ = None

class Milli(UnitPrefix):
    _power_ = -3
    _prefix_ = 'm'

class Micro(UnitPrefix):
    _power_ = -6
    _prefix_ = 'μ'
    _spice_prefix_ = 'u'

class Nano(UnitPrefix):
    _power_ = -9
    _prefix_ = 'n'

class Pico(UnitPrefix):
    _power_ = -12
    _prefix_ = 'p'

class Femto(UnitPrefix):
    _power_ = -15
    _prefix_ = 'f'
    _spice_prefix_ = None

class Atto(UnitPrefix):
    _power_ = -18
    _prefix_ = 'a'
    _spice_prefix_ = None

class Zepto(UnitPrefix):
    _power_ = -21
    _prefix_ = 'z'
    _spice_prefix_ = None

class Yocto(UnitPrefix):
    _power_ = -24
    _prefix_ = 'y'
    _spice_prefix_ = None

# Fixme: ngspice defines mil

####################################################################################################

# Define SI units

class Metre(SiBaseUnit):
    _unit_name_ = 'metre'
    _unit_suffix_ = 'm'
    _quantity_ = 'length'

class Kilogram(SiBaseUnit):
    _unit_name_ = 'kilogram'
    _unit_suffix_ = 'kg'
    _quantity_ = 'mass'

class Second(SiBaseUnit):
    _unit_name_ = 'second'
    _unit_suffix_ = 's'
    _quantity_ = 'time'
    __is_si__ = True

class Ampere(SiBaseUnit):
    _unit_name_ = 'ampere'
    _unit_suffix_ = 'A'
    _quantity_ = 'electric current'

class Kelvin(SiBaseUnit):
    _unit_name_ = 'kelvin'
    _unit_suffix_ = 'K'
    _quantity_ = 'thermodynamic temperature'

class Mole(SiBaseUnit):
    _unit_name_ = 'mole'
    _unit_suffix_ = 'mol'
    _quantity_ = 'amount of substance'

class Candela(SiBaseUnit):
    _unit_name_ = 'candela'
    _unit_suffix_ = 'cd'
    _quantity_ = 'luminosity intensity'

####################################################################################################

# Define Derived units

class Radian(Unit):
    _unit_name_ = 'radian'
    _unit_suffix_ = 'rad'
    _quantity_ = 'angle'
    _si_unit_ = 'm*m^-1'
    _default_unit_ = True

class Steradian(Unit):
    _unit_name_ = 'steradian'
    _unit_suffix_ = 'sr'
    _quantity_ = 'solid angle'
    _si_unit_ = 'm^2*m^-2'
    _default_unit_ = True

class Hertz(Unit):
    _unit_name_ = 'frequency'
    _unit_suffix_ = 'Hz'
    _quantity_ = 'frequency'
    _si_unit_ = 's^-1'
    _default_unit_ = True

class Newton(Unit):
    _unit_name_ = 'newton'
    _unit_suffix_ = 'N'
    _quantity_ = 'force'
    _si_unit_ = 'kg*m*s^-2'
    _default_unit_ = True

class Pascal(Unit):
    _unit_name_ = 'pascal'
    _unit_suffix_ = 'Pa'
    _quantity_ = 'pressure'
    _si_unit_ = 'kg*m^-1*s^-2'
    _default_unit_ = True
    # N/m^2

class Joule(Unit):
    _unit_name_ = 'joule'
    _unit_suffix_ = 'J'
    _quantity_ = 'energy'
    _si_unit_ = 'kg*m^2*s^-2'
    _default_unit_ = True
    # N*m

class Watt(Unit):
    _unit_name_ = 'watt'
    _unit_suffix_ = 'W'
    _quantity_ = 'power'
    _si_unit_ = 'kg*m^2*s^-3'
    _default_unit_ = True
    # J/s

class Coulomb(Unit):
    _unit_name_ = 'coulomb'
    _unit_suffix_ = 'C'
    _quantity_ = 'electric charge'
    _si_unit_ = 's*A'
    _default_unit_ = True

class Volt(Unit):
    _unit_name_ = 'volt'
    _unit_suffix_ = 'V'
    _quantity_ = 'voltage'
    _si_unit_ = 'kg*m^2*s^-3*A^-1'
    _default_unit_ = True
    # W/A

class Farad(Unit):
    _unit_name_ = 'farad'
    _unit_suffix_ = 'F'
    _quantity_ = 'capacitance'
    _si_unit_ = 'kg^-1*m^-2*s^4*A^2'
    _default_unit_ = True
    # C/V

class Ohm(Unit):
    _unit_name_ = 'ohm'
    _unit_suffix_ = 'Ω'
    _quantity_ = 'electric resistance, impedance, reactance'
    _si_unit_ = 'kg*m^2*s^-3*A^-2'
    _default_unit_ = True
    # V/A

class Siemens(Unit):
    _unit_name_ = 'siemens'
    _unit_suffix_ = 'S'
    _quantity_ = 'electrical conductance'
    _si_unit_ = 'kg^-1*m^-2*s^3*A^2'
    _default_unit_ = True
    # A/V

class Weber(Unit):
    _unit_name_ = 'weber'
    _unit_suffix_ = 'Wb'
    _quantity_ = 'magnetic flux'
    _si_unit_ = 'kg*m^2*s^-2*A^-1'
    _default_unit_ = True
    # V*s

class Tesla(Unit):
    _unit_name_ = 'tesla'
    _unit_suffix_ = ''
    _quantity_ = 'T'
    _si_unit_ = 'kg*s^-2*A^-1'
    _default_unit_ = True
    # Wb/m2

class Henry(Unit):
    _unit_name_ = 'henry'
    _unit_suffix_ = 'H'
    _quantity_ = 'inductance'
    _si_unit_ = 'kg*m^2*s^-2*A^-2'
    _default_unit_ = True
    # Wb/A

class DegreeCelcius(Unit):
    _unit_name_ = 'degree celcuis'
    _unit_suffix_ = '°C'
    _quantity_ = 'temperature relative to 273.15 K'
    _si_unit_ = 'K'

class Lumen(Unit):
    _unit_name_ = 'lumen'
    _unit_suffix_ = 'lm'
    _quantity_ = 'luminous flux'
    _si_unit_ = 'cd'
    # cd*sr

class Lux(Unit):
    _unit_name_ = 'lux'
    _unit_suffix_ = 'lx'
    _quantity_ = 'illuminance'
    _si_unit_ = 'm^-2*cd'
    _default_unit_ = True
    # lm/m2

class Becquerel(Unit):
    _unit_name_ = 'becquerel'
    _unit_suffix_ = 'Bq'
    _quantity_ = 'radioactivity (decays per unit time)'
    _si_unit_ = 's^-1' # same as Hertz

class Gray(Unit):
    _unit_name_ = 'gray'
    _unit_suffix_ = 'Gy'
    _quantity_ = 'absorbed dose (of ionizing radiation)'
    _si_unit_ = 'm^2*s^-2'
    # J/kg

class Sievert(Unit):
    _unit_name_ = 'sievert'
    _unit_suffix_ = 'Sv'
    _quantity_ = ' equivalent dose (of ionizing radiation)'
    _si_unit_ = 'm^2*s^-2'

class Katal(Unit):
    _unit_name_ = 'katal'
    _unit_suffix_ = 'kat'
    _quantity_ = 'catalytic activity'
    _si_unit_ = 'mol*s^-1'
    _default_unit_ = True

####################################################################################################

# class Mil(Unit):
#     __scale__ = 25.4e-6 # mm
#     __spice_suffix__ = 'mil'
