####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
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
    'join_dict',
    'join_lines',
    'join_list',
    'str_spice',
    'str_spice_list',
    'prefix_lines',
    'TextBufer',
]

####################################################################################################

import os

####################################################################################################

from PySpice.Unit.Unit import UnitValue

####################################################################################################

def str_spice(obj, unit=True):
    # Fixme: right place ???
    '''Convert an object to a Spice compatible string.'''
    if isinstance(obj, UnitValue):
        if unit:
            return obj.str_spice()
        else:   # Fixme: ok ???
            return obj.str(spice=False, space=False, unit=False)
    else:
        return str(obj)

####################################################################################################

def str_spice_list(*args):
    return [str_spice(x) for x in args]

####################################################################################################

def prefix_lines(items, prefix=''):
    return [prefix + str(item)
            for item in items
            if item is not None] # Fixme: and item

####################################################################################################

def join_lines(items, prefix=''):
    return os.linesep.join(prefix_lines(items, prefix))

####################################################################################################

def join_list(items):
    # return ' '.join([str_spice(item)
    #                  for item in items
    #                  if item is not None and str_spice(item)])
    values = []
    for item in items:
        if item is not None:
            str_value = str_spice(item)
            if str_value:
                values.append(str_value)
    return ' '.join(values)

####################################################################################################

####################################################################################################
#
# Note:
#   PR #136 has non understood changes
#     https://github.com/FabriceSalvaire/PySpice/pull/136/files
#
####################################################################################################

def join_dict(d):
    # Fixme: remove trailing _ to key ???
    return ' '.join([f'{key}={str_spice(value)}'
                     for key, value in sorted(d.items())
                     if value is not None])

####################################################################################################

class TextBuffer:

    ##############################################

    def __init__(self):
        self._lines = []

    ##############################################

    def _append_line(self, line):
        if line is not None:
            _ = str(line)
            if _:
                self._lines.append(_)

    ##############################################

    def __iadd__(self, obj):
        if isinstance(obj, (list, tuple)):
            for _ in obj:
                self._append_line(_)
        else:
            self._append_line(obj)
        return self

    ##############################################

    def __str__(self):
        return os.linesep.join(self._lines)
