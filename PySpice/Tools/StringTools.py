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

__all__ = [
    'join_dict',
    'join_lines'
    'join_list',
    'str_spice',
    'str_spice_list',
]

####################################################################################################

import os

####################################################################################################

from PySpice.Unit.Unit import UnitValue

####################################################################################################

def str_spice(obj, unit=True):

    # Fixme: right place ???

    """Convert an object to a Spice compatible string."""

    if isinstance(obj, UnitValue):
        if unit:
            return obj.str_spice()
        else: # Fixme: ok ???
            return obj.str(spice=False, space=False, unit=False)
    else:
        return str(obj)

####################################################################################################

def str_spice_list(*args):
    return [str_spice(x) for x in args]

####################################################################################################

def join_lines(items, prefix=''):
    return os.linesep.join([prefix + str(item)
                            for item in items
                            if item is not None]) # Fixme: and item

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

def join_dict(d):
    return ' '.join(["{}={}".format(key, str_spice(value))
                     for key, value in sorted(d.items())
                     if value is not None])
