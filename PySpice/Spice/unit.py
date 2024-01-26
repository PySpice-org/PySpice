####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2024 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = [
    'str_spice',
    'str_spice_list',
]

####################################################################################################

import logging

####################################################################################################

from PySpice.Unit.Unit import UnitValue

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

SPICE_SUFFIX = {
    'Tera': 'T',
    'Giga': 'G',
    'Mega': 'Meg',
    'Kilo': 'K',
    'Mil': 'mil',
    'milli': 'm',
    'micro': 'u',
    'nano': 'n',
    'pico': 'p',
    'femto': 'f',
    'atto': 'a',
}
_ = {}
for name, suffix in SPICE_SUFFIX.items():
    if name[0].isupper():
        _[name.lower()] = suffix
SPICE_SUFFIX.update(_)

try:
    import pint

    @pint.register_unit_format('spice')
    def format_spice_unit(unit, registry, **options) -> str:
        # See Ngspice Manual — 2.1.4.2 Numbers
        # See https://pint.readthedocs.io/en/stable/user/formatting.html#string-formatting-specification
        # registry.parse_unit_name
        #   return tuple of tuples (str, str, str)
        #   all non-equivalent combinations of (prefix, unit name, suffix)
        unit_tuple = registry.parse_unit_name(str(unit), case_sensitive=False)
        prefix = unit_tuple[0][0]
        if prefix and prefix not in SPICE_SUFFIX:
            raise ValueError(f"unsupported Pint unit {unit}")
        _ = str(unit)
        # Fixme: useless ?
        if _.startswith('mega'):
            _ = 'Mega' + _[4:]
        return _
except ImportError:
    pint = None

####################################################################################################

def str_spice(obj, unit=True):
    # Fixme: right place ???
    '''Convert an object to a Spice compatible string.'''
    if isinstance(obj, UnitValue):
        if unit:
            return obj.str_spice()
        else:   # Fixme: ok ???
            return obj.str(spice=False, space=False, unit=False)
    elif pint and isinstance(obj, pint.Quantity):
        # _module_logger.info(f'Pint {obj} -> {obj:spice}')
        return f"{obj:spice}".replace(' ', '')
    else:
        return str(obj)

####################################################################################################

def str_spice_list(*args):
    return [str_spice(x) for x in args]
