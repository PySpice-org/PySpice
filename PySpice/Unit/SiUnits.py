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
    __power__ = 24
    __prefix__ = 'Y'
    __spice_prefix__ = None

class Zetta(UnitPrefix):
    __power__ = 21
    __prefix__ = 'Z'
    __spice_prefix__ = None

class Exa(UnitPrefix):
    __power__ = 18
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

# Define SI units

class Metre(SiBaseUnit):
    __unit_name__ = 'metre'
    __unit_suffix__ = 'm'
    __quantity__ = 'length'

class Kilogram(SiBaseUnit):
    __unit_name__ = 'kilogram'
    __unit_suffix__ = 'kg'
    __quantity__ = 'mass'

class Second(SiBaseUnit):
    __unit_name__ = 'second'
    __unit_suffix__ = 's'
    __quantity__ = 'time'
    __is_si__ = True

class Ampere(SiBaseUnit):
    __unit_name__ = 'ampere'
    __unit_suffix__ = 'A'
    __quantity__ = 'electric current'

class Kelvin(SiBaseUnit):
    __unit_name__ = 'kelvin'
    __unit_suffix__ = 'K'
    __quantity__ = 'thermodynamic temperature'

class Mole(SiBaseUnit):
    __unit_name__ = 'mole'
    __unit_suffix__ = 'mol'
    __quantity__ = 'amount of substance'

class Candela(SiBaseUnit):
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
    __default_unit__ = True

class Steradian(Unit):
    __unit_name__ = 'steradian'
    __unit_suffix__ = 'sr'
    __quantity__ = 'solid angle'
    __si_unit__ = 'm^2*m^-2'
    __default_unit__ = True

class Hertz(Unit):
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
    __default_unit__ = True

class Pascal(Unit):
    __unit_name__ = 'pascal'
    __unit_suffix__ = 'Pa'
    __quantity__ = 'pressure'
    __si_unit__ = 'kg*m^-1*s^-2'
    __default_unit__ = True
    # N/m^2

class Joule(Unit):
    __unit_name__ = 'joule'
    __unit_suffix__ = 'J'
    __quantity__ = 'energy'
    __si_unit__ = 'kg*m^2*s^-2'
    __default_unit__ = True
    # N*m

class Watt(Unit):
    __unit_name__ = 'watt'
    __unit_suffix__ = 'W'
    __quantity__ = 'power'
    __si_unit__ = 'kg*m^2*s^-3'
    __default_unit__ = True
    # J/s

class Coulomb(Unit):
    __unit_name__ = 'coulomb'
    __unit_suffix__ = 'C'
    __quantity__ = 'electric charge'
    __si_unit__ = 's*A'
    __default_unit__ = True

class Volt(Unit):
    __unit_name__ = 'volt'
    __unit_suffix__ = 'V'
    __quantity__ = 'voltage'
    __si_unit__ = 'kg*m^2*s^-3*A^-1'
    __default_unit__ = True
    # W/A

class Farad(Unit):
    __unit_name__ = 'farad'
    __unit_suffix__ = 'F'
    __quantity__ = 'capacitance'
    __si_unit__ = 'kg^-1*m^-2*s^4*A^2'
    __default_unit__ = True
    # C/V

class Ohm(Unit):
    __unit_name__ = 'ohm'
    __unit_suffix__ = 'Ω'
    __quantity__ = 'electric resistance, impedance, reactance'
    __si_unit__ = 'kg*m^2*s^-3*A^-2'
    __default_unit__ = True
    # V/A

class Siemens(Unit):
    __unit_name__ = 'siemens'
    __unit_suffix__ = 'S'
    __quantity__ = 'electrical conductance'
    __si_unit__ = 'kg^-1*m^-2*s^3*A^2'
    __default_unit__ = True
    # A/V

class Weber(Unit):
    __unit_name__ = 'weber'
    __unit_suffix__ = 'Wb'
    __quantity__ = 'magnetic flux'
    __si_unit__ = 'kg*m^2*s^-2*A^-1'
    __default_unit__ = True
    # V*s

class Tesla(Unit):
    __unit_name__ = 'tesla'
    __unit_suffix__ = ''
    __quantity__ = 'T'
    __si_unit__ = 'kg*s^-2*A^-1'
    __default_unit__ = True
    # Wb/m2

class Henry(Unit):
    __unit_name__ = 'henry'
    __unit_suffix__ = 'H'
    __quantity__ = 'inductance'
    __si_unit__ = 'kg*m^2*s^-2*A^-2'
    __default_unit__ = True
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
    __default_unit__ = True
    # lm/m2

class Becquerel(Unit):
    __unit_name__ = 'becquerel'
    __unit_suffix__ = 'Bq'
    __quantity__ = 'radioactivity (decays per unit time)'
    __si_unit__ = 's^-1' # same as Hertz

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
    __default_unit__ = True

####################################################################################################

# class Mil(Unit):
#     __scale__ = 25.4e-6 # mm
#     __spice_suffix__ = 'mil'
