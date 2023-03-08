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
    POWER = 24
    PREFIX = 'Y'
    SPICE_PREFIX = None

class Zetta(UnitPrefix):
    POWER = 21
    PREFIX = 'Z'
    SPICE_PREFIX = None

class Exa(UnitPrefix):
    POWER = 18
    PREFIX = 'E'
    SPICE_PREFIX = None

class Peta(UnitPrefix):
    POWER = 15
    PREFIX = 'P'
    SPICE_PREFIX = None

class Tera(UnitPrefix):
    POWER = 12
    PREFIX = 'T'

class Giga(UnitPrefix):
    POWER = 9
    PREFIX = 'G'

class Mega(UnitPrefix):
    POWER = 6
    PREFIX = 'M'
    SPICE_PREFIX = 'meg'

class Kilo(UnitPrefix):
    POWER = 3
    PREFIX = 'k'

class Hecto(UnitPrefix):
    POWER = 2
    PREFIX = 'h'
    SPICE_PREFIX = None

class Deca(UnitPrefix):
    POWER = 1
    PREFIX = 'da'
    SPICE_PREFIX = None

class Milli(UnitPrefix):
    POWER = -3
    PREFIX = 'm'

class Micro(UnitPrefix):
    POWER = -6
    PREFIX = 'μ'
    SPICE_PREFIX = 'u'

class Nano(UnitPrefix):
    POWER = -9
    PREFIX = 'n'

class Pico(UnitPrefix):
    POWER = -12
    PREFIX = 'p'

class Femto(UnitPrefix):
    POWER = -15
    PREFIX = 'f'

class Atto(UnitPrefix):
    POWER = -18
    PREFIX = 'a'
    SPICE_PREFIX = None

class Zepto(UnitPrefix):
    POWER = -21
    PREFIX = 'z'
    SPICE_PREFIX = None

class Yocto(UnitPrefix):
    POWER = -24
    PREFIX = 'y'
    SPICE_PREFIX = None

# Fixme: ngspice defines mil

####################################################################################################

# Define SI units

class Meter(SiBaseUnit):
    UNIT_NAME = 'meter'
    UNIT_SUFFIX = 'm'
    SPICE_SUFFIX = ''
    QUANTITY = 'length'

class Kilogram(SiBaseUnit):
    UNIT_NAME = 'kilogram'
    UNIT_SUFFIX = 'kg'
    SPICE_SUFFIX = ''
    QUANTITY = 'mass'

class Second(SiBaseUnit):
    UNIT_NAME = 'second'
    UNIT_SUFFIX = 's'
    QUANTITY = 'time'
    IS_SI = True

class Ampere(SiBaseUnit):
    UNIT_NAME = 'ampere'
    UNIT_SUFFIX = 'A'
    SPICE_SUFFIX = 'a'
    QUANTITY = 'electric current'

class Kelvin(SiBaseUnit):
    UNIT_NAME = 'kelvin'
    UNIT_SUFFIX = 'K'
    SPICE_SUFFIX = ''
    QUANTITY = 'thermodynamic temperature'

class Mole(SiBaseUnit):
    UNIT_NAME = 'mol'
    UNIT_SUFFIX = 'mol'
    SPICE_SUFFIX = ''
    QUANTITY = 'amount of substance'

class Candela(SiBaseUnit):
    UNIT_NAME = 'candela'
    UNIT_SUFFIX = 'cd'
    QUANTITY = 'luminosity intensity'

####################################################################################################

# Define Derived units

class Radian(Unit):
    UNIT_NAME = 'radian'
    UNIT_SUFFIX = 'rad'
    QUANTITY = 'angle'
    SI_UNIT = 'm*m^-1'
    DEFAULT_UNIT = True

class Steradian(Unit):
    UNIT_NAME = 'steradian'
    UNIT_SUFFIX = 'sr'
    SPICE_SUFFIX = ''
    QUANTITY = 'solid angle'
    SI_UNIT = 'm^2*m^-2'
    DEFAULT_UNIT = True

class Hertz(Unit):
    UNIT_NAME = 'frequency'
    UNIT_SUFFIX = 'Hz'
    SPICE_SUFFIX = 'hz'
    QUANTITY = 'frequency'
    SI_UNIT = 's^-1'
    DEFAULT_UNIT = True

class Newton(Unit):
    UNIT_NAME = 'newton'
    UNIT_SUFFIX = 'N'
    SPICE_SUFFIX = ''
    QUANTITY = 'force'
    SI_UNIT = 'kg*m*s^-2'
    DEFAULT_UNIT = True

class Pascal(Unit):
    UNIT_NAME = 'pascal'
    UNIT_SUFFIX = 'Pa'
    SPICE_SUFFIX = ''
    QUANTITY = 'pressure'
    SI_UNIT = 'kg*m^-1*s^-2'
    DEFAULT_UNIT = True
    # N/m^2

class Joule(Unit):
    UNIT_NAME = 'joule'
    UNIT_SUFFIX = 'J'
    SPICE_SUFFIX = ''
    QUANTITY = 'energy'
    SI_UNIT = 'kg*m^2*s^-2'
    DEFAULT_UNIT = True
    # N*m

class Watt(Unit):
    UNIT_NAME = 'watt'
    UNIT_SUFFIX = 'W'
    SPICE_SUFFIX = 'w'
    QUANTITY = 'power'
    SI_UNIT = 'kg*m^2*s^-3'
    DEFAULT_UNIT = True
    # J/s

class Coulomb(Unit):
    UNIT_NAME = 'coulomb'
    UNIT_SUFFIX = 'c'
    SPICE_SUFFIX = ''
    QUANTITY = 'electric charge'
    SI_UNIT = 's*A'
    DEFAULT_UNIT = True

class Volt(Unit):
    UNIT_NAME = 'volt'
    UNIT_SUFFIX = 'V'
    SPICE_SUFFIX = 'v'
    QUANTITY = 'voltage'
    SI_UNIT = 'kg*m^2*s^-3*A^-1'
    DEFAULT_UNIT = True
    # W/A

class Farad(Unit):
    UNIT_NAME = 'farad'
    UNIT_SUFFIX = 'F'
    SPICE_SUFFIX = ''
    QUANTITY = 'capacitance'
    SI_UNIT = 'kg^-1*m^-2*s^4*A^2'
    DEFAULT_UNIT = True
    # C/V

class Ohm(Unit):
    UNIT_NAME = 'ohm'
    UNIT_SUFFIX = 'Ω'
    SPICE_SUFFIX = 'ohm'
    QUANTITY = 'electric resistance, impedance, reactance'
    SI_UNIT = 'kg*m^2*s^-3*A^-2'
    DEFAULT_UNIT = True
    # V/A

class Siemens(Unit):
    UNIT_NAME = 'siemens'
    UNIT_SUFFIX = 'S'
    SPICE_SUFFIX = ''
    QUANTITY = 'electrical conductance'
    SI_UNIT = 'kg^-1*m^-2*s^3*A^2'
    DEFAULT_UNIT = True
    # A/V

class Weber(Unit):
    UNIT_NAME = 'weber'
    UNIT_SUFFIX = 'wb'
    QUANTITY = 'magnetic flux'
    SI_UNIT = 'kg*m^2*s^-2*A^-1'
    DEFAULT_UNIT = True
    # V*s

class Tesla(Unit):
    UNIT_NAME = 'tesla'
    UNIT_SUFFIX = 'T'
    SPICE_SUFFIX = ''
    QUANTITY = 'T'
    SI_UNIT = 'kg*s^-2*A^-1'
    DEFAULT_UNIT = True
    # Wb/m2

class Henry(Unit):
    UNIT_NAME = 'henry'
    UNIT_SUFFIX = 'h'
    QUANTITY = 'inductance'
    SI_UNIT = 'kg*m^2*s^-2*A^-2'
    DEFAULT_UNIT = True
    # Wb/A

class DegreeCelsius(Unit):
    UNIT_NAME = 'degree celsius'
    UNIT_SUFFIX = '°C'
    SPICE_SUFFIX = 'c'
    QUANTITY = 'temperature relative to 273.15 K'
    SI_UNIT = 'K'

class Lumen(Unit):
    UNIT_NAME = 'lumen'
    UNIT_SUFFIX = 'lm'
    QUANTITY = 'luminous flux'
    SI_UNIT = 'cd'
    # cd*sr

class Lux(Unit):
    UNIT_NAME = 'lux'
    UNIT_SUFFIX = 'lx'
    QUANTITY = 'illuminance'
    SI_UNIT = 'm^-2*cd'
    DEFAULT_UNIT = True
    # lm/m2

class Becquerel(Unit):
    UNIT_NAME = 'becquerel'
    UNIT_SUFFIX = 'Bq'
    QUANTITY = 'radioactivity (decays per unit time)'
    SI_UNIT = 's^-1' # same as Hertz

class Gray(Unit):
    UNIT_NAME = 'gray'
    UNIT_SUFFIX = 'Gy'
    SPICE_SUFFIX = ''
    QUANTITY = 'absorbed dose (of ionizing radiation)'
    SI_UNIT = 'm^2*s^-2'
    # J/kg

class Sievert(Unit):
    UNIT_NAME = 'sievert'
    UNIT_SUFFIX = 'sv'
    SPICE_SUFFIX = ''
    QUANTITY = ' equivalent dose (of ionizing radiation)'
    SI_UNIT = 'm^2*s^-2'

class Katal(Unit):
    UNIT_NAME = 'katal'
    UNIT_SUFFIX = 'kat'
    SPICE_SUFFIX = ''
    QUANTITY = 'catalytic activity'
    SI_UNIT = 'mol*s^-1'
    DEFAULT_UNIT = True

####################################################################################################

# class Mil(Unit):
#     SCALE = 25.4e-6 # mm
#     SPICE_SUFFIX = 'mil'
